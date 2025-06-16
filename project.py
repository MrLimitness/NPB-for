import os
import shutil
import subprocess
import re
from extract_for import extract_for_loops_from_content

base_dir = os.environ.get('BASE_DIR', os.getcwd())
NPB_dir = f"{base_dir}/NPB3.0-omp-C"


def init_NPB(bench):
    """
    NPB bench初始化
    
    Args:
        bench (str): NPB 基准测试名称，例如 "BT"
    """
    bench_lower = bench.lower()

    src_file = f"{NPB_dir}/{bench}/{bench_lower}_#_omp.c"
    dst_file = f"{NPB_dir}/{bench}/{bench_lower}.c"
    shutil.copy(src_file, dst_file)
    
    print(f"{bench} has been initialized")


def replace_NPB(bench, loop_file, folder):
    """
    替换 NPB 基准测试中的指定 for 循环
    
    Args:
        bench (str): NPB 基准测试名称，例如 "BT"
        loop_file (str): 循环文件名，例如 "1.c"
        folder (str): 循环所在的子目录，例如 "for_refinement" 或 "for_pattern_baseline"
    """
    bench_lower = bench.lower()
    
    # 提取循环序号
    try:
        loop_number = int(loop_file.split('.')[0])
    except (ValueError, IndexError):
        print(f"错误：无法从文件名 {loop_file} 提取循环序号")
        return False
    
    # 文件路径
    original_file = f"{NPB_dir}/{bench}/{bench_lower}_#_omp.c"
    optimized_file = f"{NPB_dir}/{bench}/{folder}/{loop_file}"
    target_file = f"{NPB_dir}/{bench}/{bench_lower}.c"
    
    # 检查文件是否存在
    if not os.path.exists(original_file):
        print(f"错误：原始文件不存在: {original_file}")
        return False
    
    if not os.path.exists(optimized_file):
        print(f"错误：优化文件不存在: {optimized_file}")
        return False
    
    if not os.path.exists(target_file):
        print(f"错误：目标文件不存在: {target_file}")
        return False
    
    try:
        # 读取原始文件内容
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 提取所有 for 循环
        for_loops = extract_for_loops_from_content(original_content)
        
        if loop_number > len(for_loops) or loop_number < 1:
            print(f"错误：循环序号 {loop_number} 超出范围 (1-{len(for_loops)})")
            return False
        
        # 获取要替换的原始循环（序号从1开始，索引从0开始）
        original_loop = for_loops[loop_number - 1]
        
        # 读取优化后的循环
        with open(optimized_file, 'r', encoding='utf-8') as f:
            optimized_loop = f.read().strip()
        
        # 如果优化文件为空，跳过替换
        if not optimized_loop:
            print(f"跳过：优化文件 {optimized_file} 为空")
            return False
        
        # 读取目标文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            target_content = f.read()
        
        # 执行替换
        if original_loop in target_content:
            updated_content = target_content.replace(original_loop, optimized_loop)
            
            # 写入更新后的内容
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"成功：已将循环 {loop_number} 从 {folder} 替换到 {bench_lower}.c 中")
            return True
        else:
            print(f"错误：在目标文件中找不到原始循环 {loop_number}")
            return False
            
    except Exception as e:
        print(f"替换过程中发生错误: {e}")
        return False


def replace_all(bench, folder):
    """
    替换指定文件夹中的所有循环
    
    Args:
        bench (str): NPB 基准测试名称，例如 "BT"
        folder (str): 循环所在的子目录，例如 "for_refinement" 或 "for_pattern_baseline"
    """
    folder_path = f"{NPB_dir}/{bench}/{folder}"
    
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在: {folder_path}")
        return
    
    # 获取所有.c文件
    loop_files = [f for f in os.listdir(folder_path) 
                  if f.endswith('.c') and os.path.isfile(os.path.join(folder_path, f))]
    
    if not loop_files:
        print(f"在 {folder_path} 中没有找到.c文件")
        return
    
    # 按数字排序
    try:
        loop_files.sort(key=lambda x: int(x.split('.')[0]))
    except ValueError:
        print("警告：某些文件名不是数字格式，使用字母顺序排序")
        loop_files.sort()
    
    success_count = 0
    total_count = len(loop_files)
    
    print(f"开始替换 {bench} 的 {total_count} 个循环...")
    
    for loop_file in loop_files:
        # 检查文件是否为空
        file_path = os.path.join(folder_path, loop_file)
        if os.path.getsize(file_path) == 0:
            print(f"跳过：文件 {loop_file} 为空")
            continue
            
        if replace_NPB(bench, loop_file, folder):
            success_count += 1
    
    print(f"替换完成：{success_count}/{total_count} 个循环替换成功")


def run_NPB(bench, CLASS):
    """
    执行 NPB , 返回结果正确性 & 执行时间
    
    Args:
        bench (str): NPB 基准测试名称，例如 "BT"
        CLASS (str): 数据大小，例如 "S", 从小到大可选"S" "W" "A" "B" "C" 
    """
    bench = bench.lower()
    # 构建 make 命令
    make_command = f"make {bench} CLASS={CLASS}"
    
    # 切换到 NPB 目录并执行 make 命令
    try:
        subprocess.run(make_command, shell=True, check=True, cwd=NPB_dir)
    except subprocess.CalledProcessError:
        return False, 9999  # make 失败，返回错误
    
    # 构建运行命令
    run_command = f"./bin/{bench}.{CLASS}"
    
    # 执行基准测试并获取输出
    try:
        result = subprocess.run(run_command, shell=True, check=True, cwd=NPB_dir, capture_output=True, text=True)
        output = result.stdout
    except subprocess.CalledProcessError:
        return False, 9999  # 运行失败，返回错误

    # 检查输出以确认结果
    verification_successful = re.search(r"Verification\s*=\s*SUCCESSFUL", output)
    time_match = re.search(r"Time in seconds\s*=\s*([\d.]+)", output)
    
    if verification_successful and time_match:
        time_taken = float(time_match.group(1))
        return True, time_taken  # 返回结果正确和执行时间
    else:
        return False, 9999  # 验证失败，返回错误


def clear_folder_contents(folder_path):
    """
    清空文件夹中所有文件的内容，但保留文件。
    """
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'w') as file:
                    file.truncate(0)  # 清空文件内容
        print(f"已清空文件夹 {folder_path} 中所有文件的内容")
    except FileNotFoundError:
        print(f"文件夹 {folder_path} 不存在")
    except IOError as e:
        print(f"操作文件夹 {folder_path} 时出错: {e}")


def clear_all():
    """
    清空所有文件夹中所有文件的内容，但保留文件。
    """
    folders = ["BT", "CG", "EP", "FT", "LU", "MG", "SP"]
    
    for folder in folders:
        folder_path1 = os.path.join(NPB_dir, folder, "for_pattern_baseline")
        folder_path2 = os.path.join(NPB_dir, folder, "for_refinement")
        if os.path.exists(folder_path1):
            clear_folder_contents(folder_path1)
        if os.path.exists(folder_path2):
            clear_folder_contents(folder_path2)


def main():
    # 示例用法
    bench = "CG"
    
    # 初始化
    init_NPB(bench)
    
    # 替换单个循环示例
    replace_NPB(bench, "1.c", "for_pattern_baseline")
    
    # 批量替换示例
    # replace_all(bench, "for_pattern_baseline")
    
    # 运行测试
    success, time_taken = run_NPB(bench, "S")
    
    if success:
        print(f"运行成功，执行时间: {time_taken} 秒")
    else:
        print("运行失败或验证不成功")


if __name__ == "__main__":
    main()