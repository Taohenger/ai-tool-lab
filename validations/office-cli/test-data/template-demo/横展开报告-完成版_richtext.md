# 横展开报告-完成版

<!-- 由 excel-to-md Skill 生成；源 Excel 未被修改。 -->

> 来源文件：`横展开报告-完成版.xlsx`；工作表：3 个

> 公式保留表达式及缓存结果；无法直接转换的对象见 conversion-report.json。

# 工作表：1\_横展开报告

> 原序号：1；状态：可见；范围：A1:F32；合并单元格：10 个

## <span style="background-color:#1F4E78"><span style="color:#FFFFFF">**横展开报告**</span></span>

- **A3**：**报告编号：**
- **B3**：OOO-2026-0804-001
- **D3**：**作成日：**
- **E3**：2026-08-04 00:00:00

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**1. 横展开目的**</span></span>

チーム共通の問題（エラーメッセージ横展開漏れ・ハードコード・機密情報出力）に対し、認証/決済サービスの横展開調査を実施し、是正箇所を明らかにする。

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**2. 横展开分支（対象ブランチ）**</span></span>

| **対象ブランチ：** | feature/auth-enterprise, feature/payment-v2 |
|---|---|
| **コミットハッシュ：** | a8f3c91e, 4d7b2250 |

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**3. 横展开作业时间**</span></span>

- **A13**：**开始时间：**
- **B13**：2026-08-04 09:30:00
- **D13**：**结束时间：**
- **E13**：2026-08-04 14:15:00

- **A14**：**总工时：**
- **B14**：4.5

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**4. 横展开方法**</span></span>

Step1: 検査観点 3 項目を定義 → Step2: CloudCode Agent が対象コードに grep/regex → Step3: 該当箇所を Sheet2/Sheet3 に自動集計 → Step4: 結論を Sheet1 に記載。

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**5. 横展开观点（检查项目）**</span></span>

| <span style="background-color:#BDD7EE">**No.**</span> | <span style="background-color:#BDD7EE">**检查观点**</span> | <span style="background-color:#BDD7EE">**检查说明**</span> | <span style="background-color:#BDD7EE">**优先级**</span> |
|---|---|---|---|
| 1 | 横展開（日本語化） | エラーメッセージ・コメントの日本語化漏れチェック | 高 (P1) |
| 2 | ハードコード確認 | DB/API/Secret の直埋め込み検出 | 高 (P1) |
| 3 | 情報漏洩チェック | ログ/標準出力への機密情報出力検出 | 高 (P1) |
| **总文件数：** | 2 |  |  |
| **检查总项目数：** | 15 |  |  |

<span style="background-color:#DDEBF7"><span style="color:#1F4E78">**6. 横展开结论**</span></span>

- **A28**：**问题数：**
- **B28**：12
- **D28**：**横展开状态：**
- **E28**：<span style="color:#C00000">**要対応**</span>

- **A29**：**结论总结：**
- **B29**：全体として横展開（日本語化）・ハードコード・情報漏洩いずれも該当箇所が検出された。特に payment-processor.go の DB パスワードハードコードと auth-service.ts のパスワードログ出力は P0 として今週中の修正必須。

- **A32**：**作成者：**
- **B32**：Taohenger（開発チーム）
- **D32**：**承认者：**
- **E32**：（承認待ち）

# 工作表：2\_监测一览

> 原序号：2；状态：可见；范围：A1:H16；合并单元格：2 个

<span style="background-color:#4472C4"><span style="color:#FFFFFF">**コード検索・モニタリング結果一覧（监测一览）**</span></span>

