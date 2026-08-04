import os
import glob
import pandas as pd
import requests
import json
from dotenv import load_dotenv
import concurrent.futures
import time
import threading

# Load API keys from .env
load_dotenv()
DEEPSEEK_APIKEY = os.getenv("DEEPSEEK_APIKEY")

# Paths
BASE_DIR = "C:/Users/antar/Desktop/LLMWorld/Data/2021_GCP_all_for_AUS_short-header"
METADATA_FILE = os.path.join(BASE_DIR, "Metadata/Metadata_2021_GCP_DataPack_R1_R2.xlsx")
POA_DIR = os.path.join(BASE_DIR, "2021 Census GCP All Geographies for AUS/POA/AUS")
OUTPUT_FILE = "C:/Users/antar/Desktop/LLMWorld/clayton_3168_census_overview.csv"

# Translation Cache Setup
cache_lock = threading.Lock()
CACHE_FILE = "C:/Users/antar/Desktop/LLMWorld/clayton_translation_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}", flush=True)
    return {}

def save_cache(cache_data):
    with cache_lock:
        try:
            latest_cache = {}
            if os.path.exists(CACHE_FILE):
                try:
                    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                        latest_cache = json.load(f)
                except Exception:
                    pass
            latest_cache.update(cache_data)
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(latest_cache, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving cache: {e}", flush=True)

def load_table_names():
    print("Loading table names from metadata spreadsheet...", flush=True)
    # Sheet 0 (index 0) contains Table Number and Table Name
    df_tables = pd.read_excel(METADATA_FILE, sheet_name=0)
    df_tables.columns = df_tables.iloc[7]
    df_tables = df_tables.iloc[8:].reset_index(drop=True)
    df_tables = df_tables.dropna(subset=['Table Number', 'Table Name'])
    
    table_names = {}
    for _, row in df_tables.iterrows():
        t_num = str(row['Table Number']).strip()
        t_name = str(row['Table Name']).strip()
        table_names[t_num] = t_name
    return table_names

def load_metadata(table_names):
    print("Loading cell metadata descriptors...", flush=True)
    # Sheet 1: Cell Descriptors Information
    df_meta = pd.read_excel(METADATA_FILE, sheet_name=1)
    df_meta.columns = df_meta.iloc[9]
    df_meta = df_meta.iloc[10:].reset_index(drop=True)
    df_meta = df_meta.dropna(subset=['Short', 'Long', 'Columnheadingdescriptioninprofile', 'Profiletable'])
    
    mapping = {}
    for _, row in df_meta.iterrows():
        short_name = str(row['Short']).strip()
        long_name = str(row['Long']).strip()
        col_heading = str(row['Columnheadingdescriptioninprofile']).strip()
        table_id = str(row['Profiletable']).strip()
        
        # Profiletable might be G04A or G04B, but table number in Sheet 0 is G04
        base_table_id = table_id[:3] if len(table_id) >= 3 else table_id
        table_name = table_names.get(base_table_id, "Unknown Table")
        
        # Reconstruct row label from long_name and col_heading
        col_under = col_heading.replace(' ', '_')
        if long_name.endswith('_' + col_under):
            row_label = long_name[:-len(col_under)-1]
        elif long_name.endswith(col_under):
            row_label = long_name[:-len(col_under)]
        else:
            row_label = long_name
            
        row_label = row_label.replace('_', ' ').strip()
        
        # Build structured English text for LLM
        structured_text = f"Table: {table_id} ({table_name}) | Row: {row_label} | Column: {col_heading}"
        
        mapping[short_name] = {
            'text': structured_text,
            'table': table_id
        }
    return mapping

def translate_descriptions_llm(descriptions):
    cache = load_cache()
    
    # Filter descriptions to translate
    to_translate = [d for d in descriptions if d not in cache]
    
    if not to_translate:
        print("All descriptors are already in cache! Reusing cached translations.", flush=True)
        return cache
        
    if not DEEPSEEK_APIKEY or DEEPSEEK_APIKEY == "YOUR_API_KEY_HERE":
        print("Warning: No valid DEEPSEEK_APIKEY found in .env. Falling back to English descriptions.", flush=True)
        return cache
        
    print(f"Found {len(cache)} cached items. Translating remaining {len(to_translate)} unique descriptors using DeepSeek API in parallel...", flush=True)
    
    desc_list = list(to_translate)
    chunk_size = 30
    batches = []
    
    for i in range(0, len(desc_list), chunk_size):
        chunk = desc_list[i:i+chunk_size]
        batch_dict = {str(idx): text for idx, text in enumerate(chunk)}
        batches.append((batch_dict, chunk))
        
    translations = dict(cache)
    
    def worker(batch_idx, batch_dict, chunk):
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_APIKEY}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            "你是一个极其老练、极其耐心的澳大利亚人口普查数据分析师。\n"
            "请将以下普查指标的表-行-列（Table-Row-Column）结构化描述，转换为【超级通俗易懂、口语化、接地气的中文解释】。\n"
            "你的解释必须要做到让“大街上随便找一个什么都不知道的普通人/傻子都能一听就懂”的程度。\n"
            "【核心解释要求】：\n"
            "1. 绝不简单直接翻译！绝对不要写类似于“女性20-24岁”这样冷冰冰的直接翻译。\n"
            "   例如：Table: Age by Sex (G04) | Row: Age groups 0-4 years | Column: Males 应当解释为：\n"
            "   “在“按性别划分的年龄”普查表（G04）中，统计的是该地区（Clayton 3168）里年龄在0到4岁之间的男性婴幼儿人数。也就是该地区所有在这个年龄段的小男孩、男宝宝的总人数。”\n"
            "2. 必须把表（Table）、行（Row）和列（Column）的所有相关信息完美融会贯通到解释中，写出该数据项真实的物理含义。不要怕啰嗦、不怕信息重复，写的越详细、口语化、越清晰越好。\n"
            "3. 如果涉及中位数（Median）或平均数（Average），必须通俗解释其统计学含义（比如：Median rent weekly 解释为：“租房住的家庭每周付的租金中间数。把 Clayton 所有租房家庭的周租金从小到大排，最中间那个数字就是中位数。这代表这里有一半人房租比这个高，另一半比这个低，反映了这里最普遍、最真实的周房租平均负担水平”）。\n"
            "4. 如果包含英文缩写，请全部在解释中完整展开，绝对不要保留任何英文简称，更不要在中文解释里留下拼音或英文首字母。\n"
            "5. 返回格式：必须只返回一个干净的 JSON 对象，Key 是输入的数字编号（如 \"0\"、\"1\" 等），Value 是你写出的超详细通俗中文解释。不要包含 markdown 格式、不要有反引号，不要写任何前言或多余说明。\n\n"
            f"待解释的指标列表：\n{json.dumps(batch_dict, ensure_ascii=False)}"
        )
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        for attempt in range(4):
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=45)
                if response.status_code == 200:
                    content = response.json()['choices'][0]['message']['content'].strip()
                    # Clean potential markdown wrapping
                    if content.startswith("```"):
                        content = content.split("\n", 1)[1]
                    if content.endswith("```"):
                        content = content.rsplit("\n", 1)[0]
                    if content.startswith("json"):
                        content = content.split("json", 1)[1].strip()
                    
                    chunk_trans = json.loads(content)
                    result = {}
                    for k, v in chunk_trans.items():
                        orig_text = batch_dict.get(k)
                        if orig_text:
                            result[orig_text] = v
                    
                    # Save batch translations to disk immediately
                    save_cache(result)
                    return result
                else:
                    print(f"API Error {response.status_code} on batch {batch_idx} (attempt {attempt+1}): {response.text}", flush=True)
            except Exception as e:
                print(f"Request failed on batch {batch_idx} (attempt {attempt+1}): {e}", flush=True)
            time.sleep(2 ** attempt)
        return {}
        
    print(f"Starting parallel translation of {len(batches)} batches using 25 workers...", flush=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        future_to_batch = {
            executor.submit(worker, idx, batch_dict, chunk): idx 
            for idx, (batch_dict, chunk) in enumerate(batches)
        }
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_idx = future_to_batch[future]
            try:
                data = future.result()
                translations.update(data)
                print(f"Completed batch {batch_idx + 1}/{len(batches)} ({len(data)} items translated)", flush=True)
            except Exception as e:
                print(f"Batch {batch_idx + 1} generated an exception: {e}", flush=True)
                
    return translations

def main():
    # Delete all previously generated Clayton CSV files
    print("Deleting old generated files...", flush=True)
    old_files = glob.glob("C:/Users/antar/Desktop/LLMWorld/clayton_3168_*.csv")
    for f in old_files:
        try:
            os.remove(f)
            print(f"Deleted old file: {f}", flush=True)
        except Exception as e:
            print(f"Failed to delete {f}: {e}", flush=True)

    table_names = load_table_names()
    metadata_map = load_metadata(table_names)
    csv_files = glob.glob(os.path.join(POA_DIR, "*.csv"))
    
    clayton_row = {}
    
    print(f"Scanning {len(csv_files)} CSV files in POA/AUS directory...", flush=True)
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        try:
            df_csv = pd.read_csv(file_path)
            # Find row for Clayton (POA3168)
            row = df_csv[df_csv.iloc[:, 0].astype(str) == "POA3168"]
            if not row.empty:
                # Extract columns
                for col in df_csv.columns:
                    if col == df_csv.columns[0]:
                        continue
                    clayton_row[col] = row[col].values[0]
        except Exception as e:
            print(f"Error reading {filename}: {e}", flush=True)
            
    print(f"Extracted {len(clayton_row)} data columns for Clayton (3168).", flush=True)
    
    # Collect unique English structured descriptions for columns we found
    unique_descriptions = set()
    col_to_desc = {}
    col_to_table = {}
    
    for col in clayton_row.keys():
        meta = metadata_map.get(col, {'text': f"Short Code: {col}", 'table': 'Unknown'})
        col_to_desc[col] = meta['text']
        col_to_table[col] = meta['table']
        unique_descriptions.add(meta['text'])
        
    # Translate unique structured texts
    translations = translate_descriptions_llm(unique_descriptions)
    
    # Define the 5 categories mapping
    CATEGORIES = {
        'demographics': {
            'tables': ['G01', 'G03', 'G04', 'G05', 'G06', 'G07', 'G27', 'G28', 'G29', 'G30', 'G31', 'G44', 'G45'],
            'filename': 'clayton_3168_demographics.csv',
            'title': '基本人口特征'
        },
        'economics': {
            'tables': ['G02', 'G17', 'G32', 'G33', 'G57', 'G58', 'G59'],
            'filename': 'clayton_3168_economics.csv',
            'title': '收入与经济水平'
        },
        'housing': {
            'tables': ['G34', 'G35', 'G36', 'G37', 'G38', 'G39', 'G40', 'G41', 'G42'],
            'filename': 'clayton_3168_housing.csv',
            'title': '住房性质与硬件'
        },
        'education_employment': {
            'tables': [
                'G15', 'G16', 'G43', 'G46', 'G47', 'G48', 'G49', 'G50', 
                'G51', 'G52', 'G53', 'G54', 'G55', 'G56', 'G60', 'G61', 'G62'
            ],
            'filename': 'clayton_3168_education_employment.csv',
            'title': '教育与就业作息'
        },
        'culture_habits': {
            'tables': [
                'G08', 'G09', 'G10', 'G11', 'G12', 'G13', 'G14', 'G18', 
                'G19', 'G20', 'G21', 'G22', 'G23', 'G24', 'G25', 'G26'
            ],
            'filename': 'clayton_3168_culture_habits.csv',
            'title': '文化与生活习惯'
        }
    }
    
    # Classify records
    categorized_data = {cat: [] for cat in CATEGORIES.keys()}
    uncategorized = []
    
    for col, val in clayton_row.items():
        structured_text = col_to_desc[col]
        table_src = col_to_table[col]
        zh_desc = translations.get(structured_text, structured_text)
        
        record = {
            'Column_Code': col,
            'Table_Source': table_src,
            'Chinese_Description': zh_desc,
            'Clayton_Value': val
        }
        
        # Get base table name (e.g. G04A -> G04) to match categories
        base_table = table_src[:3] if len(table_src) >= 3 else table_src
        
        assigned = False
        for cat, config in CATEGORIES.items():
            if base_table in config['tables']:
                categorized_data[cat].append(record)
                assigned = True
                break
                
        if not assigned:
            uncategorized.append(record)
            
    # Save the 5 split CSV files
    for cat, records_list in categorized_data.items():
        config = CATEGORIES[cat]
        file_path = os.path.join(os.path.dirname(OUTPUT_FILE), config['filename'])
        
        if records_list:
            df_cat = pd.DataFrame(records_list)
            df_cat.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved {config['title']} ({len(df_cat)} rows) to: {file_path}", flush=True)
        else:
            print(f"Warning: No data found for category {config['title']}", flush=True)
            
    # Save uncategorized fallback if any
    if uncategorized:
        fallback_path = os.path.join(os.path.dirname(OUTPUT_FILE), "clayton_3168_uncategorized.csv")
        df_fallback = pd.DataFrame(uncategorized)
        df_fallback.to_csv(fallback_path, index=False, encoding='utf-8-sig')
        print(f"Saved uncategorized data ({len(df_fallback)} rows) to: {fallback_path}", flush=True)
        
    print("Execution completed successfully.", flush=True)

if __name__ == "__main__":
    main()
