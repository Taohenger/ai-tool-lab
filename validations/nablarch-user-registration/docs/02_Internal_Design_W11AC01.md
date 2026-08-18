# ユーザー登録機能 内部設計書 (W11AC01)

| 項目 | 値 |
|------|----|
| 画面ID | W11AC01 |
| 機能名 | ユーザー登録 |
| 対象フレームワーク | Nablarch 5 |
| 設計根拠 | nabledge-5 `web-application-getting-started-project-update.md` / `web-application-application-design.md` |
| 版数 | 1.0 |

---

## 1. 責務配置 (アーキテクチャ)

> nabledge-5 `web-application-application-design.md#アプリケーションの責務配置` に準拠。

```
[Browser]
   │ HTTP (POST/GET)
   ▼
[Action]  UserRegistrationAction       ← HTTP 受付・Form 取出・遷移制御
   │
   ├─► [Form]   UserRegistrationForm   ← 入力値保持・Bean Validation
   │
   ├─► [Entity] User                    ← DB 永続化用 Entity
   │
   └─► [DAO]   UniversalDao            ← 汎用 DAO (SQL ファイル駆動)
                  │
                  ▼
              [SQL File] UserRegistration.sql
                  │
                  ▼
              [DB] USERS テーブル
```

### 責務分離の原則
- **Form は 1 画面単位で作成**(`web-application-application-design.md` 推奨)。入力確認をまたぐ値受け渡しは Form をセッションに直接入れず、Entity に詰め替えて `SessionUtil` へ格納(`web-application-getting-started-project-update.md` 参照)。
- **DB 相関バリデーション**(メール重複)は Action 内に記述(`libraries-bean-validation.md#データベースとの相関バリデーションを行う`)。
- **楽観的ロック不要**:本機能は新規登録のため `@Version` は付与しない(更新時のみ必須)。

---

## 2. クラス設計

### 2.1 UserRegistrationForm (Form)

| 項目 | 内容 |
|------|------|
| パッケージ | `com.example.app.form` |
| 役割 | 入力画面から POST された値を受取・Bean Validation |
| 継承 | `Serializable` 実装 |
| ライフサイクル | リクエストスコープ(`@InjectForm` で注入) |

### 2.2 UserRegistrationAction (Action)

| 項目 | 内容 |
|------|------|
| パッケージ | `com.example.app.action` |
| 役割 | HTTP リクエスト受付・Form 注入・バリデーション・DB 登録・画面遷移 |
| メソッド一覧 | 下表 |

| メソッド | HTTP | URI | 役割 | アノテーション |
|----------|------|-----|------|-----------------|
| `input` | GET | `/action/userRegistration` | 入力画面初期表示 | - |
| `confirm` | POST | `/action/userRegistration/confirm` | バリデーション + 確認画面表示 | `@InjectForm` + `@OnError` |
| `register` | POST | `/action/userRegistration/register` | DB 登録 + 完了画面へリダイレクト | `@InjectForm` + `@OnDoubleSubmission` |
| `completeOfRegister` | GET | `/action/userRegistration/complete` | 完了画面表示 (PRG 着地) | - |

### 2.3 User (Entity)

| 項目 | 内容 |
|------|------|
| パッケージ | `com.example.app.entity` |
| 役割 | USERS テーブルとのマッピング |
| 永続化 | `UniversalDao.insert(User.class, entity)` |

### 2.4 UserRegistration.sql (SQL ファイル)

| 項目 | 内容 |
|------|------|
| パス | `src/main/resources/com/example/app/entity/UserRegistration.sql` |
| 役割 | UniversalDao が名前付き SQL として読込 |
| 格納ルール | `ユニバーサルDAO#findBySqlFile` / `#insert` 等が SQL ファイル内の `NAME = <SQL>` 形式エントリを検索 |

---

## 3. 画面項目定義 (→ 02_Screen_Item_List.csv)

> この表は `02_Screen_Item_List.csv` と同内容。CSV は Excel 設計書「項目定義」Sheet へ灌入する。

| No | 画面ID | 項目名 (論理名) | 物理名 | Java型 | 桁数 | 精査ルール (Validation) |
|----|--------|-----------------|--------|--------|------|--------------------------|
| 1 | W11AC01 | ユーザー名 | userName | String | 50 | @Required + @Length(max=50) + @Domain("userName") |
| 2 | W11AC01 | メールアドレス | email | String | 254 | @Required + @Email + @Length(max=254) + @Domain("email") |
| 3 | W11AC01 | パスワード | password | String | 100 | @Required + @Length(min=8, max=100) + @Pattern(regexp="[0-9a-zA-Z]+") + @Domain("password") |

### Entity 側の項目定義 (USERS テーブル)

| No | カラム名 | Java型 | DB 型 | 桁数 | 備考 |
|----|----------|--------|-------|------|------|
| 1 | USER_ID | Long | NUMBER | 19 | PK / 採番は `UniversalDao#sequence` 経由で SEQ_USER_ID 採番 |
| 2 | USER_NAME | String | VARCHAR2 | 50 | Not Null |
| 3 | EMAIL | String | VARCHAR2 | 254 | Not Null / Unique |
| 4 | PASSWORD | String | VARCHAR2 | 100 | Not Null / 平文(本件ではデモ簡略化。実運用は PBKDF2PasswordEncryptor 参照) |
| 5 | VERSION | Long | NUMBER | 19 | 楽観ロック用(更新機能追加時に使用) |
| 6 | REGISTERED_AT | Timestamp | TIMESTAMP | - | 登録日時(デフォルト SYSTIMESTAMP) |

