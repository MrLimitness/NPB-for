# NPB OpenMP 循环优化项目

本项目提供了一套完整的工具链，用于分析、提取、优化和替换 NPB (NAS Parallel Benchmarks) 基准测试程序中的 for 循环，支持基于 OpenMP 的并行化优化。

## 📁 项目结构

```
D:\New_NPB\
├── NPB3.0-omp-C/          # NPB基准测试源代码
│   ├── BT/                # Block Tridiagonal solver
│   ├── CG/                # Conjugate Gradient
│   ├── EP/                # Embarrassingly Parallel
│   ├── FT/                # Fast Fourier Transform
│   ├── LU/                # Lower-Upper Gauss-Seidel solver
│   ├── MG/                # Multi-Grid
│   └── SP/                # Scalar Pentadiagonal solver
├── prompt/                # AI优化提示词模板
│   ├── 0.txt             # 基础优化提示词
│   ├── 1.txt-5.txt       # 针对性优化提示词
│   └── refine.txt        # 高级重构提示词
├── dependency_analysis_manual/  # 循环依赖分析报告
│   ├── direct_parallelizable/   # 可直接并行化的循环
│   └── needs_refactoring/       # 需要重构的循环
├── extract_for.py         # for循环提取工具
├── pattern.py            # 基础并行化优化
├── refine.py             # 高级重构优化
├── project.py            # 循环替换和项目管理
├── API.py                # AI API调用接口
└── clean.py              # 清理工具
```

### NPB 基准测试程序文件结构

每个基准测试目录（如 BT/、CG/等）包含：

```
BT/
├── bt_#_omp.c            # 去除注释和OpenMP的原始代码
├── bt_ori.c              # 专家优化的原始备份
├── bt.c                  # 实际编译执行的代码
├── header.h              # 头文件
├── npbparams.h           # 参数配置
├── for_origin/           # 提取的原始for循环
├── for_pattern_baseline/ # 基础并行化优化后的循环
└── for_refinement/       # 高级重构优化后的循环
```

## 🚀 快速开始

### 1. 环境准备

确保您已安装 Python 3.6+，并安装所需依赖：

```powershell
pip install openai
```

### 2. 配置 API 密钥

编辑 `API.py` 文件，设置您的 AI 服务 API 密钥：

```python
openai.base_url = 'https://api.siliconflow.cn/v1/'
openai.api_key = 'your_api_key_here'
```

### 3. 基本使用流程

#### 步骤 1：提取 for 循环

```powershell
# 提取所有NPB程序的for循环
python extract_for.py --all

# 或提取单个程序的循环
python extract_for.py --file "D:\New_NPB\NPB3.0-omp-C\CG\cg_#_omp.c"
```

此步骤会为每个基准测试程序创建三个文件夹：

- `for_origin/`: 原始循环代码（1.c, 2.c, 3.c...）
- `for_pattern_baseline/`: 基础并行化版本（空文件，待生成）
- `for_refinement/`: 高级重构版本（空文件，待生成）

#### 步骤 2：生成基础并行化优化

```powershell
# 对所有程序进行基础OpenMP优化
python pattern.py

# 或指定特定程序
python pattern.py --folder CG BT
```

#### 步骤 3：生成高级重构优化

```powershell
# 对指定程序进行高级重构优化
python refine.py --folder BT

# 或处理多个程序
python refine.py --folder BT CG SP
```

#### 步骤 4：应用优化到源代码

```python
from project import init_NPB, replace_NPB, replace_all, run_NPB

# 初始化基准测试程序
init_NPB('CG')

# 替换单个循环
replace_NPB('CG', '1.c', 'for_pattern_baseline')

# 批量替换所有优化的循环
replace_all('CG', 'for_pattern_baseline')

# 运行测试验证结果
success, time_taken = run_NPB('CG', 'S')
print(f"运行结果: {success}, 执行时间: {time_taken}秒")
```

## 🔧 详细功能说明

