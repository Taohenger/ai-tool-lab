# 测试文件目录

> 注意：本验证工程的测试数据文件实际存放在 **`test-data/`** 目录中，而非本目录。

## 测试数据文件一览（`test-data/`）

| 文件 | 用途 | 对应任务 |
|------|------|---------|
| `blank-test.xlsx` | 空白 Excel 文件，验证创建功能 | 001 |
| `basic-rw-test.xlsx` | 基础读写测试数据（姓名/年龄/分数 5 行） | 002 |
| `formulas-test.xlsx` | 公式测试数据（算术/聚合/逻辑/查找/文本 6 类） | 003 |
| `hidden-test.xlsx` | 隐藏行列测试数据（含 hidden/veryHidden 工作表） | 004 |
| `advanced-test.xlsx` | 进阶功能测试数据（Table/命名范围/排序/CSV 导入） | 005 |
| `deep-test.xlsx` | 深度进阶测试数据（图表/条件格式/数据验证/筛选/超链接/注释） | 005 |
| `csv-import-test.xlsx` | CSV 导入目标文件 | 005 |
| `import.csv` | CSV 导入源文件（3 行 4 列） | 005 |
| `word-test.docx` | Word 测试文档（段落/表格/格式/列表/链接） | 006 |
| `ppt-test.pptx` | PPT 测试演示（2 张幻灯片/形状/表格/图表） | 007 |

## 测试证据文件一览（`results/evidence/`）

所有命令执行的输出和截图都按任务分目录存放：

```
results/evidence/
├── 001-installation/      # 安装验证（7 个证据文件）
├── 002-excel-basic-rw/    # 基础读写（19 个证据文件）
├── 003-excel-formulas/    # 公式验证（9 个证据文件）
├── 004-excel-hidden/      # 隐藏行列（7 个证据文件）
├── 005-excel-advanced/    # 进阶功能（25+ 个证据文件）
├── 006-word/               # Word 验证（10 个证据文件）
└── 007-ppt/                # PPT 验证（8 个证据文件）
```

## 目录说明

```
validations/office-cli/
├── test-data/              # ✅ 测试数据文件（10 个）
├── results/evidence/       # ✅ 测试证据文件（分任务存放）
├── tasks/                   # ✅ 测试任务定义 + 结果报告
└── tests/                   # 本目录（预留）
```
