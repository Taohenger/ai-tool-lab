# 任务 008 — 横展开报告模板（Excel）生成验证

## 任务概述

本任务验证 OfficeCLI 作为 **AI 代理输出的数据写入引擎** 时的实战能力：模拟 CloudCode / 各種 Agent が生成した横展开报告数据（JSON）を OfficeCLI を使って Excel テンプレートに流し込み、最終的なレポートを生成します。

> **背景**：ユーザー（開発チーム）は、Agent がコードを横展開調査した結果を「共通の Excel レポート形式」で自動出力させたい。
> テンプレート × JSON データ → OfficeCLI → 完成レポート というパイプラインの実証検証。

## タスクゴール

- ✅ 3 シート構成の横展开报告テンプレート作成
- ✅ CloudCode / Agent が出力する JSON データ構造の定義
- ✅ OfficeCLI セット系コマンドを使ったテンプレート埋め込み（逐次実行）
- ✅ OfficeCLI `merge` コマンド + `{{key}}` プレースホルダーによる置換方式の検証
- ✅ 生成された Excel を OfficeCLI で再読み込み → 内容正しさの検証
- ✅ テンプレート・サンプルコード・検査観点一式をレポジトリに残し、デモ可能にする

## テストケース一覧

| 用例 ID | 用例名称 | 優先度 |
|---------|---------|--------|
| TC-001 | 横展开报告テンプレート Excel の構成確認（3 Sheet） | P1 |
| TC-002 | 検査観点 JSON × サンプルコード 2 件の準備確認 | P1 |
| TC-003 | Sheet1「横展开报告」に OfficeCLI set でレポート基本情報を埋め込み | P1 |
| TC-004 | Sheet1「検査観点一覧表」に set/add で行を埋め込み | P1 |
| TC-005 | Sheet2「モニタリング結果一覧」に set/add で表を埋め込み | P1 |
| TC-006 | Sheet3「詳細明細」に set/add で 10 件以上の検索詳細行を埋め込み | P1 |
| TC-007 | 完成レポートを officecli view outline で可視化確認 | P1 |
| TC-008 | 完成レポートを officecli get --json でデータとして再読み込み検証 | P1 |
| TC-009 | officecli merge コマンドによる {{key}} 置換方式の比較実験 | P2 |
| TC-010 | テンプレート→完成レポートの変更差分（ファイルサイズ・壊れ無し） | P2 |

---

## TC-001: テンプレート 3 Sheet 構成確認

**目標**：`横展开报告模板.xlsx` が 3 Sheet であり、各 Sheet のタブ色・列幅などが正しいこと。

**手順**：
```bash
export PATH="$HOME/.officecli/bin:$PATH"
cd /workspace/validations/office-cli
TEMPLATE=test-data/template-demo/横展开报告模板.xlsx

officecli query "$TEMPLATE" sheet --json
officecli view  "$TEMPLATE" outline
```

**期待結果**：
- Sheet 一覧に `1_横展开报告` `2_监测一览` `3_详细明細` が存在する
- 各 Sheet にプレースホルダ（`{{report_id}}` など）が正しく配置されている

---

## TC-002: 検査観点 JSON とサンプルコードの準備確認

**目標**：CloudCode/Agent の模擬入力データを準備する。

**手順**：
```bash
ls -la test-data/template-demo/
ls -la test-data/template-demo/sample-code/
cat test-data/template-demo/check-viewpoints.json | jq length
```

**期待結果**：
- サンプルコードが 2 ファイル存在：`auth-service.ts`, `payment-processor.go`
- 検査観点 JSON が 3 件（横展開・ハードコード・情報漏洩）
- 各観点には regex が定義されている

---

## TC-003: Sheet1 レポート基本情報埋め込み

**目標**：OfficeCLI の `set` コマンドで、Sheet1 のレポート基本情報セクションに値を流し込む。

