"""模拟世界可视化后端：常驻 HTTP 服务 + 命令行查询（前后端分离）。

启动（常驻服务，浏览器访问 http://localhost:8080）：
    python Implement/server.py [--port 8080]

命令行查询（同一后端逻辑，一次性输出）：
    python Implement/server.py --query worlds
    python Implement/server.py --query days pop02
    python Implement/server.py --query profile pop02 --scenario tou --date 2026-04-21
    python Implement/server.py --query matrix pop02
    python Implement/server.py --query events pop02

数据来源：outputs/（模拟产物）与 worlds/（世界配置/上帝剧本）。
零第三方依赖（标准库 http.server）。
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
WORLDS_DIR = os.path.join(PROJECT_ROOT, "worlds")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")


# ============================================================
# 数据读取层（API 与 CLI 共用）
# ============================================================

def list_worlds():
    """世界列表：worlds/ 下的目录 + outputs/ 下的"虚拟世界"（如多世界联合聚合）。"""
    worlds = []
    if not os.path.isdir(WORLDS_DIR):
        return worlds
    for name in sorted(os.listdir(WORLDS_DIR)):
        wdir = os.path.join(WORLDS_DIR, name)
        if not os.path.isdir(wdir):
            continue
        world = {"id": name, "households": [], "scenarios": [], "days": []}
        # 家庭构成（world.json 或 3168/house_*）
        meta_path = os.path.join(wdir, "world.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                world["households"] = meta.get("households", [])
                world["district"] = meta.get("district", {})
            except Exception:
                pass
        # 场景与日期（outputs/<world>/）
        world.update(scan_world(name))
        worlds.append(world)

    # 虚拟世界：outputs/ 下存在但 worlds/ 不存在的目录（combine_worlds 产物等）
    real_ids = {w["id"] for w in worlds}
    if os.path.isdir(OUTPUTS_DIR):
        for name in sorted(os.listdir(OUTPUTS_DIR)):
            if name in real_ids:
                continue
            out_world_dir = os.path.join(OUTPUTS_DIR, name)
            if not os.path.isdir(out_world_dir):
                continue
            if not os.path.isdir(os.path.join(out_world_dir, "population")):
                continue
            world = {"id": name, "households": [], "scenarios": [], "days": [],
                     "virtual": True}
            world.update(scan_world(name))
            if world["scenarios"]:
                worlds.append(world)
    return worlds


def scan_world(world_id):
    """扫描 outputs/<world_id>/ → {scenarios: [...], days: [...], per_house_dirs: [...]}"""
    result = {"scenarios": [], "days": []}
    out_dir = os.path.join(OUTPUTS_DIR, world_id, "population")
    if os.path.isdir(out_dir):
        for scenario in sorted(os.listdir(out_dir)):
            sdir = os.path.join(out_dir, scenario)
            if os.path.isdir(sdir):
                dates = sorted(d for d in os.listdir(sdir)
                               if os.path.isdir(os.path.join(sdir, d)))
                if dates:
                    result["scenarios"].append({
                        "name": scenario, "dates": dates,
                        "latest": dates[-1],
                    })
                result["days"].extend(f"{scenario}/{d}" for d in dates)
    return result


def load_profile(world_id, scenario, date):
    """读取某场景某日的聚合曲线。返回 dict 或 None。"""
    path = os.path.join(OUTPUTS_DIR, world_id, "population", scenario, date,
                        "population_profile_1440min.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_matrix(world_id):
    """场景对比矩阵（compare_policies 产物）。"""
    path = os.path.join(OUTPUTS_DIR, world_id, "comparison", "policy_matrix.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_analysis(world_id, scenario="baseline"):
    """人口归因分析（analyze_population 产物，计划25）。"""
    path = os.path.join(OUTPUTS_DIR, world_id, "analysis", f"population_{scenario}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_world_state(world_id):
    """世界连续状态（worlds/<id>/state.json，计划27）：上次日期+记忆天数。"""
    path = os.path.join(WORLDS_DIR, world_id, "state.json")
    if not os.path.exists(path):
        return {"has_state": False}
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    return {
        "has_state": True,
        "date": state.get("date"),
        "memory_days": len(state.get("memory_days", [])),
    }


def load_events(world_id):
    """上帝剧本（events.json）。"""
    path = os.path.join(WORLDS_DIR, world_id, "events.json")
    if not os.path.exists(path):
        return {"events": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def add_event_to_script(world_id, event):
    """上帝注入：把事件追加进 worlds/<id>/events.json（模拟中每天重读 → 实时生效）。"""
    path = os.path.join(WORLDS_DIR, world_id, "events.json")
    data = load_events(world_id)
    item = {
        "date": event["date"], "time": event.get("time", "07:00"),
        "title": event["title"], "content": event["content"],
        "source": event.get("source", "上帝"), "type": event.get("type", "一般"),
    }
    data.setdefault("events", []).append(item)
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def _dir_date(date_str):
    """日期目录兼容：'2026-04-21' 与 '20260421' 都接受（per-house 目录为紧凑格式）。"""
    return date_str.replace("-", "") if date_str else date_str


def load_house_profile(world_id, postcode, house_id, scenario, date):
    """单户 1440 分钟曲线。"""
    path = os.path.join(OUTPUTS_DIR, world_id, postcode, house_id, scenario,
                        _dir_date(date), "用电信息", "house_load_profile_1440min.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_house_summary(world_id, postcode, house_id, scenario, date):
    """单户电器级汇总（总用电汇总.json）。"""
    path = os.path.join(OUTPUTS_DIR, world_id, postcode, house_id, scenario,
                        _dir_date(date), "用电信息", "总用电汇总.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# HTTP 服务
# ============================================================

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def _send_file(self, path):
        if not os.path.exists(path):
            self._send_json({"error": "not found"}, 404)
            return
        with open(path, "rb") as f:
            body = f.read()
        ext = os.path.splitext(path)[1]
        ctype = {"html": "text/html; charset=utf-8", "js": "text/javascript",
                 "css": "text/css"}.get(ext.lstrip("."), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        parts = [p for p in path.split("/") if p]

        try:
            # 静态前端
            if not parts or parts[0] == "index.html":
                self._send_file(os.path.join(FRONTEND_DIR, "index.html"))
                return
            if parts[0].startswith("static"):
                self._send_file(os.path.join(FRONTEND_DIR, *parts[1:]))
                return

            # API
            if parts == ["api", "worlds"]:
                self._send_json(list_worlds())
                return
            if len(parts) >= 3 and parts[:2] == ["api", "worlds"]:
                world_id = parts[2]
                if len(parts) == 3:
                    world = next((w for w in list_worlds() if w["id"] == world_id), None)
                    self._send_json(world or {"error": "world not found"}, 200 if world else 404)
                    return
                if parts[3] == "profile" and len(parts) >= 5:
                    data = load_profile(world_id, parts[4], parts[5] if len(parts) > 5 else None)
                    self._send_json(data or {"error": "profile not found"}, 200 if data else 404)
                    return
                if parts[3] == "matrix":
                    data = load_matrix(world_id)
                    self._send_json(data or {"error": "no matrix"}, 200 if data else 404)
                    return
                if parts[3] == "analysis" and len(parts) >= 5:
                    data = load_analysis(world_id, parts[4])
                    self._send_json(data or {"error": "no analysis"}, 200 if data else 404)
                    return
                if parts[3] == "events":
                    self._send_json(load_events(world_id))
                    return
                if parts[3] == "state":
                    self._send_json(load_world_state(world_id))
                    return
                if parts[3] == "house" and len(parts) >= 6:
                    # /api/worlds/<id>/house/<house_id>/summary/<scenario>/<date>
                    house_id, sub, scenario, date = parts[4], parts[5], parts[6], parts[7]
                    postcode = None
                    world = next((w for w in list_worlds() if w["id"] == world_id), None)
                    district = (world or {}).get("district") or {}
                    postcode = district.get("postcode")
                    if not postcode:
                        self._send_json({"error": "unknown postcode"}, 404)
                        return
                    if sub == "summary":
                        data = load_house_summary(world_id, postcode, house_id, scenario, date)
                    else:
                        data = load_house_profile(world_id, postcode, house_id, scenario, date)
                    self._send_json(data or {"error": "house data not found"}, 200 if data else 404)
                    return
            if parts == ["api", "compare"]:
                self._send_json({"worlds": [w["id"] for w in list_worlds()]})
                return

            self._send_json({"error": f"unknown api: {path}"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        parts = [p for p in path.split("/") if p]
        try:
            if len(parts) == 4 and parts[:2] == ["api", "worlds"] and parts[3] == "events":
                world_id = parts[2]
                body = self._read_json_body()
                missing = [k for k in ("date", "title", "content") if not body.get(k)]
                if missing:
                    self._send_json({"error": f"缺少字段: {missing}"}, 400)
                    return
                events = add_event_to_script(world_id, body)
                self._send_json(events)
                return
            self._send_json({"error": f"unknown api: {path}"}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def log_message(self, format, *args):
        pass  # 静默访问日志，保持终端干净


def serve(port=8080):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"模拟世界可视化服务已启动：http://localhost:{port}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


# ============================================================
# 命令行查询
# ============================================================

def query_cli(args):
    if args.query == "worlds":
        for w in list_worlds():
            hh = len(w["households"])
            sc = ", ".join(s["name"] for s in w["scenarios"]) or "-"
            print(f"{w['id']}：{hh} 户 | 场景: {sc}")
        return

    if args.query == "days":
        for w in list_worlds():
            if w["id"] == args.world:
                for s in w["scenarios"]:
                    for d in s["dates"]:
                        print(f"{s['name']}/{d}")
                return
        print(f"世界 {args.world} 未找到")
        return

    if args.query == "profile":
        data = load_profile(args.world, args.scenario, args.date)
        if not data:
            print("未找到聚合曲线（检查场景/日期）")
            return
        print(f"[{args.world}/{args.scenario}/{args.date}]")
        print(f"  总用电 {data['total_energy_kwh']} kWh | 户均 {data['mean_household_kwh']} | "
              f"峰值 {data['peak_watts']} W @ {data['peak_time']}")
        for h in data["per_house"]:
            print(f"  {h['house_id']}: {h['total_energy_kwh']} kWh @ {h['peak_time']}")
        return

    if args.query == "matrix":
        m = load_matrix(args.world)
        if not m:
            print("无对比矩阵（先跑 compare_policies --all）")
            return
        for s in m["scenarios"]:
            print(" | ".join(str(s.get(k, "")) for k in s.keys()))
        return

    if args.query == "events":
        e = load_events(args.world)
        for item in e.get("events", []):
            print(f"[{item['date']} {item['time']}]（{item.get('source','')}）{item['title']}")
            print(f"  {item['content']}")
        return

    print(f"未知查询: {args.query}")


def parse_args():
    parser = argparse.ArgumentParser(description="模拟世界可视化后端")
    parser.add_argument("--port", type=int, default=8080, help="HTTP 端口")
    parser.add_argument("--query", default=None, help="命令行查询: worlds/days/profile/matrix/events")
    parser.add_argument("--world", default=None, help="查询用的世界ID")
    parser.add_argument("--scenario", default="baseline", help="查询用的场景")
    parser.add_argument("--date", default=None, help="查询用的日期(YYYY-MM-DD)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.query:
        query_cli(args)
    else:
        serve(args.port)
