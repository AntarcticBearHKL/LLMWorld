# 电器数据库使用说明

## 概述

电器数据库是一个可扩展的电器管理系统，通过文本名称识别电器，每种电器都有独立的类文件，可以自定义电量计算逻辑。

## 目录结构

```
ApplianceDatabase/
├── __init__.py              # 电器注册表和工厂函数
├── base_appliance.py        # 基础电器类
├── README.md                # 本文档
├── tv.py                    # 电视
├── ac.py                    # 空调
├── fridge.py                # 冰箱
├── phone.py                 # 手机
├── computer.py              # 电脑
├── ev.py                    # 电动汽车
└── ...                      # 其他电器
```

## 使用方法

### 1. 创建电器

```python
from appliance import create_appliance

# 通过名称创建电器
tv = create_appliance("电视", location="客厅")
phone = create_appliance("手机", owner="爸爸")
ac = create_appliance("空调", location="卧室1")
```

### 2. 在Room中添加电器

```python
living_room = Room("客厅")
living_room.add_appliance_by_name("电视")
living_room.add_appliance_by_name("空调")
```

### 3. 在Member中添加个人电器

```python
member = Member("爸爸", 45, "工程师", "勤劳", "节能意识中等")
member.add_personal_appliance_by_name("手机")
```

## 电器类型

### 1. OnDemandAppliance (按需使用电器)
- **描述**: 使用时才耗电的设备
- **可用操作**: `use`, `idle`
- **示例**: 电视、空调、灯、电脑

### 2. ChargingAppliance (充电设备)
- **描述**: 可以充电的设备
- **可用操作**: `charge_home`, `charge_external`, `use`, `idle`
- **示例**: 手机、电动汽车

### 3. AlwaysOnAppliance (持续运行设备)
- **描述**: 持续耗电的设备
- **可用操作**: 无（自动运行）
- **示例**: 冰箱

## 添加新电器

### 步骤1: 创建电器类文件

在 `ApplianceDatabase/` 目录下创建新文件，例如 `dishwasher.py`:

```python
from .base_appliance import OnDemandAppliance

class Dishwasher(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("洗碗机", power_watts=1500, location=location, owner=owner)
```

### 步骤2: 注册到电器表

在 `__init__.py` 中添加导入和注册:

```python
from .dishwasher import Dishwasher

APPLIANCE_REGISTRY = {
    # ... 其他电器
    "洗碗机": Dishwasher,
}
```

### 步骤3: 使用新电器

```python
kitchen.add_appliance_by_name("洗碗机")
```

## 自定义电量计算逻辑

### 方法1: 重写 `_calculate_energy_logic` 方法

```python
from .base_appliance import OnDemandAppliance

class SmartAC(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("智能空调", power_watts=2000, location=location, owner=owner)
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        # 自定义计算逻辑：根据温度调整功率
        temperature = kwargs.get('temperature', 25)
        
        if temperature > 30:
            # 高温时功率增加20%
            adjusted_power = self.power_watts * 1.2
        elif temperature < 15:
            # 低温时功率增加30%
            adjusted_power = self.power_watts * 1.3
        else:
            adjusted_power = self.power_watts
        
        return (adjusted_power / 1000.0) * duration_hours
```

### 方法2: 使用公式计算

```python
class VariableSpeedFan(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("变频风扇", power_watts=60, location=location, owner=owner)
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        # 根据档位计算功率
        speed_level = kwargs.get('speed_level', 2)  # 1-5档
        
        # 功率随档位线性增加
        actual_power = self.power_watts * (speed_level / 5.0)
        
        return (actual_power / 1000.0) * duration_hours
```

### 方法3: 调用AI模型（示例）

```python
from .base_appliance import OnDemandAppliance
# from some_ai_library import predict_energy

class AISmartAppliance(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("AI智能电器", power_watts=1000, location=location, owner=owner)
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        # 使用AI模型预测能耗
        usage_pattern = kwargs.get('usage_pattern', 'normal')
        weather = kwargs.get('weather', 'sunny')
        
        # 调用AI模型
        # predicted_energy = predict_energy(
        #     appliance_type=self.name,
        #     duration=duration_hours,
        #     pattern=usage_pattern,
        #     weather=weather
        # )
        
        # 这里使用简化的逻辑代替
        base_energy = (self.power_watts / 1000.0) * duration_hours
        
        if usage_pattern == 'intensive':
            return base_energy * 1.5
        elif usage_pattern == 'light':
            return base_energy * 0.7
        else:
            return base_energy
```

