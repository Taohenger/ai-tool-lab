# tests/ 目录说明

本目录留作运行自动化测试脚本的入口；验证工程实际的数据文件统一放在 `../test-data/` 下，命令执行的证据统一放在 `../results/evidence/` 下。

本工程当前所有测试用例都在 `../tasks/` 下按任务拆分（task.md + results/result.md），单测结果统一写在各任务的 result.md 里，不额外写 pytest / jest 脚本。