**手順**：
```bash
TEMPLATE=test-data/template-demo/横展开报告模板.xlsx
REPORT=test-data/template-demo/横展开报告-完成版.xlsx
cp "$TEMPLATE" "$REPORT"

# 报告基本情報
officecli set "$REPORT" /1_横展开报告/B3  --prop value="OOO-2026-0804-001"
officecli set "$REPORT" /1_横展开报告/E3  --prop value="2026-08-04"

# 1. 目的
officecli set "$REPORT" /1_横展开报告/A6  \
  --prop value="チーム共通の問題（エラーメッセージ横展開漏れ・ハードコード・機密情報出力）に対し、認証/決済サービスの横展開調査を実施し、是正箇所を明らかにする。"

# 2. 分支
officecli set "$REPORT" /1_横展开报告/B9  --prop value="feature/auth-enterprise, feature/payment-v2"
officecli set "$REPORT" /1_横展开报告/B10 --prop value="a8f3c91e, 4d7b2250"

# 3. 作业时间
officecli set "$REPORT" /1_横展开报告/B13 --prop value="2026-08-04 09:30"
officecli set "$REPORT" /1_横展开报告/E13 --prop value="2026-08-04 14:15"
officecli set "$REPORT" /1_横展开报告/B14 --prop value="4.5"

# 4. 方法
officecli set "$REPORT" /1_横展开报告/A17 \
  --prop value="Step1: 検査観点 3 項目を定義 → Step2: CloudCode Agent が対象コードに grep/regex → Step3: 該当箇所を Sheet2/Sheet3 に自動集計 → Step4: 結論を Sheet1 に記載。"

# 6. 結論
officecli set "$REPORT" /1_横展开报告/B26 --prop value="2"
officecli set "$REPORT" /1_横展开报告/B27 --prop value="15"
officecli set "$REPORT" /1_横展开报告/B28 --prop value="12"
officecli set "$REPORT" /1_横展开报告/E28 --prop value="要対応"
officecli set "$REPORT" /1_横展开报告/B29 \
  --prop value="全体として横展開（日本語化）・ハードコード・情報漏洩いずれも該当箇所が検出された。特に payment-processor.go の DB パスワードハードコードと auth-service.ts のパスワードログ出力は P0 として今週中の修正必須。"

# 署名
officecli set "$REPORT" /1_横展开报告/B32 --prop value="Taohenger（開発チーム）"
officecli set "$REPORT" /1_横展开报告/E32 --prop value="（承認待ち）"

officecli save "$REPORT"
```

---

## TC-004: Sheet1 検査観点表を埋め込み

**目標**：`A20:D23` の表に、3 つの検査観点を埋め込む。

**手順**：
```bash
# 既存の {{placeholders}} があるセルを上書き
officecli set "$REPORT" /1_横展开报告/B21 --prop value="横展開（日本語化）"
officecli set "$REPORT" /1_横展开报告/C21 --prop value="エラーメッセージ・コメントの日本語化漏れチェック"
officecli set "$REPORT" /1_横展开报告/D21 --prop value="高 (P1)"

officecli set "$REPORT" /1_横展开报告/B22 --prop value="ハードコード確認"
officecli set "$REPORT" /1_横展开报告/C22 --prop value="DB/API/Secret の直埋め込み検出"
officecli set "$REPORT" /1_横展开报告/D22 --prop value="高 (P1)"

officecli set "$REPORT" /1_横展开报告/B23 --prop value="情報漏洩チェック"
officecli set "$REPORT" /1_横展开报告/C23 --prop value="ログ/標準出力への機密情報出力検出"
officecli set "$REPORT" /1_横展开报告/D23 --prop value="高 (P1)"
```

---

## TC-005: Sheet2 モニタリング一覧埋め込み

**目標**：ファイル単位の検査サマリ（2 ファイル）を書き込み、合計行も埋める。