### extract_for.py - for 循环提取工具

**功能**: 从 C 源文件中提取所有 for 循环并保存为独立的 C 文件

**主要特性**:

- 智能识别嵌套循环
- 自动处理大括号匹配
- 生成带编号的循环文件（1.c, 2.c, ...）
- 同时创建优化文件夹结构

**使用方法**:

```powershell
# 处理所有NPB文件
python extract_for.py --all

# 处理单个文件
python extract_for.py --file path\to\file.c

# 自定义输出目录
python extract_for.py --all --output my_loops
```

### pattern.py - 基础并行化优化

**功能**: 使用 AI 对 for 循环进行基础的 OpenMP 并行化优化

**优化策略**:

- 添加适当的 OpenMP 指令
- 选择合适的调度策略
- 处理数据竞争问题
- 设置私有变量

**使用方法**:

```powershell
# 处理默认的所有程序
python pattern.py

# 处理指定程序
python pattern.py --folder CG BT SP
```

### refine.py - 高级重构优化

**功能**: 对需要重构的循环进行深度优化

**优化策略**:

- 循环依赖分析和解除
- 算法重构
- 内存访问模式优化
- 高级并行化技术

**使用方法**:

```powershell
# 处理指定程序（默认只处理BT）
python refine.py --folder BT

# 处理多个程序
python refine.py --folder BT CG LU
```

### project.py - 项目管理和循环替换

**核心功能**:

1. **init_NPB(bench)**: 初始化基准测试程序
2. **replace_NPB(bench, loop_file, folder)**: 替换单个循环
3. **replace_all(bench, folder)**: 批量替换循环
4. **run_NPB(bench, CLASS)**: 运行并测试基准程序

**使用示例**:

```python
from project import *

# 初始化CG程序
init_NPB('CG')

# 应用基础优化
replace_all('CG', 'for_pattern_baseline')

# 应用高级优化
replace_all('CG', 'for_refinement')

# 运行测试
success, time = run_NPB('CG', 'S')
```

### API.py - AI 服务接口

**功能**: 封装 AI 服务调用接口

**主要函数**:

- `ask_gpt_question(prompt)`: 简单的 API 调用
- `sys_question(sys_prompt, prompt)`: 带系统提示词的调用

### clean.py - 清理工具

**功能**: 清理生成的文件和重置项目状态

## 📊 支持的 NPB 基准测试

| 基准测试 | 全名                    | 说明             | 复杂度 |
| -------- | ----------------------- | ---------------- | ------ |
| BT       | Block Tridiagonal       | 块三对角线求解器 | 高     |
| CG       | Conjugate Gradient      | 共轭梯度法       | 中     |
| EP       | Embarrassingly Parallel | 易并行问题       | 低     |
| FT       | Fast Fourier Transform  | 快速傅里叶变换   | 中     |
| LU       | Lower-Upper             | 下上三角分解     | 高     |
| MG       | Multi-Grid              | 多重网格法       | 高     |
| SP       | Scalar Pentadiagonal    | 标量五对角线     | 高     |

## 🎯 优化策略

### 基础并行化 (pattern.py)

- 适用于可直接并行化的循环
- 主要添加 `#pragma omp parallel for` 指令
- 自动选择合适的调度策略
- 处理简单的数据依赖问题

### 高级重构 (refine.py)

- 适用于存在复杂依赖的循环
- 循环分裂和重组
- 数据依赖解除
- 算法级别的重构
- 高级并行化模式

## 🔍 完整工作流程示例

### 从零开始的优化流程

