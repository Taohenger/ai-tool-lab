# Harness —— 验证辅助工具集

Harness 目录提供用于辅助工具验证的脚本、模板和自动化工具。

## 目录结构

```
harness/
├── README.md                # 本文件
├── scripts/                 # 自动化脚本
│   ├── create-branch.sh     # 创建验证分支
│   └── init-validation.sh   # 初始化新工具验证目录
└── templates/               # 验证报告模板
    └── validation-report.md # 标准验证报告模板
```

## 脚本使用

### 创建验证分支

```bash
./harness/scripts/create-branch.sh <tool-name>
```

### 初始化新验证目录

```bash
./harness/scripts/init-validation.sh <tool-name>
```
