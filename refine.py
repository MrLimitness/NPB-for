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

    # 查找refinement文件夹中的所有 C 文件（这些是需要处理的目标文件）
    target_files = glob.glob(os.path.join(refinement_folder, "*.c"))
    
    if not target_files:
        print(f"No target files found in {refinement_folder}")
        return

    for target_file_path in target_files:
        # 获取文件名
        c_file_name = os.path.basename(target_file_path)
        
        # 检查目标文件是否已有内容（非空）
        if os.path.exists(target_file_path) and os.path.getsize(target_file_path) > 0:
            print(f"File {target_file_path} already has content, skipping...")
            continue

        # 对应的源文件路径
        source_file_path = os.path.join(source_folder, c_file_name)
        
        # 检查源文件是否存在
        if not os.path.exists(source_file_path):
            print(f"Warning: Source file {source_file_path} not found, skipping...")
            continue

        # 读取源文件内容
        with open(source_file_path, 'r', encoding='utf-8') as f:
            c_file_content = f.read()

        # 如果源文件为空，跳过
        if not c_file_content.strip():
            print(f"Source file {source_file_path} is empty, skipping...")
            continue

        # 生成完整的 prompt
        full_prompt = f"Refine and optimize this for loop code:\n\n{c_file_content}"

        # 调用 API
        print(f"Processing {c_file_name} in {folder_name}...")
        try:
            api_response = sys_question(prompt_template, full_prompt)
        except Exception as e:
            print(f"API call failed for {c_file_name}: {e}")
            continue

        # 获取生成的 C 代码
        c_code_match = re.search(r'```c(.*?)```', api_response, re.DOTALL)
        if c_code_match:
            refined_c_code = c_code_match.group(1).strip()
            print(f"Generated refined code for {c_file_name}")
        else:
            print(f"Warning: No C code markers found in response for {c_file_name}")
            # 如果没有找到代码块，使用原始代码
            refined_c_code = c_file_content

        # 保存生成的 C 文件
        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(refined_c_code)
        print(f"Saved refined C file to {target_file_path}")

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
    base_dir = os.environ.get('BASE_DIR', os.getcwd())
    prompt_file = f"{base_dir}/prompt/refine.txt"

    # 检查prompt文件是否存在
    if not os.path.exists(prompt_file):
        print(f"Error: Prompt file {prompt_file} not found")
        return

    # 读取 prompt 模板
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # 遍历所有指定的文件夹名称
    for folder_name in args.folder:
        print(f"\n=== Processing {folder_name} ===")
        process_folder(base_dir, folder_name, prompt_template)

    print("\nAll folders processed!")


if __name__ == "__main__":
    main()