```python
from project import *

# 1. 选择要优化的基准测试
benchmark = "CG"

# 2. 提取循环（如果还没有提取）
# 在PowerShell中运行: python extract_for.py --all

# 3. 生成基础优化
# 在PowerShell中运行: python pattern.py --folder CG

# 4. 生成高级优化（仅对需要重构的循环）
# 在PowerShell中运行: python refine.py --folder CG

# 5. 初始化基准测试
init_NPB(benchmark)

# 6. 获取基础性能
success, baseline_time = run_NPB(benchmark, 'S')
print(f"基础版本: {baseline_time}秒")

# 7. 应用基础优化
replace_all(benchmark, 'for_pattern_baseline')
success, pattern_time = run_NPB(benchmark, 'S')
print(f"基础优化后: {pattern_time}秒")

# 8. 重新初始化
init_NPB(benchmark)

# 9. 应用高级优化
replace_all(benchmark, 'for_refinement')
success, refined_time = run_NPB(benchmark, 'S')
print(f"高级优化后: {refined_time}秒")

# 10. 计算加速比
if baseline_time > 0:
    pattern_speedup = baseline_time / pattern_time
    refined_speedup = baseline_time / refined_time
    print(f"基础优化加速比: {pattern_speedup:.2f}x")
    print(f"高级优化加速比: {refined_speedup:.2f}x")
```

### 批量测试所有基准程序

```powershell
# 1. 提取所有程序的循环
python extract_for.py --all

# 2. 生成所有基础优化
python pattern.py

# 3. 生成重点程序的高级优化
python refine.py --folder BT CG LU MG SP

# 4. 使用project.py进行性能测试
python project.py
```

## 📂 依赖分析报告

项目包含了详细的依赖分析报告，位于 `dependency_analysis_manual/` 目录：

### direct_parallelizable/

记录了每个基准程序中可以直接并行化的循环编号

### needs_refactoring/

记录了每个基准程序中需要重构才能并行化的循环编号

这些分析报告指导了优化策略的选择。

## 💼 提示词系统

项目使用位于 `prompt/` 目录下的提示词文件来指导 AI 优化：

- `0.txt`: 基础 OpenMP 并行化提示词
- `1.txt-5.txt`: 不同级别的优化策略提示词
- `refine.txt`: 高级重构和算法优化提示词

## ⚠️ 注意事项

1. **API 配置**: 确保正确配置 AI 服务的 API 密钥和基础 URL
2. **编译环境**: 确保系统已安装 OpenMP 支持的 C 编译器（如 GCC 或 MSVC）
3. **PowerShell**: 在 Windows 环境下使用 PowerShell 运行命令
4. **内存要求**: 某些基准测试可能需要较大内存
5. **文件备份**: 建议在进行修改前备份原始文件
6. **测试验证**: 每次优化后都应运行测试验证正确性

## 🐛 常见问题

**Q: API 调用失败怎么办？**
A: 检查网络连接和 API 密钥配置，脚本会自动重试

**Q: 编译失败？**
A: 检查 OpenMP 编译器是否正确安装，查看 make 输出信息

**Q: 运行结果不正确？**
A: 使用 `init_NPB()` 重置到原始版本，检查优化代码

**Q: 循环替换失败？**
A: 确保循环文件不为空，检查循环序号是否正确

**Q: PowerShell 命令无法识别？**
A: 确保使用正确的 PowerShell 语法，路径使用反斜杠

## 📈 性能评估

项目提供了完整的性能评估框架：

- **正确性验证**: 每次运行都会验证结果正确性
- **执行时间测量**: 精确测量优化前后的执行时间
- **加速比计算**: 自动计算并行化带来的性能提升
- **多级别测试**: 支持不同数据规模的测试（S、W、A、B、C）

## 🎁 项目特色

- **自动化循环提取**: 智能识别和提取 C 代码中的 for 循环
- **AI 驱动优化**: 基于大语言模型的智能并行化优化
- **分层优化策略**: 区分简单并行化和复杂重构
- **完整工具链**: 从提取、优化到替换、测试的完整流程
- **性能验证**: 内置正确性检查和性能测试

## 🤝 贡献指南

欢迎提交 Issues 和 Pull Requests 来改进这个项目！

## 📄 许可证

MIT License

---

**项目维护者**: NPB 优化团队  
**最后更新**: 2025 年 6 月 11 日
