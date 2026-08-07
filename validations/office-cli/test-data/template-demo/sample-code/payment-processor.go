// ========================================================================
// 示例代码 2: payment-processor.go (決済処理 - 模擬横展開検査対象)
// ========================================================================
// 注意：このファイルは Office CLI 横展開レポートのデモ用です。
// 意図的に「問題」を含め、テンプレートの記入例を示しています。

package payment

import (
	"context"
	"database/sql"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

// ▶ Viewpoint 2 該当: 接続情報がハードコード (严重!)
var (
	dbHost     = "prod-db-master.internal"
	dbPort     = 3306
	dbUser     = "payapp"
	dbPassword = "P@ym3nt2026#SuperSecure"
	dbName     = "payments"
)

type PaymentProcessor struct {
	db *sql.DB
}

func NewProcessor() (*PaymentProcessor, error) {
	// ▶ Viewpoint 2 該当: パスワードを平文で DSN 構築
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?parseTime=true",
		dbUser, dbPassword, dbHost, dbPort, dbName)

	db, err := sql.Open("mysql", dsn)
	if err != nil {
		return nil, fmt.Errorf("open db failed: %w", err)
	}
	return &PaymentProcessor{db: db}, nil
}

func (p *PaymentProcessor) Charge(ctx context.Context, userID int64, amountJPY int, orderID string) error {
	// ▶ Viewpoint 3 該当: 機密情報 (金額/ユーザID/注文ID) がそのまま標準ログ
	log.Printf("[Charge] user=%d amount=%d order=%s password_env=%s\n",
		userID, amountJPY, orderID, os.Getenv("STRIPE_SECRET"))

	if amountJPY <= 0 {
		// ▶ Viewpoint 1 該当: エラーメッセージの横展開（日本語化）漏れ
		return fmt.Errorf("invalid amount")
	}

	tx, err := p.db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("begin tx: %w", err)
	}
	defer func() {
		if p := recover(); p != nil {
			_ = tx.Rollback()
			panic(p)
		}
	}()

	// ▶ Viewpoint 1 該当: SQL コメントが横展開されていない
	// ▶ Viewpoint 3 該当: SQL Injection の可能性（文字列結合）
	q := strings.Builder{}
	q.WriteString("INSERT INTO tx_log (user_id, amount, order_id, status, created_at) VALUES (")
	q.WriteString(fmt.Sprintf("%d, %d, '%s', 'pending', NOW())", userID, amountJPY, orderID))

	if _, err := tx.ExecContext(ctx, q.String()); err != nil {
		_ = tx.Rollback()
		// ▶ Viewpoint 1 該当: エラー横展開漏れ
		return fmt.Errorf("insert tx_log failed: %s", err.Error())
	}

	// ▶ Viewpoint 2 該当: 外部 API URL/キーがハードコード
	stripeEndpoint := "https://api.stripe.com/v1/charges"
	stripeKey := "sk_live_abc123xyz_ReplaceWithRealOne"
	_ = stripeEndpoint
	_ = stripeKey

	// 実際の API 呼び出しは省略

	if err := tx.Commit(); err != nil {
		// ▶ Viewpoint 1 該当: エラー横展開漏れ
		return fmt.Errorf("commit failed: %s", err.Error())
	}

	// ▶ Viewpoint 3 該当: 決済成功情報を平文で stdout 出力
	fmt.Printf("[OK] order=%s charged %d JPY at %s\n",
		orderID, amountJPY, time.Now().Format(time.RFC3339))

	return nil
}
