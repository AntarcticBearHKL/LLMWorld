"""Shared household schema and persona-grounded personality helpers.

``HOUSEHOLD_SCHEMA`` is the canonical shape of a generated household
(``home`` + ``members``). It is the single definition the home step reuses when
it builds its strict request schema, so the two can never drift.

The personality helpers map a sampled persona row (or the aligned portrait as a
fallback) onto each member's ``energy_awareness`` + ``big_five`` fields. They
were the durable, pure part of the retired ``s3_household_build`` step and live
here so ``s2_household_compose`` and ``s3_home`` share one definition.
"""

import re

HOUSEHOLD_SCHEMA = {
    "type": "object",
    "required": ["home", "members"],
    "properties": {
        "type": {"type": "string"},
        "season": {"type": "string"},
        "story": {"type": "string"},
        "home": {
            "type": "object",
            "required": ["name", "rooms"],
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "size": {"type": "integer"},
                "rooms": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "appliances"],
                        "properties": {
                            "name": {"type": "string"},
                            "size": {"type": "integer"},
                            "appliances": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["type", "brand", "power", "age"],
                                    "properties": {
                                        "type": {"type": "string"},
                                        "brand": {"type": "string"},
                                        "power": {"type": "integer"},
                                        "age": {"type": "integer"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        "members": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source_persona_index", "name", "age", "cultural_background", "bedroom"],
                "properties": {
                    "source_persona_index": {"type": "integer"},
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "cultural_background": {"type": "string"},
                    "bedroom": {"type": "string"},
                    "gender": {"type": "string"},
                    "occupation": {"type": "string"},
                    "work_schedule": {"type": "object"},
                    "personality": {
                        "type": "object",
                        "properties": {
                            "energy_awareness": {"type": "string", "enum": ["Low", "Medium", "High"]},
                            "big_five": {
                                "type": "object",
                                "properties": {
                                    "openness": {"type": "number"},
                                    "conscientiousness": {"type": "number"},
                                    "extraversion": {"type": "number"},
                                    "agreeableness": {"type": "number"},
                                    "neuroticism": {"type": "number"},
                                },
                            },
                        },
                    },
                    "habits": {"type": "object"},
                    "health": {"type": "object"},
                    "personal_appliances": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {"type": "string"},
                                "brand": {"type": "string"},
                                "power": {"type": "number"},
                                "age": {"type": "number"},
                            },
                        },
                    },
                },
            },
        },
    },
}


def _normalize_appliance_entry(entry):
    if isinstance(entry, str):
        token = entry.strip()
        return {"type": token} if token else None
    if isinstance(entry, dict) and entry.get("type"):
        return entry
    return None


def _normalize_personal_appliances(members):
    for member in members:
        if not isinstance(member, dict):
            continue
        personal = member.get("personal_appliances")
        if isinstance(personal, list):
            member["personal_appliances"] = [
                norm for norm in (_normalize_appliance_entry(x) for x in personal) if norm
            ]
    return members


BIG_FIVE_DIMENSIONS = ("openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism")

# Raw persona-CSV columns carrying the Big Five dimensions read by the analysis scripts.
PERSONA_BIG_FIVE_COLUMNS = {
    "openness": "BFI-2 Open-Mindedness",
    "conscientiousness": "BFI-2 Conscientiousness",
    "extraversion": "BFI-2 Extraversion",
    "agreeableness": "BFI-2 Agreeableness",
    "neuroticism": "BFI-2 Negative Emotionality",
}

# Persona BFI-2 cells are 5-point labels; map them to floats in [0, 1].
BFI_LEVEL_SCORES = {
    "very low": 0.1,
    "low": 0.25,
    "slightly low": 0.35,
    "average": 0.5,
    "moderate": 0.5,
    "slightly high": 0.65,
    "high": 0.8,
    "very high": 0.9,
}

# Persona "Energy level" cell -> coarse energy_awareness bucket.
ENERGY_LEVEL_AWARENESS = {
    "very low": "Low",
    "low": "Low",
    "slightly low": "Low",
    "average": "Medium",
    "moderate": "Medium",
    "fair": "Medium",
    "slightly high": "Medium",
    "high": "High",
    "very high": "High",
    "excellent": "High",
}

# Energy-awareness label is a *construct* (attitude to energy + conscientiousness),
# not the wellness "Energy level" cell alone: in the persona bank the latter is
# almost always "Moderate", which collapses analyze_groups --label-source awareness
# into a single group (intervention_experiment_guide.md §3.4 groups high-awareness /
# high-conscientiousness households). Composite = mean of available components.
ATTITUDE_ENERGY_SCORES = {
    "opposed": 0.1,
    "very negative": 0.1,
    "negative": 0.25,
    "skeptical": 0.25,
    "neutral": 0.5,
    "positive": 0.8,
    "enthusiast": 0.9,
    "very positive": 0.9,
}
ENERGY_AWARENESS_LOW_BELOW = 0.4
ENERGY_AWARENESS_HIGH_AT = 0.65


