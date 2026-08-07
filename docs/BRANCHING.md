# 分支管理规范

## 分支命名规则

| 前缀 | 用途 | 示例 |
|------|------|------|
| `main` | 主分支，稳定的项目结构和模板 | `main` |
| `verify/<tool>` | 工具验证分支 | `verify/office-cli` |
| `feat/<name>` | 新功能/新特性分支 | `feat/harness-auto-report` |
| `fix/<name>` | 修复分支 | `fix/validation-template` |

## 分支操作流程

### 1. 开始新工具验证

```bash
# 从 main 创建验证分支
git checkout main
git pull origin main
git checkout -b verify/<tool-name>

# 或使用 Harness 脚本
./harness/scripts/create-branch.sh <tool-name>
```

### 2. 完成验证

```bash
# 在验证分支上工作
git add .
git commit -m "验证(<tool-name>): 完成安装步骤文档"

# 推送到远程
git push -u origin verify/<tool-name>
```

### 3. 验证结果归档

验证完成后，验证分支保持不删除，作为历史记录。关键的验证报告可以考虑合并回 main。
