#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据依赖分析结果清理baseline和refinement文件夹
"""

import os
import shutil

def clean_folders():
    """根据循环分类清理文件夹"""
    
    # 从simple_loop_extractor.py中复制的分类数据
    需要重构的 = {
        "BT": [1, 4, 5, 7, 8, 10, 11, 12, 25, 27, 29, 32, 61, 64, 66, 68],
        "SP": [1, 4, 7, 11, 12, 13, 26, 27, 28, 41, 42, 43, 48, 49, 50, 54, 55, 56, 69, 70, 71, 88, 89, 90],
        "CG": [4, 6, 8, 9, 10, 11, 13, 16, 17, 19, 22],
        "EP": [6, 8],
        "FT": [3, 5],
        "LU": [1, 2, 4, 8, 10, 11, 17, 34, 35, 36, 37, 45],
        "MG": [6, 9, 10, 11, 12, 13, 14, 15, 16, 21, 23, 24]
    }
    
    不需要重构的 = {
        "BT": [2, 3, 6, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 28, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 62, 63, 65, 67, 69],
        "SP": [2, 3, 5, 6, 8, 9, 10, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 44, 45, 46, 47, 51, 52, 53, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87],
        "CG": [1, 2, 3, 5, 7, 12, 14, 15, 18, 20, 21, 23, 24],
        "EP": [1, 2, 3, 4, 5, 7],
        "FT": [1, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
        "LU": [3, 5, 6, 7, 9, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49],
        "MG": [1, 2, 3, 4, 5, 7, 8, 17, 18, 19, 20, 22, 25, 26, 27, 28, 29, 30]
    }
    base_dir = os.environ.get('BASE_DIR', os.getcwd())
    # NPB基准程序路径
    npb_dirs = [
        os.path.join(base_dir, "NPB3.0-omp-C", "BT"),
        os.path.join(base_dir, "NPB3.0-omp-C", "CG"), 
        os.path.join(base_dir, "NPB3.0-omp-C", "EP"),
        os.path.join(base_dir, "NPB3.0-omp-C", "FT"),
        os.path.join(base_dir, "NPB3.0-omp-C", "LU"),
        os.path.join(base_dir, "NPB3.0-omp-C", "MG"),
        os.path.join(base_dir, "NPB3.0-omp-C", "SP")
    ]
    
    total_removed = 0
    
    for npb_dir in npb_dirs:
        if not os.path.exists(npb_dir):
            print(f"跳过不存在的目录: {npb_dir}")
            continue
            
        benchmark_name = os.path.basename(npb_dir)
        print(f"\n处理 {benchmark_name}...")
        
        # 获取分类信息
        refactor_needed = 需要重构的.get(benchmark_name, [])
        direct_parallel = 不需要重构的.get(benchmark_name, [])
        
        # 处理for_pattern_baseline文件夹（应该只保留不需要重构的）
        baseline_dir = os.path.join(npb_dir, "for_pattern_baseline")
        if os.path.exists(baseline_dir):
            print(f"  清理 for_pattern_baseline...")
            removed = clean_folder(baseline_dir, direct_parallel, refactor_needed, "baseline")
            total_removed += removed
        
        # 处理for_refinement文件夹（应该只保留需要重构的）
        refinement_dir = os.path.join(npb_dir, "for_refinement")
        if os.path.exists(refinement_dir):
            print(f"  清理 for_refinement...")
            removed = clean_folder(refinement_dir, refactor_needed, direct_parallel, "refinement")
            total_removed += removed
    
    print(f"\n清理完成！总共删除了 {total_removed} 个文件")

def clean_folder(folder_path, keep_numbers, remove_numbers, folder_type):
    """
    清理指定文件夹，只保留应该保留的文件
    
    Args:
        folder_path: 文件夹路径
        keep_numbers: 应该保留的循环编号列表
        remove_numbers: 应该删除的循环编号列表
        folder_type: 文件夹类型（用于日志）
    
    Returns:
        删除的文件数量
    """
    removed_count = 0
    
    if not os.path.exists(folder_path):
        return 0
    
    # 获取文件夹中所有的.c文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.c'):
            try:
                # 提取文件编号
                file_number = int(filename.replace('.c', ''))
                file_path = os.path.join(folder_path, filename)
                
                # 检查是否应该删除这个文件
                if file_number in remove_numbers:
                    os.remove(file_path)
                    print(f"    删除 {filename} (编号 {file_number} 不属于 {folder_type})")
                    removed_count += 1
                elif file_number in keep_numbers:
                    print(f"    保留 {filename} (编号 {file_number} 属于 {folder_type})")
                else:
                    print(f"    警告: {filename} (编号 {file_number} 不在任何分类中)")
                    
            except ValueError:
                print(f"    跳过非数字文件名: {filename}")
    
    return removed_count

def verify_cleanup():
    """验证清理结果"""
    print("\n验证清理结果...")
    
    npb_dirs = [
        "D:\\New_NPB\\NPB3.0-omp-C\\BT",
        "D:\\New_NPB\\NPB3.0-omp-C\\CG", 
        "D:\\New_NPB\\NPB3.0-omp-C\\EP",
        "D:\\New_NPB\\NPB3.0-omp-C\\FT",
        "D:\\New_NPB\\NPB3.0-omp-C\\LU",
        "D:\\New_NPB\\NPB3.0-omp-C\\MG",
        "D:\\New_NPB\\NPB3.0-omp-C\\SP"
    ]
    
    for npb_dir in npb_dirs:
        if not os.path.exists(npb_dir):
            continue
            
        benchmark_name = os.path.basename(npb_dir)
        
        # 统计各文件夹中的文件数量
        origin_dir = os.path.join(npb_dir, "for_origin")
        baseline_dir = os.path.join(npb_dir, "for_pattern_baseline")
        refinement_dir = os.path.join(npb_dir, "for_refinement")
        
        origin_count = len([f for f in os.listdir(origin_dir) if f.endswith('.c')]) if os.path.exists(origin_dir) else 0
        baseline_count = len([f for f in os.listdir(baseline_dir) if f.endswith('.c')]) if os.path.exists(baseline_dir) else 0
        refinement_count = len([f for f in os.listdir(refinement_dir) if f.endswith('.c')]) if os.path.exists(refinement_dir) else 0
        
        print(f"{benchmark_name}:")
        print(f"  for_origin: {origin_count} 文件")
        print(f"  for_pattern_baseline: {baseline_count} 文件")
        print(f"  for_refinement: {refinement_count} 文件")

if __name__ == "__main__":
    print("开始清理baseline和refinement文件夹...")
    print("=" * 50)
    
    # 执行清理
    clean_folders()
    
    # 验证结果
    verify_cleanup()
    
    print("\n清理完成！")