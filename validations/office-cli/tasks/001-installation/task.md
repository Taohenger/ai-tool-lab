# 任务 001 — OfficeCLI 安装与配置验证

## 任务概述

本任务验证 OfficeCLI 在当前 Linux 环境下的安装、配置和基础可用性。

## 任务目标

- ✅ 确认 OfficeCLI 能够成功下载和安装
- ✅ 确认基础命令（version、help、create）正常工作
- ✅ 确认能够创建空白 Excel 文件
- ✅ 确认配置文件正确生成

## 测试用例列表

| 用例 ID | 用例名称 | 优先级 |
|---------|---------|--------|
| TC-001 | 下载并安装 OfficeCLI 二进制文件 | P0 |
| TC-002 | 验证 version 和 help 命令 | P0 |
| TC-003 | 执行 officecli install 完成自安装 | P1 |
| TC-004 | 创建空白 Excel 文件 | P0 |
| TC-005 | 验证配置文件生成 | P2 |

---

## TC-001: 下载并安装 OfficeCLI 二进制文件

**目标**：验证 OfficeCLI 能够在当前环境中正确安装

**前置条件**：
- [ ] 网络连接正常
- [ ] 有 ~/.local/bin 目录的写入权限

**步骤**：

### 步骤 1.1：使用安装脚本安装

执行命令：
```bash
cd /workspace/validations/office-cli
bash harness/scripts/install-officecli.sh
```

**预期结果**：
- 脚本成功执行
- officecli 二进制文件被下载到 ~/.local/bin/
- 文件具有可执行权限

### 步骤 1.2：验证二进制文件存在

执行命令：
```bash
ls -la ~/.local/bin/officecli
```

**预期结果**：
- 文件存在
- 文件大小 > 0
- 有可执行权限（x）

---

## TC-002: 验证 version 和 help 命令

**目标**：验证基础信息命令正常工作

**前置条件**：
- [ ] TC-001 已通过

**步骤**：

### 步骤 2.1：查看版本

执行命令：
```bash
officecli --version
```

**预期结果**：
- 输出 OfficeCLI 的版本号
- 无错误信息

### 步骤 2.2：查看帮助

执行命令：
```bash
officecli --help
```

**预期结果**：
- 输出所有可用命令的列表
- 包含 create、view、add、set、get、remove 等核心命令

---

## TC-003: 执行 officecli install 完成自安装

**目标**：验证自安装功能

**前置条件**：
- [ ] TC-001 已通过

**步骤**：

### 步骤 3.1：执行自安装

执行命令：
```bash
officecli install
```

**预期结果**：
- 安装过程顺利完成
- 提示安装成功

### 步骤 3.2：检查配置目录

执行命令：
```bash
ls -la ~/.officecli/
```

**预期结果**：
- 配置目录存在
- 可能包含 config.json 等配置文件

---

## TC-004: 创建空白 Excel 文件

**目标**：验证 Excel 文件创建功能

**前置条件**：
- [ ] TC-002 已通过

**步骤**：

### 步骤 4.1：创建空白 xlsx 文件

执行命令：
```bash
cd /workspace/validations/office-cli
officecli create test-data/blank-test.xlsx
```

**预期结果**：
- 命令成功执行，无报错
- 文件 test-data/blank-test.xlsx 被创建

### 步骤 4.2：验证文件存在且有效

执行命令：
```bash
ls -la test-data/blank-test.xlsx
file test-data/blank-test.xlsx
```

**预期结果**：
- 文件存在，大小 > 0
- file 命令显示为 Microsoft Excel 或 ZIP 格式（xlsx 本质是 ZIP）

---

## TC-005: 验证配置文件生成

**目标**：验证配置系统正常工作

**前置条件**：
- [ ] TC-003 已通过

**步骤**：

### 步骤 5.1：查看配置

执行命令：
```bash
cat ~/.officecli/config.json 2>/dev/null || echo "配置文件不存在（这可能是正常的）"
```

**预期结果**：
- 如果存在，是有效的 JSON 格式
- 如果不存在，记录下来（非阻塞问题）

---

## 完成标准

- [ ] 所有 P0 级用例通过
- [ ] 至少 1 个 Excel 文件成功创建
- [ ] officecli --version 正常输出版本
