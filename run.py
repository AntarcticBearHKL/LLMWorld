from engine import Home, Room, Member, World

def create_default_home():
    home = Home("家庭")
    
    living_room = Room("客厅")
    living_room.add_appliance_by_name("电视")
    living_room.add_appliance_by_name("空调")
    living_room.add_appliance_by_name("吸尘器")
    living_room.add_appliance_by_name("灯")
    
    kitchen = Room("厨房")
    kitchen.add_appliance_by_name("冰箱")
    kitchen.add_appliance_by_name("电饭煲")
    kitchen.add_appliance_by_name("微波炉")
    kitchen.add_appliance_by_name("电磁炉")
    kitchen.add_appliance_by_name("油烟机")
    kitchen.add_appliance_by_name("灯")
    
    bedroom1 = Room("卧室1")
    bedroom1.add_appliance_by_name("空调")
    bedroom1.add_appliance_by_name("台灯")
    bedroom1.add_appliance_by_name("电脑")

    bedroom2 = Room("卧室2")
    bedroom2.add_appliance_by_name("空调")
    bedroom2.add_appliance_by_name("台灯")

    bedroom3 = Room("卧室3")
    bedroom3.add_appliance_by_name("空调")
    bedroom3.add_appliance_by_name("台灯")
    
    bathroom = Room("卫生间")
    bathroom.add_appliance_by_name("热水器")
    bathroom.add_appliance_by_name("洗衣机")
    bathroom.add_appliance_by_name("灯")

    garage = Room("车库")
    garage.add_appliance_by_name("电动汽车")
    
    home.add_room(living_room)
    home.add_room(kitchen)
    home.add_room(bedroom1)
    home.add_room(bedroom2)
    home.add_room(bedroom3)
    home.add_room(bathroom)
    home.add_room(garage)
    
    mem1 = Member("爸爸", 45, "工程师", "勤劳、负责", "节能意识中等")
    mem1.add_personal_appliance_by_name("手机")
    
    mem2 = Member("妈妈", 43, "教师", "勤劳、负责", "节能意识中等")
    mem2.add_personal_appliance_by_name("手机")
    
    home.add_member(mem1)
    home.add_member(mem2)
    
    return home

home = create_default_home()

world = World(home, start_date="2025年4月13日")

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