def _score_attitude(value):
    if value is None:
        return None
    return ATTITUDE_ENERGY_SCORES.get(str(value).strip().lower())


def _row_energy_awareness(row):
    """Derive Low/Medium/High from the persona row's energy construct fields."""
    if not isinstance(row, dict):
        return None
    components = []
    for column in ("Attitude: Renewable energy", "Attitude: Climate action"):
        score = _score_attitude(row.get(column))
        if score is not None:
            components.append(score)
            break
    score = _level_to_score(row.get("BFI-2 Conscientiousness"))
    if score is not None:
        components.append(score)
    for column in ("Energy level", "BFI-2 Energy Level"):
        score = _level_to_score(row.get(column))
        if score is not None:
            components.append(score)
            break
    if not components:
        return None
    composite = sum(components) / len(components)
    if composite < ENERGY_AWARENESS_LOW_BELOW:
        return "Low"
    if composite < ENERGY_AWARENESS_HIGH_AT:
        return "Medium"
    return "High"

# Deterministic fallback for rows without BFI-2 columns: each marker hit shifts
# the 0.5 baseline by +-0.1, clamped to [0.1, 0.9]. Same portrait -> same score.
PORTRAIT_BIG_FIVE_MARKERS = {
    "openness": (
        ("curious", "creative", "imaginative", "artistic", "open-minded", "intellectual",
         "adventurous", "aesthetic", "philosophical", "exploratory"),
        ("conventional", "traditional", "routine", "practical", "predictable"),
    ),
    "conscientiousness": (
        ("organized", "organised", "disciplined", "orderly", "dutiful", "punctual",
         "planned", "structured", "thorough", "reliable"),
        ("spontaneous", "messy", "disorganized", "impulsive", "carefree", "last-minute"),
    ),
    "extraversion": (
        ("outgoing", "social", "extrovert", "talkative", "gregarious", "assertive",
         "energetic", "lively", "enthusiastic"),
        ("introvert", "quiet", "solitary", "reserved", "shy", "withdrawn", "reclusive"),
    ),
    "agreeableness": (
        ("kind", "compassionate", "cooperative", "warm", "trusting", "helpful",
         "friendly", "empathetic", "generous", "gentle"),
        ("competitive", "skeptical", "critical", "blunt", "argumentative", "selfish"),
    ),
    "neuroticism": (
        ("anxious", "worried", "stressed", "sensitive", "moody", "nervous", "tense", "insecure"),
        ("calm", "stable", "relaxed", "resilient", "composed", "even-tempered"),
    ),
}

PORTRAIT_ENERGY_MARKERS = (
    ("energetic", "high energy", "very active", "active", "vigorous", "lively"),
    ("tired", "fatigue", "exhausted", "low energy", "lethargic", "sluggish", "drained"),
)


def _marker_hits(text, markers):
    hits = 0
    for marker in markers:
        hits += len(re.findall(r"\b" + re.escape(marker) + r"\b", text))
    return hits


def _portrait_big_five(portrait):
    text = str(portrait or "").lower()
    scores = {}
    for dimension in BIG_FIVE_DIMENSIONS:
        positive, negative = PORTRAIT_BIG_FIVE_MARKERS[dimension]
        raw = 0.5 + 0.1 * (_marker_hits(text, positive) - _marker_hits(text, negative))
        scores[dimension] = round(min(0.9, max(0.1, raw)), 2)
    return scores


def _portrait_energy_awareness(portrait):
    text = str(portrait or "").lower()
    positive, negative = PORTRAIT_ENERGY_MARKERS
    high_hits = _marker_hits(text, positive)
    low_hits = _marker_hits(text, negative)
    if high_hits > low_hits:
        return "High"
    if low_hits > high_hits:
        return "Low"
    return "Medium"


def _level_to_score(value):
    if value is None:
        return None
    return BFI_LEVEL_SCORES.get(str(value).strip().lower())


def _level_to_awareness(value):
    if value is None:
        return None
    return ENERGY_LEVEL_AWARENESS.get(str(value).strip().lower())


def _apply_personality(member, row, portrait):
    """Attach energy_awareness + big_five, preferring the sampled persona row."""
    personality = member.get("personality")
    if not isinstance(personality, dict):
        personality = {}
    big_five = {}
    energy_awareness = None
    if isinstance(row, dict):
        for dimension, column in PERSONA_BIG_FIVE_COLUMNS.items():
            score = _level_to_score(row.get(column))
            if score is not None:
                big_five[dimension] = score
        energy_awareness = _row_energy_awareness(row)
    if len(big_five) < len(BIG_FIVE_DIMENSIONS) or energy_awareness is None:
        fallback = _portrait_big_five(portrait)
        for dimension in BIG_FIVE_DIMENSIONS:
            big_five.setdefault(dimension, fallback[dimension])
        if energy_awareness is None:
            energy_awareness = _portrait_energy_awareness(portrait)
    personality["energy_awareness"] = energy_awareness
    personality["big_five"] = {dimension: big_five[dimension] for dimension in BIG_FIVE_DIMENSIONS}
    member["personality"] = personality
    return member
