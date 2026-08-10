# 项目约定与规范

## 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 任务目录 | `<NNN>-<description>/` | `001-installation/` |
| 测试用例 | `tc-<NNN>-<description>.md` | `tc-001-install-binary.md` |
| 测试结果 | `result.md`（每个任务一个） | `tasks/001-installation/results/result.md` |
| 证据文件 | `<task-id>_<step>_<desc>.<ext>` | `001_version_output.txt` |

## 状态标记规范

| 标记 | 含义 |
|------|------|
| ✅ | 通过 |
| ❌ | 失败 |
| ⚠️ | 部分支持 / 有条件通过 |
| 🔄 | 进行中 |
| ⏳ | 待执行 |

## OfficeCLI 命令使用约定

- 所有测试命令使用当前工作目录：`/workspace/validations/office-cli/`
- 生成的测试文件统一放在 `test-data/` 目录下
- 临时文件可放在 `/tmp/` 下

## 证据保存约定

- 命令输出：保存为 `.txt` 或 `.md` 文件
- 生成的 Excel 文件：保留原件在 `test-data/`
- 所有证据按任务 ID 组织在 `results/evidence/<task-id>/`
