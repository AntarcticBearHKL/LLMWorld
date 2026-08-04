from appliances import APPLIANCE_REGISTRY, get_supported_appliances, get_supported_appliances_text, get_all_appliance_schemas, get_appliance_schemas_text
import json
import os

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    output_lines = []
    
    output_lines.append("="*80)
    output_lines.append("当前支持的家电列表")
    output_lines.append("="*80)
    
    appliances = get_supported_appliances()
    
    output_lines.append(f"\n总共支持 {len(appliances)} 种家电：\n")
    
    for i, appliance in enumerate(appliances, 1):
        appliance_class = APPLIANCE_REGISTRY[appliance]
        output_lines.append(f"{i:2d}. {appliance:8s} - {appliance_class.__name__}")
    
    output_lines.append("\n" + "="*80)
    output_lines.append("用于LLM的文本格式：")
    output_lines.append("="*80)
    output_lines.append(get_supported_appliances_text())
    
    output_lines.append("\n" + "="*80)
    output_lines.append("家电配置Schema")
    output_lines.append("="*80)
    
    schemas = get_all_appliance_schemas()
    
    for appliance_type, schema in schemas.items():
        output_lines.append(f"\n{'='*80}")
        output_lines.append(f"【{schema['type']}】 - {schema['description']}")
        output_lines.append(f"{'='*80}")
        
        for field_name, field_info in schema['config_fields'].items():
            required_mark = " [必填]" if field_info.get('required') else ""
            default_info = f" (默认: {field_info.get('default')})" if 'default' in field_info else ""
            range_info = f" 范围: {field_info.get('range')}" if 'range' in field_info else ""
            example_info = f" 例如: {field_info.get('example')}" if 'example' in field_info else ""
            
            output_lines.append(f"  • {field_name} ({field_info['type']}){required_mark}{default_info}")
            output_lines.append(f"    {field_info['description']}{range_info}{example_info}")
    
    output_lines.append("\n" + "="*80)
    output_lines.append("用于LLM的简化格式：")
    output_lines.append("="*80)
    output_lines.append(get_appliance_schemas_text())
    
    output_lines.append("\n" + "="*80)
    output_lines.append("完整JSON Schema（可用于LLM）：")
    output_lines.append("="*80)
    output_lines.append(json.dumps(schemas, ensure_ascii=False, indent=2))
    
    output_lines.append("\n" + "="*80)
    output_lines.append("示例配置（用于LLM返回）：")
    output_lines.append("="*80)
    example = {
        "type": "电视",
        "brand": "索尼",
        "power": 150,
        "age": 2
    }
    output_lines.append(json.dumps(example, ensure_ascii=False, indent=2))
    output_lines.append("\n使用示例配置创建家电：")
    output_lines.append("create_appliance_from_config('电视', config, location='客厅')")
    
    output_text = "\n".join(output_lines)
    
    print(output_text)
    
    output_file = os.path.join(logs_dir, 'listapp.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"\n\n输出已保存到: {output_file}")

if __name__ == "__main__":
    main()
