#!/usr/bin/env bash
# OfficeCLI の set コマンドを逐次発行してレポートを埋める
set -euo pipefail

export PATH="$HOME/.officecli/bin:$PATH"
cd /workspace/validations/office-cli

TEMPLATE=test-data/template-demo/横展开报告模板.xlsx
REPORT=test-data/template-demo/横展开报告-完成版.xlsx
EVIDENCE=results/evidence/008-template-report

rm -f "$REPORT"
cp "$TEMPLATE" "$REPORT"

LOG=$EVIDENCE/tc003-006-sets.txt
: > "$LOG"

run() {
  echo ">>> $*" >> "$LOG"
  officecli "$@" >> "$LOG" 2>&1
  echo "    exit=$?" >> "$LOG"
}

# ============ TC-003 Sheet1 レポート基本情報 ============
run set "$REPORT" /1_横展开报告/B3  --prop value="OOO-2026-0804-001"
run set "$REPORT" /1_横展开报告/E3  --prop value="2026-08-04"

run set "$REPORT" /1_横展开报告/A6  \
  --prop 'value=チーム共通の問題（エラーメッセージ横展開漏れ・ハードコード・機密情報出力）に対し、認証/決済サービスの横展開調査を実施し、是正箇所を明らかにする。'

run set "$REPORT" /1_横展开报告/B9  --prop value="feature/auth-enterprise, feature/payment-v2"
run set "$REPORT" /1_横展开报告/B10 --prop value="a8f3c91e, 4d7b2250"

run set "$REPORT" /1_横展开报告/B13 --prop value="2026-08-04 09:30"
run set "$REPORT" /1_横展开报告/E13 --prop value="2026-08-04 14:15"
run set "$REPORT" /1_横展开报告/B14 --prop value="4.5"

run set "$REPORT" /1_横展开报告/A17 \
  --prop 'value=Step1: 検査観点 3 項目を定義 → Step2: CloudCode Agent が対象コードに grep/regex → Step3: 該当箇所を Sheet2/Sheet3 に自動集計 → Step4: 結論を Sheet1 に記載。'

run set "$REPORT" /1_横展开报告/B26 --prop value="2"
run set "$REPORT" /1_横展开报告/B27 --prop value="15"
run set "$REPORT" /1_横展开报告/B28 --prop value="12"
run set "$REPORT" /1_横展开报告/E28 --prop value="要対応" --prop bold=true --prop font.color=C00000
run set "$REPORT" /1_横展开报告/B29 \
  --prop 'value=全体として横展開（日本語化）・ハードコード・情報漏洩いずれも該当箇所が検出された。特に payment-processor.go の DB パスワードハードコードと auth-service.ts のパスワードログ出力は P0 として今週中の修正必須。'

run set "$REPORT" /1_横展开报告/B32 --prop value="Taohenger（開発チーム）"
run set "$REPORT" /1_横展开报告/E32 --prop value="（承認待ち）"

# ============ TC-004 Sheet1 検査観点表 ============
run set "$REPORT" /1_横展开报告/B21 --prop value="横展開（日本語化）"
run set "$REPORT" /1_横展开报告/C21 --prop value="エラーメッセージ・コメントの日本語化漏れチェック"
run set "$REPORT" /1_横展开报告/D21 --prop value="高 (P1)"
run set "$REPORT" /1_横展开报告/B22 --prop value="ハードコード確認"
run set "$REPORT" /1_横展开报告/C22 --prop value="DB/API/Secret の直埋め込み検出"
run set "$REPORT" /1_横展开报告/D22 --prop value="高 (P1)"
run set "$REPORT" /1_横展开报告/B23 --prop value="情報漏洩チェック"
run set "$REPORT" /1_横展开报告/C23 --prop value="ログ/標準出力への機密情報出力検出"
run set "$REPORT" /1_横展开报告/D23 --prop value="高 (P1)"

# ============ TC-005 Sheet2 モニタリング一覧 ============
run set "$REPORT" /2_监测一览/B3 --prop value="OOO-2026-0804-001"
run set "$REPORT" /2_监测一览/E3 --prop value="feature/auth, feature/pay"
run set "$REPORT" /2_监测一览/H3 --prop value="2026-08-04"

run set "$REPORT" /2_监测一览/A6 --prop value="1"
run set "$REPORT" /2_监测一览/B6 --prop value="auth-service.ts"
run set "$REPORT" /2_监测一览/C6 --prop value="4"
run set "$REPORT" /2_监测一览/D6 --prop value="2"
run set "$REPORT" /2_监测一览/E6 --prop value="1"
run set "$REPORT" /2_监测一览/F6 --prop value="7"
run set "$REPORT" /2_监测一览/G6 --prop value="要修正"
run set "$REPORT" /2_监测一览/H6 --prop value="P0: パスワードログ出力あり"

