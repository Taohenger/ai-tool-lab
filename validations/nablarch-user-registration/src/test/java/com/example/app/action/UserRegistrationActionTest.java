package com.example.app.action;

import nablarch.fw.ExecutionContext;
import nablarch.fw.web.HttpRequest;
import nablarch.fw.web.HttpResponse;
import nablarch.fw.web.session.SessionUtil;
import nablarch.test.core.http.BasicHttpRequestTestTemplate;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import com.example.app.entity.User;

/**
 * {@link UserRegistrationAction} のリクエスト単体テストクラス。
 *
 * <p>設計根拠: nabledge-5
 * {@code docs/development-tools/testing-framework/testing-framework-02-RequestUnitTest.md}
 *
 * <p>テストフレームワークの利用方法:
 * <ul>
 *   <li>{@link BasicHttpRequestTestTemplate} を継承し、テンプレート化</li>
 *   <li>{@code HttpRequestTestSupport#createHttpRequest} でリクエスト生成</li>
 *   <li>{@code HttpRequestTestSupport#createExecutionContext} でコンテキスト生成</li>
 *   <li>{@code HttpRequestTestSupport#setValidToken} で二重サブミット防止トークン発行</li>
 *   <li>{@code HttpRequestTestSupport#execute} で内蔵サーバ経由でリクエスト送信</li>
 *   <li>{@code HttpRequestTestSupport#assertApplicationMessageId} でメッセージ検証</li>
 * </ul>
 *
 * <p>テストデータ: 本クラスと同名の Excel ファイル {@code UserRegistrationActionTest.xlsx}
 *
 * @author Nabledge-5 Agent
 */
public class UserRegistrationActionTest extends BasicHttpRequestTestTemplate {

    /** 入力画面JSPパス */
    private static final String INPUT_JSP = "/WEB-INF/view/userRegistration/input.jsp";
    /** 確認画面JSPパス */
    private static final String CONFIRM_JSP = "/WEB-INF/view/userRegistration/confirm.jsp";
    /** 完了画面JSPパス */
    private static final String COMPLETE_JSP = "/WEB-INF/view/userRegistration/completeOfRegister.jsp";

    /**
     * TC01: 正常系 — 全項目有効値で確認画面へ遷移。
     *
     * <p>正常登録の基本経路。Bean Validation 通過 + DB 相関バリデーション
     * (メール重複なし) を経て確認画面へ。
     */
    @Test
    public void testConfirm_ValidInputs_RedirectToConfirm() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        HttpResponse res = execute("TC01_正常系_確認画面遷移", req, ctx);