## 电器识别系统

### unique_id 生成规则

电器的 `unique_id` 由以下部分组成：
- **位置** (可选): `living`, `kitchen`, `bedroom1`, 等
- **拥有者** (可选): `dad`, `mom`, `son`, 等
- **电器名称**: `tv`, `phone`, `ac`, 等

示例：
- `living_tv` - 客厅的电视
- `mom_phone` - 妈妈的手机
- `bedroom1_ac` - 卧室1的空调
- `kitchen_fridge` - 厨房的冰箱

### 通过名称查找电器

```python
# 通过 unique_id 查找
appliance = home.get_appliance("living_tv")

# 通过房间和名称查找
appliance = home.get_appliance_by_room_and_name("客厅", "电视")
```

## 已注册电器列表

| 中文名称 | 类名 | 类型 | 默认功率(W) |
|---------|------|------|------------|
| 电视 | TV | on_demand | 150 |
| 空调 | AirConditioner | on_demand | 1800-2000 |
| 冰箱 | Fridge | always_on | 100 |
| 电饭煲 | RiceCooker | on_demand | 800 |
| 微波炉 | Microwave | on_demand | 1000 |
| 电磁炉 | InductionCooker | on_demand | 2000 |
| 油烟机 | Hood | on_demand | 200 |
| 灯 | Light | on_demand | 30-60 |
| 台灯 | Lamp | on_demand | 15 |
| 电脑 | Computer | on_demand | 200 |
| 手机 | Phone | charging | 20 |
| 电动汽车 | ElectricVehicle | charging | 7000 |
| 热水器 | WaterHeater | on_demand | 3000 |
| 洗衣机 | WashingMachine | on_demand | 500 |
| 吸尘器 | VacuumCleaner | on_demand | 1200 |

## 高级特性

### 1. 位置相关的功率调整

某些电器的功率会根据位置自动调整：

```python
class Light(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        power_map = {
            "客厅": 60,
            "厨房": 40,
            "卫生间": 30
        }
        power = power_map.get(location, 40)
        super().__init__("灯", power_watts=power, location=location, owner=owner)
```

### 2. 传递额外参数

在计算能耗时可以传递额外参数：

```python
energy = appliance.calculate_energy(
    start_minutes=480,
    end_minutes=540,
    power_source="home",
    temperature=28,
    speed_level=3,
    usage_pattern="intensive"
)
```

## 注意事项

1. **电器名称必须唯一**: 每个电器类型只能有一个中文名称
2. **继承正确的基类**: 根据电器特性选择合适的基类
3. **功率单位**: 使用瓦特(W)作为功率单位
4. **能耗单位**: 返回千瓦时(kWh)作为能耗单位
5. **默认计算**: 如果不重写 `_calculate_energy_logic`，使用默认的线性计算公式

## 示例：完整的自定义电器

```python
from .base_appliance import OnDemandAppliance

class SmartWaterHeater(OnDemandAppliance):
    def __init__(self, location=None, owner=None):
        super().__init__("智能热水器", power_watts=3000, location=location, owner=owner)
        self.water_temperature = 60  # 默认水温
    
    def _calculate_energy_logic(self, duration_hours, **kwargs):
        # 获取环境温度和目标水温
        ambient_temp = kwargs.get('temperature', 20)
        target_temp = kwargs.get('target_temp', self.water_temperature)
        
        # 温差越大，能耗越高
        temp_diff = target_temp - ambient_temp
        power_factor = 1.0 + (temp_diff - 40) * 0.02
        
        # 限制功率因子范围
        power_factor = max(0.5, min(power_factor, 2.0))
        
        adjusted_power = self.power_watts * power_factor
        return (adjusted_power / 1000.0) * duration_hours
    
    def set_temperature(self, temp):
        self.water_temperature = temp
```

使用：
```python
# 在 __init__.py 中注册
from .smart_water_heater import SmartWaterHeater
APPLIANCE_REGISTRY["智能热水器"] = SmartWaterHeater

# 使用
bathroom.add_appliance_by_name("智能热水器")
```
