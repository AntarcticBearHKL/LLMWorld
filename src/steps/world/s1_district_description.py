"""World step: generate a district description from a custom prompt or a preset.

The caller supplies either free-form prompt text or one of the presets in
``src/prompts/district_presets.json`` (the ``clayton_3168`` preset embeds the
real Clayton 3168 census text). The chosen brief is wrapped by
``src/prompts/generate_world_district.md`` and sent to the model as a single
non-JSON call; the returned prose is written to ``<district>/description.md``
and merged into ``<district>/district.json`` (existing keys are kept).

Additive: the s1-s4 world steps and ``run.py`` are untouched, and the dashboard
can enumerate presets with ``--list-presets``.

Run:
  .venv\\Scripts\\python.exe src\\steps\\world\\s1_district_description.py --world <id> --preset clayton_3168
  .venv\\Scripts\\python.exe src\\steps\\world\\s1_district_description.py --list-presets
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from engine import SubAgent
from engine.subagent import LLMCallError
from engine.prompt import Prompt
import generate_world as gw

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PRESETS_PATH = os.path.join(PROJECT_ROOT, "src", "prompts", "district_presets.json")

HISTORY_STAGE = "district_description"


def load_presets() -> list[dict]:
    """Presets parsed from district_presets.json; [] when missing or malformed."""
    try:
        with open(PRESETS_PATH, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [p for p in data if isinstance(p, dict) and p.get("id") and p.get("prompt")]


def _find_preset(presets, preset_id):
    for preset in presets:
        if preset.get("id") == preset_id:
            return preset
    return None


def resolve_prompt(preset_id=None, prompt=None) -> tuple[str, str]:
    """Resolve the district brief text and its source.

    Precedence: an explicit ``prompt`` wins, then a matching ``preset_id``, then
    the first preset as the built-in default. Returns ``(text, source)`` where
    ``source`` is ``"custom"``, the resolved preset id, or ``"default"``.
    """
    if isinstance(prompt, str) and prompt.strip():
        return prompt, "custom"
    presets = load_presets()
    if preset_id:
        preset = _find_preset(presets, preset_id)
        if preset is not None:
            return preset["prompt"], str(preset.get("id"))
    if presets:
        return presets[0]["prompt"], "default"
    return "", "default"


def _read_district_meta(district_path):
    path = os.path.join(district_path, "district.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def run_step(world_id, district=None, *, preset=None, prompt=None, seed=42) -> tuple[bool, str]:
    """Generate one district description and persist it.

    Returns ``(True, description)`` on success and ``(False, error)`` otherwise.
    ``seed`` is accepted for CLI parity with the other world steps; this call is
    not sampled.
    """
    district = district or gw.primary_district(world_id)
    if not district:
        return False, f"no districts in world {world_id}"

    body, source = resolve_prompt(preset, prompt)
    district_path = gw.district_dir(world_id, district)
    os.makedirs(district_path, exist_ok=True)
    log_dir = os.path.join(district_path, "log")
    os.makedirs(log_dir, exist_ok=True)
    logger = gw.ChatLogger(log_dir)

    instruction = Prompt().load("generate_world_district", prompt=body)
    print("================ INPUT ================")
    print(instruction)
    try:
        resp = SubAgent.single_call(instruction)
    except LLMCallError as exc:
        print(f"[LLM failed] {exc}")
        logger.record(HISTORY_STAGE, instruction, "", reasoning="", ok=False,
                      error=str(exc), attempt=1, prefix="district_")
        return False, str(exc)

    print("================ OUTPUT ================")
    print(resp["content"])
    description = resp["content"].strip()
    if not description:
        logger.record(HISTORY_STAGE, instruction, "", reasoning="", ok=False,
                      error="empty description", attempt=1, prefix="district_")
        return False, "empty description"
    logger.record(HISTORY_STAGE, instruction, description, reasoning="", ok=True,
                  attempt=1, prefix="district_",
                  parsed={"description_source": source, "seed": seed})

    md_path = os.path.join(district_path, "description.md")
    with open(md_path, "w", encoding="utf-8") as file:
        file.write(description + "\n")
    print(f"[Saved] {md_path}")

    meta_path = os.path.join(district_path, "district.json")
    meta = _read_district_meta(district_path)
    meta["description"] = description
    meta["description_source"] = source
    meta["description_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(meta, file, ensure_ascii=False, indent=2)
        file.write("\n")
    print(f"[Saved] {meta_path} (source={source}, {len(description.split())} words)")
    return True, description


def main():
    parser = argparse.ArgumentParser(description="World step: district description (preset or custom prompt)")
    parser.add_argument("--world", default=None, help="world ID (required unless --list-presets)")
    parser.add_argument("--district", default=None, help="district name (default: world's primary district)")
    parser.add_argument("--preset", default=None, help="preset id from district_presets.json")
    parser.add_argument("--prompt", default=None, help="custom prompt text (wins over --preset)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--list-presets", action="store_true", help="list available presets and exit")
    args = parser.parse_args()

    if args.list_presets:
        for preset in load_presets():
            print(f"{preset.get('id')}\t{preset.get('title', '')}\t{preset.get('description', '')}")
        sys.exit(0)
    if not args.world:
        parser.error("--world is required")

    ok, result = run_step(args.world, args.district, preset=args.preset,
                          prompt=args.prompt, seed=args.seed)
    if ok:
        print(result)
    else:
        print(f"[Error] {result}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
