=====================================================================
# Entity: com.example.app.entity.User
# Table: USERS
#
# 設計根拠: nabledge-5
#   - docs/processing-pattern/web-application/web-application-getting-started-project-update.md#SQLの作成
#   - docs/component/libraries/libraries-universal-dao.md (SQL ファイル規約)
#
# UniversalDao 規約:
#   - ファイルパス = src/main/resources/<Entityパッケージ>/<Entity名>.sql
#   - 書式: <SQL名> = <SQL文>
#   - 呼出: UniversalDao.findBySqlFile(<Entity>.class, "<SQL名>", params)
#           UniversalDao.exists(<Entity>.class, "<SQL名>", params)
#
# INSERT は UniversalDao#insert(entity) が自動生成するため、本ファイルには
# SELECT 系のみを定義する。
=====================================================================

# ---------------------------------------------------------------------
# メールアドレス重複チェック (DB 相関バリデーション用)
# 呼出元: UserRegistrationAction#confirm
#         UniversalDao.exists(User.class, "FIND_BY_EMAIL", new Object[]{email})
# 戻り値: 重複行が存在すれば true → ApplicationException 送出
# ---------------------------------------------------------------------
FIND_BY_EMAIL =
SELECT
    USER_ID,
    USER_NAME,
    EMAIL
FROM
    USERS
WHERE
    EMAIL = :email

# ---------------------------------------------------------------------
# ユーザーID による1件検索 (完了画面表示・テスト用)
# 呼出元: UniversalDao.findById(User.class, userId)
# ---------------------------------------------------------------------
FIND_BY_ID =
SELECT
    USER_ID,
    USER_NAME,
    EMAIL,
    VERSION,
    REGISTERED_AT
FROM
    USERS
WHERE
    USER_ID = :userId
