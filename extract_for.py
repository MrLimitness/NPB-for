#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用于从C代码文件中提取for循环，并将每个循环保存为单独的C文件。
"""

import os
import re
import argparse


def clean_code(code):
    """清理代码，移除注释"""
    # 移除单行注释
    code = re.sub(r'//.*?\n', '\n', code)
    # 移除多行注释
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code


def find_matching_brace(text, start_pos):
    """找到与起始位置匹配的大括号"""
    brace_count = 0
    i = start_pos
    while i < len(text):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return i
        i += 1
    return -1


def extract_for_loop_at_position(text, start_pos):
    """从指定位置提取完整的for循环"""
    # 找到for关键字后的括号内容
    paren_start = text.find('(', start_pos)
    if paren_start == -1:
        return None

    # 找到匹配的右括号
    paren_count = 0
    paren_end = paren_start
    for i in range(paren_start, len(text)):
        if text[i] == '(':
            paren_count += 1
        elif text[i] == ')':
            paren_count -= 1
            if paren_count == 0:
                paren_end = i
                break

    # 跳过空白字符，找到循环体开始
    body_start = paren_end + 1
    while body_start < len(text) and text[body_start].isspace():
        body_start += 1

    if body_start >= len(text):
        return None

    # 如果是大括号，找到匹配的右大括号
    if text[body_start] == '{':
        body_end = find_matching_brace(text, body_start)
        if body_end == -1:
            return None
        return text[start_pos:body_end + 1].strip()
    else:
        # 单行循环体，找到分号或下一行
        body_end = body_start
        while body_end < len(text) and text[body_end] not in ';\n':
            body_end += 1
        if body_end < len(text) and text[body_end] == ';':
            body_end += 1
        return text[start_pos:body_end].strip()


def extract_for_loops_from_content(content):
    """
    从C代码内容中提取所有的for循环

    Args:
        content: C代码字符串

    Returns:
        list: 包含所有for循环的列表
    """
    # 清理代码
    content = clean_code(content)

    for_loops = []

    # 使用正则表达式找到所有for关键字的位置
    for_pattern = r'\bfor\s*\('
    matches = list(re.finditer(for_pattern, content))

    for match in matches:
        start_pos = match.start()

        # 向前查找，确保这是一个完整的for语句开始
        # 检查前面是否有其他字符（如变量名的一部分）
        if start_pos > 0:
            prev_char = content[start_pos - 1]
            if prev_char.isalnum() or prev_char == '_':
                continue

        loop_text = extract_for_loop_at_position(content, start_pos)
        if loop_text:
            # 检查是否已经被包含在一个更大的循环中
            is_nested = False
            for existing_loop in for_loops:
                if loop_text in existing_loop and loop_text != existing_loop:
                    is_nested = True
                    break

            # 如果不是嵌套的，或者是最外层的循环，添加到列表中
            if not is_nested:
                # 检查是否需要替换已存在的嵌套循环
                to_remove = []
                for i, existing_loop in enumerate(for_loops):
                    if (existing_loop in loop_text and
                            existing_loop != loop_text):
                        to_remove.append(i)

                # 移除被包含的小循环
                for i in reversed(to_remove):
                    for_loops.pop(i)

                for_loops.append(loop_text)

    return for_loops


def save_individual_loops(for_loops, source_file, target_folder):
    """
    将每个for循环保存为单独的C文件，并创建对应的空文件

    Args:
        for_loops: for循环列表
        source_file: 源文件路径
        target_folder: 目标文件夹路径（for_origin）
    """
    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 获取父目录用于创建其他文件夹
    parent_dir = os.path.dirname(target_folder)
    pattern_baseline_folder = os.path.join(parent_dir, "for_pattern_baseline")
    refinement_folder = os.path.join(parent_dir, "for_refinement")

    # 创建另外两个文件夹
    os.makedirs(pattern_baseline_folder, exist_ok=True)
    os.makedirs(refinement_folder, exist_ok=True)

    saved_count = 0

    for i, loop in enumerate(for_loops, 1):
        try:
            # 保存实际的for循环到for_origin文件夹
            file_content = loop
            target_file = os.path.join(target_folder, f"{i}.c")
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # 在for_pattern_baseline文件夹创建空文件
            baseline_file = os.path.join(pattern_baseline_folder, f"{i}.c")
            with open(baseline_file, 'w', encoding='utf-8') as f:
                f.write("")

            # 在for_refinement文件夹创建空文件
            refinement_file = os.path.join(refinement_folder, f"{i}.c")
            with open(refinement_file, 'w', encoding='utf-8') as f:
                f.write("")

            print(f"Loop {i} saved to {target_file}")
            print(f"  - Created baseline: {baseline_file}")
            print(f"  - Created refinement: {refinement_file}")
            saved_count += 1

        except Exception as e:
            print(f"Error saving loop {i}: {e}")

    return saved_count


def process_single_file(source_file, base_output_dir="for_origin"):
    """
    处理单个C文件，提取for循环并保存为单独的C文件

    Args:
        source_file: 源C文件路径
        base_output_dir: 基础输出目录名

    Returns:
        int: 成功保存的循环数量
    """
    print(f"Processing file: {source_file}")

    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"Error: Source file not found: {source_file}")
        return 0

    try:
        # 读取源文件内容
        with open(source_file, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading source file: {e}")
        return 0

    # 提取for循环
    for_loops = extract_for_loops_from_content(content)

    if not for_loops:
        print("No for loops found in the source file.")
        return 0

    print(f"Found {len(for_loops)} for loops")

    # 生成目标文件夹路径
    source_dir = os.path.dirname(source_file)
    target_folder = os.path.join(source_dir, base_output_dir)

    # 保存每个循环为单独的文件
    saved_count = save_individual_loops(for_loops, source_file, target_folder)

    print(f"Successfully saved {saved_count} out of {len(for_loops)} "
          f"loops to {target_folder}")

    return saved_count


def process_all_npb_files(base_output_dir="for_origin"):
    """
    处理所有NPB基准程序的C文件

    Args:
        base_output_dir: 基础输出目录名

    Returns:
        dict: 处理结果统计
    """
    base_dir = os.environ.get('BASE_DIR', os.getcwd())
    npb_files = [
        os.path.join(base_dir, "NPB3.0-omp-C", "BT", "bt_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "CG", "cg_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "EP", "ep_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "FT", "ft_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "LU", "lu_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "MG", "mg_#_omp.c"),
        os.path.join(base_dir, "NPB3.0-omp-C", "SP", "sp_#_omp.c")
    ]

    results = {}
    total_files = 0
    total_loops = 0

    print("Processing all NPB benchmark files...")
    print("=" * 50)

    for file_path in npb_files:
        if os.path.exists(file_path):
            saved_count = process_single_file(file_path, base_output_dir)
            benchmark_name = os.path.basename(os.path.dirname(file_path))
            results[benchmark_name] = saved_count
            total_files += 1
            total_loops += saved_count
            print("-" * 30)
        else:
            print(f"File not found: {file_path}")
            benchmark_name = os.path.basename(os.path.dirname(file_path))
            results[benchmark_name] = 0

    # 生成总结报告
    create_extraction_summary(results, base_output_dir,
                             total_files, total_loops)

    return results


def create_extraction_summary(results, output_dir, total_files, total_loops):
    """
    创建提取总结报告

    Args:
        results: 处理结果字典
        output_dir: 输出目录
        total_files: 处理的文件总数
        total_loops: 提取的循环总数
    """
    summary_file = os.path.join(output_dir, "extraction_summary.txt")

    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("NPB For Loop Extraction Summary\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Total files processed: {total_files}\n")
            f.write(f"Total loops extracted: {total_loops}\n\n")

            f.write("Individual Results:\n")
            f.write("-" * 30 + "\n")

            for benchmark, count in results.items():
                f.write(f"{benchmark}: {count} loops\n")

            f.write(f"\nAll loops saved to: {output_dir}/\n")
            f.write("Each benchmark has its own subdirectory with "
                   "numbered C files (1.c, 2.c, etc.)\n")

        print(f"Extraction summary saved to: {summary_file}")

    except Exception as e:
        print(f"Error creating summary report: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Extract individual for loops from C files and "
                   "save as separate C files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python extra_for.py --file "D:\\New_NPB\\NPB3.0-omp-C\\CG\\cg_#_omp.c"

  # Process all NPB files (default)
  python extra_for.py --all

  # Process all NPB files with custom output directory
  python extra_for.py --all --output my_loops
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Process a single C file'
    )

    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Process all NPB benchmark files'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='for_origin',
        help='Output directory name (default: for_origin)'
    )

    args = parser.parse_args()

    print("For Loop Extraction Tool")
    print("=" * 40)

    if args.file:
        # 处理单个文件
        saved_count = process_single_file(args.file, args.output)
        print(f"\\nProcessing completed! Extracted {saved_count} loops.")

    elif args.all:
        # 处理所有NPB文件
        results = process_all_npb_files(args.output)
        total_loops = sum(results.values())
        print("\\nProcessing completed!")
        print(f"Processed {len(results)} benchmark files")
        print(f"Total loops extracted: {total_loops}")

    else:
        # 默认行为：交互式选择
        print("Choose operation mode:")
        print("1. Process single file")
        print("2. Process all NPB files")

        choice = input("Enter your choice (1/2): ").strip()

        if choice == "1":
            file_path = input("Enter C file path: ").strip()
            if file_path and os.path.exists(file_path):
                saved_count = process_single_file(file_path, args.output)
                print(f"\\nProcessing completed! "
                      f"Extracted {saved_count} loops.")
            else:
                print("Invalid file path or file does not exist")

        elif choice == "2":
            results = process_all_npb_files(args.output)
            total_loops = sum(results.values())
            print("\\nProcessing completed!")
            print(f"Processed {len(results)} benchmark files")
            print(f"Total loops extracted: {total_loops}")

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