**手順**：
```bash
# ファイル 1: auth-service.ts
officecli set "$REPORT" /2_监测一览/A6 --prop value="1"
officecli set "$REPORT" /2_监测一览/B6 --prop value="auth-service.ts"
officecli set "$REPORT" /2_监测一览/C6 --prop value="4"
officecli set "$REPORT" /2_监测一览/D6 --prop value="2"
officecli set "$REPORT" /2_监测一览/E6 --prop value="1"
officecli set "$REPORT" /2_监测一览/F6 --prop value="7"
officecli set "$REPORT" /2_监测一览/G6 --prop value="要修正"
officecli set "$REPORT" /2_监测一览/H6 --prop value="P0: パスワードログ出力あり"

# ファイル 2: payment-processor.go
officecli set "$REPORT" /2_监测一览/A7 --prop value="2"
officecli set "$REPORT" /2_监测一览/B7 --prop value="payment-processor.go"
officecli set "$REPORT" /2_监测一览/C7 --prop value="4"
officecli set "$REPORT" /2_监测一览/D7 --prop value="3"
officecli set "$REPORT" /2_监测一览/E7 --prop value="1"
officecli set "$REPORT" /2_监测一览/F7 --prop value="8"
officecli set "$REPORT" /2_监测一览/G7 --prop value="要修正"
officecli set "$REPORT" /2_监测一览/H7 --prop value="P0: DBパスワード直埋め込み"

# 合計行
officecli set "$REPORT" /2_监测一览/C16 --prop value="8"
officecli set "$REPORT" /2_监测一览/D16 --prop value="5"
officecli set "$REPORT" /2_监测一览/E16 --prop value="2"
officecli set "$REPORT" /2_监测一览/F16 --prop value="15"
```

---

## TC-006: Sheet3 詳細明細埋め込み（10 行）

**目標**：各 VP に該当したコード箇所を 10 行分埋め込む。合計 15 件のうち代表 10 件。

**手順**：
```bash
# 行 6〜15 に詳細を記載（代表 10 件）
# 1) auth-service: 日本語化漏れエラー ×2
officecli batch "$REPORT" --commands '[
  {"command":"set","path":"/3_详细明細/A6","props":{"value":"1"}},
  {"command":"set","path":"/3_详细明細/B6","props":{"value":"src/auth/auth-service.ts"}},
  {"command":"set","path":"/3_详细明細/C6","props":{"value":"34"}},
  {"command":"set","path":"/3_详细明細/E6","props":{"value":"throw new UnauthorizedException(\"Invalid email or password\")"}},
  {"command":"set","path":"/3_详细明細/F6","props":{"value":"VP-001 横展開"}}},
  {"command":"set","path":"/3_详细明細/G6","props":{"value":"中"}},
  {"command":"set","path":"/3_详细明細/H6","props":{"value":"はい"}},
  {"command":"set","path":"/3_详细明細/I6","props":{"value":"「メールアドレスまたはパスワードが正しくありません」に変更"}}
]'
# …以下 9 行を同様に batch コマンドで追記
```

---

## TC-007: view outline による可視化

**目標**：完成したレポートを人間が見て正しいかを outline で確認。

**手順**：
```bash
officecli view "$REPORT" outline
```

---

## TC-008: get --json で値の再読み込み検証

**目標**：OfficeCLI で書き込んだ値を OfficeCLI で読み出して一致確認。

**手順**：
```bash
officecli get "$REPORT" /1_横展开报告/B3 --json | jq '.text'       # OOO-2026-0804-001
officecli get "$REPORT" /2_监测一览/F16 --json  | jq '.text'      # 15
officecli get "$REPORT" /3_详细明細/E6 --json  | jq '.text'       # コードスニペット
```

---

## TC-009: merge コマンド実験（任意）

**目標**：`officecli merge` の `{{key}}` 置換方式でも同等のレポートが作れるか検証。

**手順**：
```bash
officecli merge "$TEMPLATE" "$REPORT" --data test-data/template-demo/report-data.json
```

---

## TC-010: 生成物健全性

**目標**：テンプレートと完成版の両方を validate し、OpenXML バリデーションを通過すること。

**手順**：
```bash
officecli validate "$TEMPLATE" && echo "テンプレート正常"
officecli validate "$REPORT"   && echo "完成版正常"
ls -lh "$TEMPLATE" "$REPORT"
```

---

## 完成基準

- [ ] P1 用例（TC-001 〜 008）がすべて実施済み
- [ ] 各コマンドの実行結果が `results/evidence/008-template-report/` に保存されている
- [ ] サンプルコード 2 ファイル、検査観点 JSON、テンプレート、完成レポートの 4 種類の成果物がすべて存在
- [ ] `tasks/008-template-report/results/result.md` に結論を記載