---

## 4. SQL テンプレート (UserRegistration.sql)

> nabledge-5 `web-application-getting-started-project-update.md#SQLの作成` の `NAME = SELECT ...` 形式を踏襲。

```sql
-- メールアドレス重複チェック (DB 相関バリデーション用)
-- 呼出元: UniversalDao.exists(User.class, "FIND_BY_EMAIL", new Object[]{email})
FIND_BY_EMAIL =
SELECT
    USER_ID,
    USER_NAME,
    EMAIL
FROM
    USERS
WHERE
    EMAIL = :email

-- 新規登録
-- 呼出元: UniversalDao.insert(userEntity)
-- (UniversalDao#insert は Entity のプロパティから自動的に INSERT 文を生成するため、
--   SQL ファイルに INSERT 文を明示的に書く必要はない。以下は参考として掲載)
INSERT_USER =
INSERT INTO USERS (
    USER_ID,
    USER_NAME,
    EMAIL,
    PASSWORD,
    VERSION,
    REGISTERED_AT
) VALUES (
    :userId,
    :userName,
    :email,
    :password,
    :version,
    :registeredAt
)

-- 採番 (ユーザーID 発番)
-- UniversalDao#sequence(User.class, "SEQ_USER_ID") の呼出で使用されるシーケンス名
-- (設定は app.xml の <daoConfiguration> に基づく)
-- SEQ_USER_ID:
--   シーケンスオブジェクト(Oracle: SEQUENCE, PostgreSQL: SEQUENCE, H2: SELECT NEXTVAL('SEQ_USER_ID'))
```

### SQL ファイルの配置ルール

- ファイルパスは **Entity と同一パッケージ + Entity クラス名 + `.sql`** が既定。
  - 例:`com.example.app.entity.User` → `src/main/resources/com/example/app/entity/User.sql`
- 本件では Action から `UniversalDao.exists(User.class, "FIND_BY_EMAIL", ...)` を呼ぶため、`User.sql` に `FIND_BY_EMAIL` を定義する。
- INSERT は `UniversalDao#insert(entity)` で自動生成されるため、明示 SQL 不要(上記 `INSERT_USER` は参考用途)。

> **備考**:本検証では SQL ファイル名を `UserRegistration.sql` とするか `User.sql` とするかは運用規約による。nabledge-5 既定では Entity クラス名ベース(`User.sql`)が推奨。Phase 2.3 のコード生成では `User.sql` を採用する。

---

## 5. シーケンス設計

| シーケンス名 | 用途 | 初期値 / 増分 |
|--------------|------|---------------|
| `SEQ_USER_ID` | USER_ID 採番 | 1 / 1 |

`app.xml` の `<daoConfiguration>` で `UniversalDao` が `UniversalDao#sequence(User.class, "SEQ_USER_ID")` を呼んだ際に採番する。

---

## 6. バリデーション戦略

| レイヤ | 検査内容 | 実装方式 |
|--------|----------|----------|
| 単項目 | 必須・桁数・形式 | Bean Validation アノテーション(`@Required`/`@Length`/`@Email`/`@Pattern`/`@Domain`) |
| 項目相関 | (本件では該当なし) | - |
| DB 相関 | メールアドレス重複 | Action 内で `UniversalDao#exists` を呼出し `ApplicationException` 送出 |

### DB 相関バリデーションの実装位置

`confirm` メソッド内で実装(`web-application-getting-started-project-update.md` の顧客存在確認パターンを踏襲)。

```java
if (UniversalDao.exists(User.class, "FIND_BY_EMAIL",
        new Object[]{form.getEmail()})) {
    throw new ApplicationException(
        MessageUtil.createMessage(MessageLevel.ERROR,
            "errors.duplicate.email", form.getEmail()));
}
```

---

## 7. トランザクション設計

| 項目 | 設定 |
|------|------|
| 制御方式 | フレームワーク宣言的(`TransactionManagementHandler` が担当) |
| トランザクション開始 | リクエスト開始時 |
| コミット | `register` メソッド正常終了時 |
| ロールバック | `ApplicationException` / `RuntimeException` 発生時 |
| 単位 | 1 リクエスト = 1 トランザクション |

> nabledge-5 `javadoc-nablarch-common-handler-TransactionManagementHandler.md` 参照。

---

## 8. セッション利用

| キー | 格納内容 | 格納タイミング | 削除タイミング |
|------|----------|----------------|----------------|
| `user` | User Entity(入力値詰替) | `confirm` メソッド正常終了時 | `register` 開始時(`SessionUtil#delete`) |

> Form を直接セッションに格納しない点は `web-application-getting-started-project-update.md` の指針通り。

---

## 9. 参照した nabledge-5 知識資産

| 資産パス | 用途 |
|----------|------|
| `docs/processing-pattern/web-application/web-application-application-design.md` | 責務配置原則 |
| `docs/processing-pattern/web-application/web-application-getting-started-project-update.md` | Form/Action/SessionUtil/UniversalDao パターン・SQL ファイル形式 |
| `docs/component/libraries/libraries-universal-dao.md`(参照) | Entity/楽観ロック/SQL ファイル規約 |
| `docs/component/libraries/libraries-bean-validation.md`(参照) | DB 相関バリデーション戦略 |
| `docs/component/libraries/libraries-session-store.md`(参照) | セッション利用指針 |
