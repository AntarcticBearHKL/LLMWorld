"""后台模拟任务管理器：模拟放后台跑，期间可继续开发，完成/报错后回来处理。

用法：
    python Implement/background_runner.py start pop02 --days 3 --policy tou --scenario foo
    python Implement/background_runner.py status
    python Implement/background_runner.py watch <job_id>     # 阻塞等待完成/失败
    python Implement/background_runner.py stop <job_id>

任务元数据与输出：logs/jobs/<job_id>.json / .out
进度从输出文件解析：'第 X/Y 天'、'Token 账单'、'[冒烟通过]'、'Traceback' 等。
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_DIR = os.path.join(PROJECT_ROOT, "logs", "jobs")
PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON):
    PYTHON = sys.executable   # 回退系统 python


def _job_path(job_id):
    return os.path.join(JOBS_DIR, f"{job_id}.json")


def _next_job_id():
    os.makedirs(JOBS_DIR, exist_ok=True)
    existing = [f[:-5] for f in os.listdir(JOBS_DIR) if f.endswith(".json")]
    n = 1
    while f"job_{n:03d}" in existing:
        n += 1
    return f"job_{n:03d}"


# ---------- 进度解析 ----------

PROGRESS_MARKERS = ["第 ", "Token 账单", "冒烟", "完成", "Traceback", "Error", "Failed"]


def _pids_of(out_path):
    """从日志路径反查任务 PID（从对应的 .json 元数据）。"""
    job_id = os.path.splitext(os.path.basename(out_path))[0]
    meta_path = _job_path(job_id)
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return [meta.get("pid")]
    return []


def _any_alive(pids):
    return any(_process_alive(p) for p in pids)


def tail_text(path, max_chars=800):
    """读日志尾部文本（供 server API 展示）。"""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return text[-max_chars:]
    except Exception:
        return ""


def parse_progress(out_path):
    """从输出文件提取任务进度摘要。"""
    if not os.path.exists(out_path):
        return {"status": "pending", "detail": "尚未启动"}
    try:
        with open(out_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return {"status": "unknown", "detail": "日志读取失败"}

    text = "".join(lines[-60:])   # 只看尾部（进度/错误都在尾部）

    # 状态判定（按优先级：失败 > 完成 > 运行中）
    done_markers = ["[冒烟通过]", "人口模拟完成", "离线聚合完成", "完成 N 天模拟", "完成！"]
    has_done = any(m in text for m in done_markers)
    if "Traceback" in text or "[冒烟失败]" in text or ("Error:" in text and not has_done):
        status = "failed"
    elif has_done:
        status = "done"
    else:
        status = "running"

    # 进程已死但无完成标记 → 异常终止（不能标 done）
    if status == "running" and not _any_alive(_pids_of(out_path)):
        status = "stopped"

    # 进度行：第 X/Y 天
    progress = None
    for line in reversed(lines):
        if "第" in line and "/" in line and "天" in line:
            import re
            m = re.search(r"第\s*(\d+)/(\d+)\s*天", line)
            if m:
                progress = f"{m.group(1)}/{m.group(2)} 天"
                break

    detail = progress or "初始化中…"
    return {"status": status, "detail": detail}


# ---------- 命令 ----------

def cmd_start(args):
    job_id = _next_job_id()
    os.makedirs(JOBS_DIR, exist_ok=True)
    out_path = os.path.join(JOBS_DIR, f"{job_id}.out")

    # 组装模拟命令：pop02 等世界参数直接透传
    # -X utf8：强制子进程 UTF-8 输出（Windows 默认 GBK 会乱码，导致进度解析失败）
    sim_cmd = [PYTHON, "-X", "utf8", "-u",
               os.path.join(PROJECT_ROOT, "Implement", "population_runner.py")]
    sim_cmd += args.sim_args

    with open(out_path, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(sim_cmd, stdout=f, stderr=subprocess.STDOUT,
                                cwd=PROJECT_ROOT, creationflags=subprocess.CREATE_NO_WINDOW)

    meta = {
        "job_id": job_id,
        "pid": proc.pid,
        "command": " ".join(sim_cmd),
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "out": out_path,
    }
    with open(_job_path(job_id), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"已启动后台任务 {job_id}（PID {proc.pid}）")
    print(f"  命令: {' '.join(sim_cmd)}")
    print(f"  日志: {out_path}")
    print(f"  查看进度: python Implement/background_runner.py status")
    print(f"  等待完成: python Implement/background_runner.py watch {job_id}")
    return job_id


def cmd_status(_args=None):
    if not os.path.isdir(JOBS_DIR):
        print("（无后台任务）")
        return
    jobs = sorted(f[:-5] for f in os.listdir(JOBS_DIR) if f.endswith(".json"))
    print(f"{'任务':<8}{'状态':<9}{'进度':<12}{'耗时':<8}命令")
    for jid in jobs:
        with open(_job_path(jid), "r", encoding="utf-8") as f:
            meta = json.load(f)
        prog = parse_progress(meta["out"])
        # 进程是否还活着
        alive = _process_alive(meta.get("pid"))
        if not alive and prog["status"] == "running":
            prog["status"] = "done" if prog["detail"] != "初始化中…" else "failed"
        elapsed = ""
        try:
            t0 = datetime.strptime(meta["started_at"], "%Y-%m-%d %H:%M:%S")
            elapsed = str(datetime.now() - t0).split(".")[0]
        except Exception:
            pass
        print(f"{jid:<8}{prog['status']:<9}{prog['detail']:<12}{elapsed:<8}{meta['command'][-60:]}")


def cmd_watch(args):
    if not os.path.exists(_job_path(args.job_id)):
        print(f"任务 {args.job_id} 不存在")
        sys.exit(1)
    with open(_job_path(args.job_id), "r", encoding="utf-8") as f:
        meta = json.load(f)
    print(f"等待任务 {args.job_id}…（Ctrl+C 停止等待，任务继续后台跑）")
    last_size = 0
    try:
        while True:
            prog = parse_progress(meta["out"])
            # 打印新增输出
            size = os.path.getsize(meta["out"]) if os.path.exists(meta["out"]) else 0
            if size > last_size:
                with open(meta["out"], "r", encoding="utf-8", errors="replace") as f:
                    f.seek(last_size)
                    chunk = f.read()
                if chunk.strip():
                    print(chunk, end="")
                last_size = size
            if not _process_alive(meta.get("pid")):
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[watch] 停止等待（任务仍在后台运行）")
        return
    final = parse_progress(meta["out"])
    print(f"\n[完成] 任务 {args.job_id} 最终状态: {final['status']}")
    return final


def cmd_stop(args):
    if not os.path.exists(_job_path(args.job_id)):
        print(f"任务 {args.job_id} 不存在")
        sys.exit(1)
    with open(_job_path(args.job_id), "r", encoding="utf-8") as f:
        meta = json.load(f)
    pid = meta.get("pid")
    if pid and _process_alive(pid):
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                       capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print(f"已终止任务 {args.job_id}（PID {pid}）")
    else:
        print(f"任务 {args.job_id} 已不在运行")


def _process_alive(pid):
    if not pid:
        return False
    try:
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return False
        exit_code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(h)
        return exit_code.value == 259   # STILL_ACTIVE
    except Exception:
        return False


# ---------- 服务器管理（系统级常驻，前后端修改后重启）----------

SERVER_PID_FILE = os.path.join(JOBS_DIR, "server.pid")
SERVER_LOG = os.path.join(JOBS_DIR, "server.out")
SERVER_DEFAULT_PORT = 8080


def _read_pid_file(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return None
    return None


def _write_pid_file(path, pid):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(pid))


def cmd_server(args):
    """server start|restart|stop|status [--port N]"""
    port = args.port or SERVER_DEFAULT_PORT
    pid = _read_pid_file(SERVER_PID_FILE)

    if args.action in ("restart", "start"):
        if pid and _process_alive(pid):
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"已停止旧服务器（PID {pid}）")
        cmd = [PYTHON, "-X", "utf8", "-u",
               os.path.join(PROJECT_ROOT, "Implement", "server.py"),
               "--port", str(port)]
        os.makedirs(JOBS_DIR, exist_ok=True)
        with open(SERVER_LOG, "w", encoding="utf-8") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT,
                                    cwd=PROJECT_ROOT,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
        _write_pid_file(SERVER_PID_FILE, proc.pid)
        print(f"服务器已启动（PID {proc.pid}）→ http://localhost:{port}")
        print(f"  日志: {SERVER_LOG}")
        print(f"  重启: python Implement/background_runner.py server restart")
        return

    if args.action == "stop":
        if pid and _process_alive(pid):
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"服务器已停止（PID {pid}）")
        else:
            print("服务器未在运行")
        return

    if args.action == "status":
        if pid and _process_alive(pid):
            print(f"服务器运行中（PID {pid}）→ http://localhost:{port}")
        else:
            print("服务器未运行（启动: python Implement/background_runner.py server start）")
        return


def parse_args():
    parser = argparse.ArgumentParser(description="后台任务管理器（模拟 + 服务器）")
    sub = parser.add_subparsers(dest="command", required=True)
    p_start = sub.add_parser("start", help="启动后台模拟")
    p_start.add_argument("sim_args", nargs=argparse.REMAINDER, help="模拟命令参数（世界ID等）")
    p_status = sub.add_parser("status", help="查看所有任务")
    p_watch = sub.add_parser("watch", help="等待任务完成")
    p_watch.add_argument("job_id")
    p_stop = sub.add_parser("stop", help="终止任务")
    p_stop.add_argument("job_id")
    p_server = sub.add_parser("server", help="可视化服务器管理（系统级常驻）")
    p_server.add_argument("action", choices=["start", "restart", "stop", "status"])
    p_server.add_argument("--port", type=int, default=SERVER_DEFAULT_PORT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "start":
        cmd_start(args)
    elif args.command == "status":
        cmd_status()
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "server":
        cmd_server(args)
