package com.example.app.entity;

import java.sql.Timestamp;

import nablarch.common.dao.Entity;
import nablarch.common.dao.Id;
import nablarch.common.dao.Table;
import nablarch.common.dao.Version;

/**
 * USERS テーブルに対応するエンティティクラス。
 *
 * <p>設計根拠: nabledge-5
 * {@code docs/component/libraries/libraries-universal-dao.md} の
 * JPA アノテーション規約。
 *
 * <p>※ {@link nablarch.common.dao.UniversalDao#insert(Object)} で INSERT される。
 * ※ USER_ID は {@code SEQ_USER_ID} から採番される。
 * ※ VERSION は楽観ロック用(更新機能追加時に使用)。
 *
 * @author Nabledge-5 Agent
 */
@Table(name = "USERS")
public class User implements Entity {

    /** シリアルバージョンUID */
    private static final long serialVersionUID = 1L;

    /** ユーザーID (PK) */
    @Id
    private Long userId;

    /** ユーザー名 */
    private String userName;

    /** メールアドレス (Unique) */
    private String email;

    /** パスワード */
    private String password;

    /** 楽観ロック用バージョン番号 */
    @Version
    private Long version;

    /** 登録日時 */
    private Timestamp registeredAt;

    /** デフォルトコンストラクタ。 */
    public User() {
    }

    /**
     * ユーザーIDを取得する。
     *
     * @return ユーザーID
     */
    public Long getUserId() {
        return userId;
    }

    /**
     * ユーザーIDを設定する。
     *
     * @param userId 設定するユーザーID
     */
    public void setUserId(Long userId) {
        this.userId = userId;
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

    /**
     * バージョン番号を取得する。
     *
     * @return バージョン番号
     */
    public Long getVersion() {
        return version;
    }

    /**
     * バージョン番号を設定する。
     *
     * @param version 設定するバージョン番号
     */
    public void setVersion(Long version) {
        this.version = version;
    }

    /**
     * 登録日時を取得する。
     *
     * @return 登録日時
     */
    public Timestamp getRegisteredAt() {
        return registeredAt;
    }

    /**
     * 登録日時を設定する。
     *
     * @param registeredAt 設定する登録日時
     */
    public void setRegisteredAt(Timestamp registeredAt) {
        this.registeredAt = registeredAt;
    }
}