| **报告编号：** | OOO-2026-0804-001 | 列3 | **対象ブランチ：** | feature/auth, feature/pay | 列6 | **集计日：** | 2026-08-04 00:00:00 |
|---|---|---|---|---|---|---|---|
| <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**No.**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**ファイル名 (文件)**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**观点1 該当数**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**观点2 該当数**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**观点3 該当数**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**合計**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**ステータス**</span></span> | <span style="background-color:#D6E4F0"><span style="color:#1F4E78">**備考**</span></span> |
| 1 | auth-service.ts | 4 | 2 | 1 | 7 | 要修正 | P0: パスワードログ出力あり |
| 2 | payment-processor.go | 4 | 3 | 1 | 8 | 要修正 | P0: DBパスワード直埋め込み |
| {file\_3\_no} | {file\_3\_name} | {file\_3\_vp1} | {file\_3\_vp2} | {file\_3\_vp3} | {file\_3\_total} | {file\_3\_status} | {file\_3\_remark} |
| {file\_4\_no} | {file\_4\_name} | {file\_4\_vp1} | {file\_4\_vp2} | {file\_4\_vp3} | {file\_4\_total} | {file\_4\_status} | {file\_4\_remark} |
| {file\_5\_no} | {file\_5\_name} | {file\_5\_vp1} | {file\_5\_vp2} | {file\_5\_vp3} | {file\_5\_total} | {file\_5\_status} | {file\_5\_remark} |
| {file\_6\_no} | {file\_6\_name} | {file\_6\_vp1} | {file\_6\_vp2} | {file\_6\_vp3} | {file\_6\_total} | {file\_6\_status} | {file\_6\_remark} |
| {file\_7\_no} | {file\_7\_name} | {file\_7\_vp1} | {file\_7\_vp2} | {file\_7\_vp3} | {file\_7\_total} | {file\_7\_status} | {file\_7\_remark} |
| {file\_8\_no} | {file\_8\_name} | {file\_8\_vp1} | {file\_8\_vp2} | {file\_8\_vp3} | {file\_8\_total} | {file\_8\_status} | {file\_8\_remark} |
| {file\_9\_no} | {file\_9\_name} | {file\_9\_vp1} | {file\_9\_vp2} | {file\_9\_vp3} | {file\_9\_total} | {file\_9\_status} | {file\_9\_remark} |
| {file\_10\_no} | {file\_10\_name} | {file\_10\_vp1} | {file\_10\_vp2} | {file\_10\_vp3} | {file\_10\_total} | {file\_10\_status} | {file\_10\_remark} |
| <mark>**合計**</mark> |  | <mark>**8**</mark> | <mark>**5**</mark> | <mark>**2**</mark> | <mark>**15**</mark> | <mark></mark> | <mark></mark> |

# 工作表：3\_详细明細

> 原序号：3；状态：可见；范围：A1:I25；合并单元格：2 个

## <span style="background-color:#ED7D31"><span style="color:#FFFFFF">**コード検索詳細明細（详细检测结果）**</span></span>

- **A3**：**报告编号：**
- **B3**：OOO-2026-0804-001
- **D3**：**检查观点：**
- **E3**：VP-001 横展開 / VP-002 ハードコード / VP-003 情報漏洩

