# Excel-to-Markdown three distributions

User authorized publishing three variants and delegated implementation. Use one canonical implementation plus reproducible distribution builder, three standalone Skill directories and three ZIPs; publish together on the feature branch with a reviewable PR, leaving main untouched.

- [x] Add tested backend selection: openpyxl does not run external tools or need PyMuPDF; officecli exports auxiliary HTML with explicit fidelity warning, without invoking LibreOffice; libreoffice keeps PNG/PDF flowchart support.
- [x] Build independent .trae/skills/excel-to-md-{openpyxl,officecli,libreoffice} directories with fixed default profile, correct dependencies and variant-specific instructions. Package reproducibly; omit virtualenvs/cache/binaries.
- [x] Verify pure package in a fresh dependency-only venv; run real OfficeCLI export and LibreOffice render; verify all original full-sample stats, source hashes, all relative assets and ZIP integrity.
- [ ] Write comparison/download/installation docs, commit, push and create PR; verify remote SHA and attach PR.

Validation: 13/13 backend and original regression tests passed with real OfficeCLI; package test passed; clean pure venv 10 passed/3 dependency-related skips; three full-workbook conversions preserve original totals/hash and all asset links. Review found legacy .xls backend isolation bypass; failing marker test reproduced it, then gating legacy conversion fixed it and suite passed.
