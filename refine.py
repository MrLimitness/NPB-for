import os
import re
import glob
import subprocess
import argparse
from API import sys_question

def process_folder(base_dir, folder_name, prompt_template):
    source_folder = f'{base_dir}/NPB3.0-omp-C/{folder_name}/for_origin'
    refinement_folder = f'{base_dir}/NPB3.0-omp-C/{folder_name}/for_refinement'

    # 确保目标文件夹存在
    os.makedirs(refinement_folder, exist_ok=True)

    # 查找源文件夹中的所有 C 文件
    c_files = glob.glob(os.path.join(source_folder, "*.c"))

    for c_file_path in c_files:
        # 获取文件名
        c_file_name = os.path.basename(c_file_path)
        c_file_output = os.path.join(refinement_folder, c_file_name)
        
        if os.path.exists(c_file_output) and os.path.getsize(c_file_output) > 0:
            print(f"File {c_file_output} already exists, skipping...")
            continue

        # 读取 C 文件内容
        with open(c_file_path, 'r') as f:
            c_file_content = f.read()

        # 生成完整的 prompt
        full_prompt = f"Refine and optimize this for loop code:\n\n{c_file_content}"

        # 调用 API
        print(f"Processing {c_file_name} in {folder_name}...")
        api_response = sys_question(prompt_template, full_prompt)

        # 获取生成的 C 代码
        c_code_match = re.search(r'```c(.*?)```', api_response, re.DOTALL)
        if c_code_match:
            refined_c_code = c_code_match.group(1).strip()
            print(f"Generated refined code for {c_file_name}")
        else:
            print(f"Warning: No C code markers found in response for {c_file_name}")
            refined_c_code = c_file_content

        # 保存生成的 C 文件
        with open(c_file_output, 'w') as f:
            f.write(refined_c_code)
        print(f"Saved refined C file to {c_file_output}")

    print(f"Finished processing folder: {folder_name}")


def main():
    parser = argparse.ArgumentParser(description="Refine C files with generated C code from GPT")
    parser.add_argument(
        '--folder', 
        nargs='+', 
        default=['BT'],
        help='List of folder names to process (e.g., BT CG SP)'
    )
    args = parser.parse_args()

    # 设置基础目录和 prompt 文件路径
    base_dir = "D:\\New_NPB"
    prompt_file = f"{base_dir}/prompt/refine.txt"

    # 读取 prompt 模板
    with open(prompt_file, 'r') as f:
        prompt_template = f.read()

    # 遍历所有指定的文件夹名称
    for folder_name in args.folder:
        process_folder(base_dir, folder_name, prompt_template)

    print("All folders processed!")


if __name__ == "__main__":
    main()