| <span style="background-color:#FBE5D6"><span style="color:#843C0C">**No.**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**ファイルパス (文件路径)**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**行番号**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**列番号**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**コード内容 (代码片段)**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**该当検査観点**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**重要度**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**要修正**</span></span> | <span style="background-color:#FBE5D6"><span style="color:#843C0C">**修正内容 / コメント**</span></span> |
|---|---|---|---|---|---|---|---|---|
| 1 | src/auth/auth-service.ts | 34 | {detail\_1\_col} | throw new UnauthorizedException(Invalid email or password) | VP-001 横展開 | 中 | はい | 日本語メッセージに変更 |
| 2 | src/auth/auth-service.ts | 43 | {detail\_2\_col} | throw new UnauthorizedException(Invalid password) | VP-001 横展開 | 中 | はい | 日本語メッセージに変更 |
| 3 | src/auth/auth-service.ts | 62 | {detail\_3\_col} | throw new Error(User not found) | VP-001 横展開 | 中 | はい | 日本語化 + メッセージ統一 |
| 4 | src/auth/auth-service.ts | 20 | {detail\_4\_col} | AUTH\_API = http://legacy-auth.internal:9090 | VP-002 ハードコード | 高 | はい | 環境変数 AUTH\_API\_URL へ切り出し |
| 5 | src/auth/auth-service.ts | 51 | {detail\_5\_col} | jwt expiresIn: 30d | VP-002 ハードコード | 低 | 検討中 | jwt.expiresIn config 化 |
| 6 | src/auth/auth-service.ts | 32 | {detail\_6\_col} | logger.debug(..., password=dto.password) | VP-003 情報漏洩 | 重大 | はい | P0 至急 password フィールド出力禁止 |
| 7 | pay/payment-processor.go | 20 | {detail\_7\_col} | dbPassword = P@ym3nt2026#SuperSecure | VP-002 ハードコード | 重大 | はい | P0 Vault / Secret Manager 化 |
| 8 | pay/payment-processor.go | 22 | {detail\_8\_col} | dbHost = prod-db-master.internal | VP-002 ハードコード | 高 | はい | PAY\_DB\_HOST 環境変数化 |
| 9 | pay/payment-processor.go | 90 | {detail\_9\_col} | stripeKey = sk\_live\_abc123xyz | VP-002 ハードコード | 重大 | はい | P0 vault 化必須 |
| 10 | pay/payment-processor.go | 60 | {detail\_10\_col} | log.Printf(\[Charge\] user=.. amount=.. order=.. password\_env=..) | VP-003 情報漏洩 | 重大 | はい | P0 機密・個人情報は一切 log に出さない |
| {detail\_11\_no} | {detail\_11\_file} | {detail\_11\_line} | {detail\_11\_col} | {detail\_11\_code} | {detail\_11\_viewpoint} | {detail\_11\_severity} | {detail\_11\_needfix} | {detail\_11\_comment} |
| {detail\_12\_no} | {detail\_12\_file} | {detail\_12\_line} | {detail\_12\_col} | {detail\_12\_code} | {detail\_12\_viewpoint} | {detail\_12\_severity} | {detail\_12\_needfix} | {detail\_12\_comment} |
| {detail\_13\_no} | {detail\_13\_file} | {detail\_13\_line} | {detail\_13\_col} | {detail\_13\_code} | {detail\_13\_viewpoint} | {detail\_13\_severity} | {detail\_13\_needfix} | {detail\_13\_comment} |
| {detail\_14\_no} | {detail\_14\_file} | {detail\_14\_line} | {detail\_14\_col} | {detail\_14\_code} | {detail\_14\_viewpoint} | {detail\_14\_severity} | {detail\_14\_needfix} | {detail\_14\_comment} |
| {detail\_15\_no} | {detail\_15\_file} | {detail\_15\_line} | {detail\_15\_col} | {detail\_15\_code} | {detail\_15\_viewpoint} | {detail\_15\_severity} | {detail\_15\_needfix} | {detail\_15\_comment} |
| {detail\_16\_no} | {detail\_16\_file} | {detail\_16\_line} | {detail\_16\_col} | {detail\_16\_code} | {detail\_16\_viewpoint} | {detail\_16\_severity} | {detail\_16\_needfix} | {detail\_16\_comment} |
| {detail\_17\_no} | {detail\_17\_file} | {detail\_17\_line} | {detail\_17\_col} | {detail\_17\_code} | {detail\_17\_viewpoint} | {detail\_17\_severity} | {detail\_17\_needfix} | {detail\_17\_comment} |
| {detail\_18\_no} | {detail\_18\_file} | {detail\_18\_line} | {detail\_18\_col} | {detail\_18\_code} | {detail\_18\_viewpoint} | {detail\_18\_severity} | {detail\_18\_needfix} | {detail\_18\_comment} |
| {detail\_19\_no} | {detail\_19\_file} | {detail\_19\_line} | {detail\_19\_col} | {detail\_19\_code} | {detail\_19\_viewpoint} | {detail\_19\_severity} | {detail\_19\_needfix} | {detail\_19\_comment} |
| {detail\_20\_no} | {detail\_20\_file} | {detail\_20\_line} | {detail\_20\_col} | {detail\_20\_code} | {detail\_20\_viewpoint} | {detail\_20\_severity} | {detail\_20\_needfix} | {detail\_20\_comment} |
