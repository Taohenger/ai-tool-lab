package com.example.app.action;

import nablarch.common.dao.UniversalDao;
import nablarch.common.web.interceptor.InjectForm;
import nablarch.common.web.token.OnDoubleSubmission;
import nablarch.core.beans.BeanUtil;
import nablarch.core.message.MessageLevel;
import nablarch.core.message.MessageUtil;
import nablarch.core.util.StringUtil;
import nablarch.fw.ExecutionContext;
import nablarch.fw.web.HttpRequest;
import nablarch.fw.web.HttpResponse;
import nablarch.fw.web.session.SessionUtil;
import nablarch.core.validation.ee.Validator;
import nablarch.common.dao.NoDataException;

import com.example.app.entity.User;
import com.example.app.form.UserRegistrationForm;

/**
 * ユーザー登録機能の業務アクションクラス。
 *
 * <p>設計根拠: nabledge-5
 * <ul>
 *   <li>{@code docs/processing-pattern/web-application/web-application-getting-started-project-update.md}
 *       (Form/Action/SessionUtil/UniversalDao/リダイレクト・PRG パターン)</li>
 *   <li>{@code docs/processing-pattern/web-application/web-application-client-create1.md}
 *       (初期表示・UniversalDao#findAll・リクエストスコープ)</li>
 *   <li>{@code docs/component/libraries/libraries-bean-validation.md}
 *       (DB 相関バリデーション: UniversalDao#exists + ApplicationException)</li>
 * </ul>
 *
 * <p>ルーティング(routes.xml):
 * <pre>
 *   GET  /action/userRegistration            → input
 *   POST /action/userRegistration/confirm    → confirm
 *   POST /action/userRegistration/register   → register
 *   GET  /action/userRegistration/complete   → completeOfRegister
 * </pre>
 *
 * @author Nabledge-5 Agent
 */
public class UserRegistrationAction {

    /** 入力画面JSPパス */
    private static final String INPUT_JSP = "/WEB-INF/view/userRegistration/input.jsp";
    /** 確認画面JSPパス */
    private static final String CONFIRM_JSP = "/WEB-INF/view/userRegistration/confirm.jsp";
    /** 完了画面JSPパス */
    private static final String COMPLETE_JSP = "/WEB-INF/view/userRegistration/completeOfRegister.jsp";
    /** セッション格納キー(User Entity) */
    private static final String SESSION_KEY_USER = "user";

    /**
     * 入力画面を初期表示する。
     *
     * @param request HTTP リクエスト
     * @param context 実行コンテキスト
     * @return 入力画面へのフォワード
     */
    public HttpResponse input(HttpRequest request, ExecutionContext context) {
        // 入力値をクリアして空フォームをリクエストスコープに設定
        context.setRequestScopedVar("form", new UserRegistrationForm());
        return new HttpResponse(INPUT_JSP);
    }

    /**
     * 入力値をバリデーションし、確認画面を表示する。
     *
     * <p>Bean Validation + DB 相関バリデーション(メール重複)を実施。
     * エラー時は入力画面へフォワード。
     *
     * @param request HTTP リクエスト
     * @param context 実行コンテキスト
     * @return 確認画面または入力画面(エラー時)へのフォワード
     */
    @InjectForm(form = UserRegistrationForm.class, prefix = "form")
    @OnError(type = nablarch.common.message.ApplicationException.class, path = INPUT_JSP)
    public HttpResponse confirm(HttpRequest request, ExecutionContext context) {
        UserRegistrationForm form = context.getRequestScopedVar("form");

        // DB 相関バリデーション: メールアドレス重複チェック
        // (nabledge-5 libraries-bean-validation.md#データベースとの相関バリデーションを行う)
        if (!StringUtil.isNullOrEmpty(form.getEmail())) {
            if (UniversalDao.exists(User.class, "FIND_BY_EMAIL",
                    new Object[]{form.getEmail()})) {
                throw new nablarch.common.message.ApplicationException(
                        MessageUtil.createMessage(MessageLevel.ERROR,
                                "errors.duplicate.email", form.getEmail()));
            }
        }

        // Form の値を Entity に詰め替えてセッションへ格納
        // (Form を直接セッションに入れない指針: web-application-getting-started-project-update.md)
        User user = BeanUtil.createAndCopy(User.class, form);
        SessionUtil.put(context, SESSION_KEY_USER, user);

        // 出力情報をリクエストスコープにセット
        context.setRequestScopedVar("form", form);

        return new HttpResponse(CONFIRM_JSP);
    }

    /**
     * DB へ登録し、完了画面へリダイレクトする。
     *
     * <p>二重サブミット防止のため {@link OnDoubleSubmission} を付与。
     * ブラウザ更新での再実行を防ぐため PRG パターンでリダイレクト。
     *
     * @param request HTTP リクエスト
     * @param context 実行コンテキスト
     * @return 完了画面へのリダイレクト(303)
     */
    @InjectForm(form = UserRegistrationForm.class, prefix = "form")
    @OnDoubleSubmission
    @OnError(type = nablarch.common.message.ApplicationException.class, path = INPUT_JSP)
    public HttpResponse register(HttpRequest request, ExecutionContext context) {
        // セッションから Entity を取得
        User user = SessionUtil.delete(context, SESSION_KEY_USER);

        // ユーザーIDを採番して INSERT
        // (UniversalDao#insert が自動的に SEQ_USER_ID を採番して INSERT する)
        UniversalDao.insert(user);

        // PRG パターン: 303 リダイレクトで完了画面へ
        return new HttpResponse(303, "redirect://completeOfRegister");
    }

    /**
     * 完了画面を表示する。
     *
     * <p>{@code register} メソッドからのリダイレクト着地。
     *
     * @param request HTTP リクエスト
     * @param context 実行コンテキスト
     * @return 完了画面へのフォワード
     */
    public HttpResponse completeOfRegister(HttpRequest request, ExecutionContext context) {
        return new HttpResponse(COMPLETE_JSP);
    }
}
