# 任务 007：PPT CLI 功能验证任务定义

## 任务信息

| 项目 | 内容 |
|------|------|
| **任务 ID** | 007-ppt |
| **任务名称** | PPT CLI 功能验证 |
| **优先级** | 高 |
| **验证对象** | OfficeCLI v1.0.143 — PowerPoint (.pptx) 功能 |
| **前置条件** | OfficeCLI 已安装（见任务 001） |

## 任务目标

系统性验证 OfficeCLI 对 PowerPoint 演示文稿 (.pptx) 的创建和编辑能力，评估其对人类 PPT 操作的替代程度。

## 测试范围

### TC-001: 创建空白 PPT 和幻灯片
- 创建空白 .pptx 文件
- 添加多张幻灯片
- 验证幻灯片数量

### TC-002: 添加形状和文本
- 在幻灯片中添加文本框/形状
- 设置形状位置（x/y）和大小（width/height）
- 设置文本内容

### TC-003: 文本格式
- 加粗
- 字号

### TC-004: 表格
- 在幻灯片中创建表格
- 填入数据

### TC-005: 图表
- 在幻灯片中创建图表
- 设置数据和标题

### TC-006: 演示文稿结构查看
- 使用 view outline 查看幻灯片结构

## 测试数据文件

- 输出文件：`test-data/ppt-test.pptx`

## 验证步骤

### 步骤 1：准备
```bash
officecli create test-data/ppt-test.pptx
```

### 步骤 2：按顺序执行各测试用例
见上方"测试范围"中各 TC 的描述。

### 步骤 3：记录结果
- 每个测试用例的命令输出保存到 `results/evidence/007-ppt/`
- 最终结果写入 `tasks/007-ppt/results/result.md`
