package com.example.app.form;

import java.io.Serializable;

import nablarch.core.validation.ee.Email;
import nablarch.core.validation.ee.Length;
import nablarch.core.validation.ee.Pattern;
import nablarch.core.validation.ee.Required;
import nablarch.core.validation.ee.Domain;

/**
 * ユーザー登録画面の入力値を受け付けるフォーム。
 *
 * <p>設計根拠: nabledge-5
 * {@code docs/processing-pattern/web-application/web-application-getting-started-project-update.md}
 * の {@code ProjectUpdateForm} パターン。
 *
 * <p>※ {@code @InjectForm} によりリクエストパラメータから注入される。
 * ※ セッションには直接格納せず、Entity に詰め替えて {@link nablarch.core.db.transaction.SessionUtil} へ格納する。
 *
 * @author Nabledge-5 Agent
 */
public class UserRegistrationForm implements Serializable {

    /** シリアルバージョンUID */
    private static final long serialVersionUID = 1L;

    /** ユーザー名 (必須・50 文字以内) */
    @Required
    @Length(max = 50)
    @Domain("userName")
    private String userName;

    /** メールアドレス (必須・Email 形式・254 文字以内) */
    @Required
    @Email
    @Length(max = 254)
    @Domain("email")
    private String email;

    /** パスワード (必須・8 文字以上 100 文字以下・半角英数字のみ) */
    @Required
    @Length(min = 8, max = 100)
    @Pattern(regexp = "[0-9a-zA-Z]+")
    @Domain("password")
    private String password;

    /** デフォルトコンストラクタ。 */
    public UserRegistrationForm() {
    }

    /**
     * ユーザー名を取得する。
     *
     * @return ユーザー名
     */
    public String getUserName() {
        return userName;
    }

    /**
     * ユーザー名を設定する。
     *
     * @param userName 設定するユーザー名
     */
    public void setUserName(String userName) {
        this.userName = userName;
    }

    /**
     * メールアドレスを取得する。
     *
     * @return メールアドレス
     */
    public String getEmail() {
        return email;
    }

    /**
     * メールアドレスを設定する。
     *
     * @param email 設定するメールアドレス
     */
    public void setEmail(String email) {
        this.email = email;
    }

    /**
     * パスワードを取得する。
     *
     * @return パスワード
     */
    public String getPassword() {
        return password;
    }

    /**
     * パスワードを設定する。
     *
     * @param password 設定するパスワード
     */
    public void setPassword(String password) {
        this.password = password;
    }
}