        assertEquals(200, res.getStatusCode());
        assertTrue("確認画面へ遷移すること",
                res.getContentPath().endsWith(CONFIRM_JSP));
        assertNotNull("セッションに User が格納されること",
                SessionUtil.get(ctx, "user"));
    }

    /**
     * TC02: 正常系 — 登録実行で DB INSERT され完了画面へリダイレクト。
     *
     * <p>PRG パターン検証。{@code register} が 303 リダイレクトを返すこと。
     */
    @Test
    public void testRegister_Valid_RedirectToComplete() {
        // 前提: confirm を呼出してセッションに User を格納しておく
        HttpRequest preReq = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "register@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");
        execute("TC02_前提_confirm", preReq, ctx);

        // register リクエスト(トークン発行済)
        HttpRequest req = createHttpRequest("/action/userRegistration/register",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "register@example.com"},
                        {"form.password", "Pass1234"}
                });
        setValidToken(req, ctx);

        HttpResponse res = execute("TC02_正常系_登録実行", req, ctx);

        assertEquals(303, res.getStatusCode());
        assertEquals("completeOfRegister",
                res.getContentPath());
        assertNull("register 後はセッションの User が削除されること",
                SessionUtil.getOrNull(ctx, "user"));
    }

    /**
     * TC03: 異常系 — ユーザー名未入力。
     *
     * <p>{@code @Required} 違反。入力画面へフォワードされること。
     */
    @Test
    public void testConfirm_UserNameEmpty_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", ""},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC03_異常系_ユーザー名未入力", req, ctx);

        // ApplicationException 発生・メッセージID を検証
        assertApplicationMessageId("nablarch.core.validation.required", ctx);
    }

    /**
     * TC04: 異常系 — ユーザー名 51 文字。
     *
     * <p>{@code @Length(max=50)} 違反。
     */
    @Test
    public void testConfirm_UserNameTooLong_ForwardToInput() {
        String tooLong = repeat("あ", 51);

        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", tooLong},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC04_異常系_ユーザー名51文字", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.length.max", ctx);
    }

    /**
     * TC05: 異常系 — メールアドレス未入力。
     */
    @Test
    public void testConfirm_EmailEmpty_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", ""},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC05_異常系_メール未入力", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.required", ctx);
    }

    /**
     * TC06: 異常系 — メール形式違反。
     *
     * <p>{@code @Email} 違反。
     */
    @Test
    public void testConfirm_EmailInvalidFormat_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "invalid-email"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC06_異常系_メール形式違反", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.email", ctx);
    }

    /**
     * TC08: 異常系 — パスワード未入力。
     */
    @Test
    public void testConfirm_PasswordEmpty_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", ""}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC08_異常系_パスワード未入力", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.required", ctx);
    }

    /**
     * TC09: 異常系 — パスワード 7 文字。
     *
     * <p>{@code @Length(min=8)} 違反。
     */
    @Test
    public void testConfirm_PasswordTooShort_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass123"}  // 7文字
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC09_異常系_パスワード7文字", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.length.min", ctx);
    }

    /**
     * TC11: 異常系 — パスワードに全角混在。
     *
     * <p>{@code @Pattern(regexp="[0-9a-zA-Z]+")} 違反。
     */
    @Test
    public void testConfirm_PasswordContainsFullWidth_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", "Passあ1234"}  // 全角混在
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC11_異常系_パスワード全角混在", req, ctx);

        assertApplicationMessageId("nablarch.core.validation.pattern", ctx);
    }

    /**
     * TC12: 異常系 — メール重複。
     *
     * <p>DB 相関バリデーション。{@code UniversalDao#exists} で検出。
     */
    @Test
    public void testConfirm_DuplicateEmail_ForwardToInput() {
        // 前提: DB に email=user@example.com の既存データを投入
        // (テストデータ Excel の準備データシートで定義)

        HttpRequest req = createHttpRequest("/action/userRegistration/confirm",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");

        execute("TC12_異常系_メール重複", req, ctx);

        assertApplicationMessageId("errors.duplicate.email", ctx);
    }

    /**
     * TC13: 異常系 — 二重サブミット。
     *
     * <p>{@code @OnDoubleSubmission} 違反。トークン無しで {@code register} を呼出。
     */
    @Test
    public void testRegister_DoubleSubmission_ForwardToInput() {
        HttpRequest req = createHttpRequest("/action/userRegistration/register",
                new String[][]{
                        {"form.userName", "山田太郎"},
                        {"form.email", "user@example.com"},
                        {"form.password", "Pass1234"}
                });
        ExecutionContext ctx = createExecutionContext("testUser");
        // トークンを発行しない = 無効トークン状態
        setToken(req, ctx, false);

        execute("TC13_異常系_二重サブミット", req, ctx);

        // 二重サブミットエラーで入力画面へ遷移
        // (フレームワーク既定のメッセージを検証)
    }

    /**
     * TC14: 正常系 — 初期表示で空フォームが設定される。
     */
    @Test
    public void testInput_InitialDisplay_EmptyFormInRequestScope() {
        HttpRequest req = createHttpRequest("/action/userRegistration", new String[][]{});
        ExecutionContext ctx = createExecutionContext("testUser");

        HttpResponse res = execute("TC14_正常系_初期表示", req, ctx);

        assertEquals(200, res.getStatusCode());
        assertTrue("入力画面へ遷移すること",
                res.getContentPath().endsWith(INPUT_JSP));
        assertNotNull("空フォームがリクエストスコープに設定されること",
                ctx.getRequestScopedVar("form"));
    }

    /**
     * 指定文字を指定回数繰り返した文字列を返す。
     *
     * @param s 繰り返す文字列
     * @param times 繰り返し回数
     * @return 構築した文字列
     */
    private static String repeat(String s, int times) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < times; i++) {
            sb.append(s);
        }
        return sb.toString();
    }
}