run set "$REPORT" /2_监测一览/A7 --prop value="2"
run set "$REPORT" /2_监测一览/B7 --prop value="payment-processor.go"
run set "$REPORT" /2_监测一览/C7 --prop value="4"
run set "$REPORT" /2_监测一览/D7 --prop value="3"
run set "$REPORT" /2_监测一览/E7 --prop value="1"
run set "$REPORT" /2_监测一览/F7 --prop value="8"
run set "$REPORT" /2_监测一览/G7 --prop value="要修正"
run set "$REPORT" /2_监测一览/H7 --prop value="P0: DBパスワード直埋め込み"

run set "$REPORT" /2_监测一览/C16 --prop value="8"
run set "$REPORT" /2_监测一览/D16 --prop value="5"
run set "$REPORT" /2_监测一览/E16 --prop value="2"
run set "$REPORT" /2_监测一览/F16 --prop value="15"

# ============ TC-006 Sheet3 詳細明細 ============
run set "$REPORT" /3_详细明細/B3 --prop value="OOO-2026-0804-001"
run set "$REPORT" /3_详细明細/E3 --prop 'value=VP-001 横展開 / VP-002 ハードコード / VP-003 情報漏洩'

# 10 件詳細
d(){
  local no=$1 f=$2 l=$3 code=$4 vp=$5 sev=$6 fix=$7 cmt=$8
  run set "$REPORT" "/3_详细明細/A$((5+no))" --prop value="$no"
  run set "$REPORT" "/3_详细明細/B$((5+no))" --prop value="$f"
  run set "$REPORT" "/3_详细明細/C$((5+no))" --prop value="$l"
  run set "$REPORT" "/3_详细明細/E$((5+no))" --prop value="$code"
  run set "$REPORT" "/3_详细明細/F$((5+no))" --prop value="$vp"
  run set "$REPORT" "/3_详细明細/G$((5+no))" --prop value="$sev"
  run set "$REPORT" "/3_详细明細/H$((5+no))" --prop value="$fix"
  run set "$REPORT" "/3_详细明細/I$((5+no))" --prop value="$cmt"
}

d 1 "src/auth/auth-service.ts"   34 "throw new UnauthorizedException(Invalid email or password)" "VP-001 横展開" "中" "はい" "日本語メッセージに変更"
d 2 "src/auth/auth-service.ts"   43 "throw new UnauthorizedException(Invalid password)"            "VP-001 横展開" "中" "はい" "日本語メッセージに変更"
d 3 "src/auth/auth-service.ts"   62 "throw new Error(User not found)"                                  "VP-001 横展開" "中" "はい" "日本語化 + メッセージ統一"
d 4 "src/auth/auth-service.ts"   20 "AUTH_API = http://legacy-auth.internal:9090"                     "VP-002 ハードコード" "高" "はい" "環境変数 AUTH_API_URL へ切り出し"
d 5 "src/auth/auth-service.ts"   51 "jwt expiresIn: 30d"                                               "VP-002 ハードコード" "低" "検討中" "jwt.expiresIn config 化"
d 6 "src/auth/auth-service.ts"   32 "logger.debug(..., password=dto.password)"                         "VP-003 情報漏洩" "重大" "はい" "P0 至急 password フィールド出力禁止"
d 7 "pay/payment-processor.go"   20 "dbPassword = P@ym3nt2026#SuperSecure"                            "VP-002 ハードコード" "重大" "はい" "P0 Vault / Secret Manager 化"
d 8 "pay/payment-processor.go"   22 "dbHost = prod-db-master.internal"                                 "VP-002 ハードコード" "高" "はい" "PAY_DB_HOST 環境変数化"
d 9 "pay/payment-processor.go"   90 "stripeKey = sk_live_abc123xyz"                                    "VP-002 ハードコード" "重大" "はい" "P0 vault 化必須"
d 10 "pay/payment-processor.go"  60 "log.Printf([Charge] user=.. amount=.. order=.. password_env=..)"  "VP-003 情報漏洩" "重大" "はい" "P0 機密・個人情報は一切 log に出さない"

officecli save "$REPORT" >> "$LOG" 2>&1
echo "" >> "$LOG"
echo "✅ 全 set 完了 $(date +%T)" >> "$LOG"
echo "log size: $(wc -l < $LOG) lines"
tail -5 "$LOG"
