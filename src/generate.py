from engine import EnvironmentGenerator
import json
import os
import random
import argparse
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import utils

USER_PROMPT = """
位于墨尔本的中产家庭，居住在clayton
"""

def generate_world_id():
    return str(random.randint(100, 999))

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  已保存: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="LLM 世界生成")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（可复现）")
    args = parser.parse_args()

    utils.set_seed(args.seed)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    worlds_dir = os.path.join(project_root, 'worlds')
    world_id = generate_world_id()
    
    print("="*60)
    print("世界生成系统")
    print("="*60)
    print(f"世界ID: {world_id}  随机种子: {args.seed}")
    
    user_prompt = USER_PROMPT.strip()
    
    if not user_prompt:
        print("错误：设定描述不能为空")
        return
    
    print(f"\n用户设定：")
    print(f"  {user_prompt}")
    
    generator = EnvironmentGenerator()
    
    print("\n" + "="*60)
    print("第一层：生成地区设定")
    print("="*60)
    district_info = generator.generate_district(user_prompt)
    print(f"\n地区设定生成完成：")
    print(f"  邮编: {district_info['postcode']}")
    print(f"  位置: {district_info['location']['city']} - {district_info['location']['district']}")
    print(f"  经济水平: {district_info['economic_level']}")
    
    postcode = district_info['postcode']
    district_dir = os.path.join(worlds_dir, world_id, postcode)
    save_json(os.path.join(district_dir, 'district.json'), district_info)
    
    print("\n" + "="*60)
    print("第二层：生成家庭类型分布")
    print("="*60)
    household_distribution = generator.generate_household_distribution(district_info)
    print(f"\n家庭类型分布生成完成：")
    print(f"  总家庭数: {household_distribution['total_households']}")
    print(f"  家庭类型:")
    for htype in household_distribution['household_types']:
        print(f"    - {htype['type']}: {htype['count']}户 ({htype['percentage']}%)")
    
    save_json(os.path.join(district_dir, 'household_distribution.json'), household_distribution)
    
    print("\n" + "="*60)
    print("第三层：生成具体家庭")
    print("="*60)
    
    num_households = int(input(f"\n请输入要生成的家庭数量（最多{household_distribution['total_households']}户）：").strip() or "1")
    num_households = min(num_households, household_distribution['total_households'])
    
    households = []
    for i in range(num_households):
        house_id = f"house_{i+1:04d}"
        print(f"\n生成家庭 {i+1}/{num_households} (ID: {house_id})...")
        
        household_type = random.choice(household_distribution['household_types'])
        
        household = generator.generate_household(district_info, household_type)
        
        house_dir = os.path.join(district_dir, house_id)
        save_json(os.path.join(house_dir, 'household.json'), household)
        
        households.append({
            'house_id': house_id,
            'type': household_type['type'],
            'members_count': len(household['members']),
            'rooms_count': len(household['home']['rooms'])
        })
        
        print(f"  家庭类型: {household_type['type']}")
        print(f"  成员数量: {len(household['members'])}")
        print(f"  房间数量: {len(household['home']['rooms'])}")
    
    world_meta = {
        'world_id': world_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_prompt': user_prompt,
        'district': {
            'postcode': postcode,
            'city': district_info['location']['city'],
            'district': district_info['location']['district'],
            'economic_level': district_info['economic_level']
        },
        'households': households
    }
    
    save_json(os.path.join(worlds_dir, world_id, 'world.json'), world_meta)
    
    print("\n" + "="*60)
    print("世界生成完成！")
    print("="*60)
    print(f"\n世界路径: worlds/{world_id}/")
    print(f"  地区: {postcode}")
    print(f"  家庭数: {len(households)}")
    
    print(f"\n请运行 'python src/simulate.py {world_id}' 开始模拟")

if __name__ == "__main__":
    main()
