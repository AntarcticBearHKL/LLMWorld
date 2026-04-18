from Core import SubAgent, create_default_home, Planner, Executor, Recorder, Visualizer

home = create_default_home()

planner = Planner(home)

date = "2025年4月13日"
day_type = "周二（工作日）"

print("第一步：生成宏观计划...")
planner.generate_plans(date, day_type)

print("第一步完成：生成宏观计划可视化图表...")
visualizer = Visualizer(planner)
visualizer.visualize_macro_plans()

print("第二步：识别协调场景...")
planner.analyze_interactions()

max_iterations = 5
iteration = 0
while iteration < max_iterations:
    iteration += 1
    print(f"\n第三步（迭代{iteration}）：批量调整时间线...")
    planner.adjust_timelines()
    
    print(f"第四步（迭代{iteration}）：验证协调...")
    needs_readjust = planner.verify_coordinations()
    
    if not needs_readjust:
        print("协调验证通过，进入下一步")
        break
    else:
        print("发现新的协调问题，重新调整...")
        if iteration >= max_iterations:
            print(f"警告：已达到最大迭代次数{max_iterations}，强制退出")

print("\n第五步：保存最终计划...")
planner.save_final_plans()

print("第五步完成：生成最终计划可视化图表...")
visualizer.visualize_decomposed_plans()

print("第六步：分解时间段...")
planner.decompose_to_segments()

print("第七步：执行用电模拟...")
executor = Executor(home, planner)
executor.execute_all_segments(season="秋天", weather="晴天", temperature=20)

print("第八步：生成报告...")
recorder = Recorder(home, planner.log_dir)
recorder.save_report(date)
recorder.save_json(date)

print("\n" + "="*60)
print("Token 使用统计")
print("="*60)
miss, hit, output = SubAgent.get_tokens()
print(f"未命中缓存 Token: {miss}")
print(f"命中缓存 Token: {hit}")
print(f"输出 Token: {output}")
print(f"总计: {miss + hit + output}")
print("="*60)

print("完成！")
