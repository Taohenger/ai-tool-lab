# Excel Flowcharts Implementation Plan

Goal: Preserve designer-authored Excel flowcharts as images plus explicit OOXML node/connector evidence, without inventing connections or changing source files.
Architecture: DrawingML parser inventories nested shapes, connectors and their endpoint IDs per sheet. LibreOffice exports a disposable exact workbook copy to a single-page-per-sheet PDF; PyMuPDF converts the matching pages to PNG. Markdown links images and describes verified connections; JSON records unresolved endpoints and rendering limitations.
Constraints: Python 3.10+, original workbook read-only, existing output counts preserved, no mandatory OfficeCLI. LibreOffice optional; missing renderer produces explicit warning and retains source drawing XML. Formula screenshots may contain LibreOffice recalculations; original Markdown values remain unchanged.
Execution: User explicitly delegated decisions and implementation. Work on feature branch in the existing checkout, preserve previous verification artifacts. Implement inline with TDD and review.

Review focus: nested groups; reversed/double/missing arrowheads; dangling endpoint IDs; hidden sheets/page mapping; renderer missing/failing or suspiciously large pages.

- [x] Write drawing fixture and CLI integration tests. Verify they fail before implementation.
- [x] Add scripts/flowcharts.py with extraction and optional LibreOffice/PyMuPDF rendering. Integrate into converter without changing original shape/image counts.
- [x] Verify tests with real grouped branch flowchart and missing-renderer path; inspect actual rendered PNG. Reconvert original 5-sheet workbook and verify hashes, counts and relative assets.
- [x] Update Skill, dependency list, handoff and independent ZIP. Deliver runnable package and examples.

Progress: initial four new CLI tests failed before implementation (missing --diagram-render and drawings report); implementation then passed the original test and four new tests. Added expanded checks for hidden-sheet drawing page identity, reverse/bidirectional/undirected arrows, decorated line ends, missing required renderer and external renderer failure. Real LibreOffice render preserves native connectors; OfficeCLI is intentionally not used as a guarantee. Independent review found no high-priority defects; its hidden-sheet coverage concern is addressed with a dedicated hidden drawing and PDF page text identity assertion.

Final: 8/8 tests passed; original full sample counts/hash unchanged; all preview/resource links valid; standalone ZIP extraction conversion passed.
