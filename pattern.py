import os
import re
import glob
import subprocess
import argparse
from API import sys_question

def process_folder(base_dir, folder_name, prompt_template):
    npb_base_folder = f'{base_dir}/NPB3.0-omp-C'
    source_folder = f'{npb_base_folder}/{folder_name}/for_origin'
    baseline_folder = f'{npb_base_folder}/{folder_name}/for_pattern_baseline'

    # 确保目标文件夹存在
    os.makedirs(baseline_folder, exist_ok=True)

    # 查找源文件夹中的所有 C 文件
    c_files = glob.glob(os.path.join(source_folder, "*.c"))

    for c_file_path in c_files:
        # 获取文件名
        c_file_name = os.path.basename(c_file_path)
        c_file_output = os.path.join(baseline_folder, c_file_name)
        
        if os.path.exists(c_file_output) and os.path.getsize(c_file_output) > 0:
            print(f"File {c_file_output} already exists, skipping...")
            continue

        # 读取 C 文件内容
        with open(c_file_path, 'r') as f:
            c_file_content = f.read()

        # 生成完整的 prompt
        full_prompt = f"Apply OpenMP optimization to this for loop code:\n\n{c_file_content}"

        # 调用 API
        print(f"Processing {c_file_name} in {folder_name}...")
        api_response = sys_question(prompt_template, full_prompt)

        # 获取生成的 C 代码
        c_code_match = re.search(r'```c(.*?)```', api_response, re.DOTALL)
        if c_code_match:
            optimized_c_code = c_code_match.group(1).strip()
            print(f"Generated optimized code for {c_file_name}")
        else:
            print(f"Warning: No C code markers found in response for {c_file_name}")
            optimized_c_code = c_file_content

        # 保存生成的 C 文件
        with open(c_file_output, 'w') as f:
            f.write(optimized_c_code)
        print(f"Saved optimized C file to {c_file_output}")

    print(f"Finished processing folder: {folder_name}")


def main():
    parser = argparse.ArgumentParser(description="Pattern baseline generation")
    parser.add_argument(
        '--folder', 
        nargs='+', 
        default=['BT', "CG", "EP", "FT", "LU", "MG", "SP"],
        help='List of folder names to process (e.g., BT CG SP)'
    )
    args = parser.parse_args()

    base_dir = os.environ.get('BASE_DIR', os.getcwd())
    prompt_file = f"{base_dir}/prompt/0.txt"
    
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()

    # 遍历所有指定的文件夹名称
    for folder_name in args.folder:
        process_folder(base_dir, folder_name, prompt_template)

    print("All folders processed!")


if __name__ == "__main__":
    main()