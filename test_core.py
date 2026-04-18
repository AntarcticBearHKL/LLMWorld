from Engine import DeepSeekProvider
from Core import create_default_home, Planner, Executor, Recorder

llm = DeepSeekProvider(json_mode=True)

home = create_default_home()

planner = Planner(llm, home)

date = "2025年4月13日"
day_type = "周二（工作日）"

print("第一步：生成宏观计划...")
planner.generate_all_plans(date, day_type)

print("第二步：分析互动...")
planner.analyze_interactions()

print("第三步：分解时间段...")
planner.decompose_to_segments()

print("第四步：执行用电模拟...")
executor = Executor(llm, home, planner)
executor.execute_all_segments(season="秋天", weather="晴天", temperature=20)

print("第五步：生成报告...")
recorder = Recorder(home, planner.log_dir)
recorder.save_report(date)
recorder.save_json(date)

print("完成！")
