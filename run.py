from Core import create_default_home, World

home = create_default_home()

world = World(home, start_date="2025年4月13日", day_type="工作日")

num_days = 5

for day in range(num_days):
    print(f"\n{'#'*60}")
    print(f"第 {day + 1}/{num_days} 天")
    print(f"{'#'*60}")
    
    world.simulate_day(
        season="秋天",
        weather="晴天",
        temperature=20,
        verbose=True
    )
    
    if day < num_days - 1:
        world.next_day()

print(f"\n{'='*60}")
print(f"完成 {num_days} 天模拟")
print(f"{'='*60}")
world.print_summary()

print("\n完成！")
