<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8"/>
  <title>ユーザー登録 — 確認</title>
  <style>
    body { font-family: "Hiragino Sans", sans-serif; max-width: 720px; margin: 32px auto; color:#333; }
    h1 { font-size: 20px; border-left: 4px solid #2c3e50; padding-left: 8px; }
    table { width:100%; border-collapse: collapse; margin-top:16px; }
    th, td { padding: 8px 12px; border: 1px solid #ddd; }
    th { background:#f5f5f5; text-align:left; width:30%; }
    .buttons { margin-top: 24px; text-align: center; }
    .buttons input { padding: 8px 24px; font-size: 14px; margin: 0 8px; }
  </style>
</head>
<body>
  <h1>ユーザー登録 — 確認画面</h1>

  <p>以下の内容で登録します。よろしいですか?</p>

  <table>
    <tr><th>ユーザー名</th><td><n:write name="form.userName" /></td></tr>
    <tr><th>メールアドレス</th><td><n:write name="form.email" /></td></tr>
    <tr><th>パスワード</th><td>******** (入力済)</td></tr>
  </table>

  <n:write name="form" />

  <n:form action="/action/userRegistration/register" method="post" useToken="true">
    <div class="buttons">
      <n:submit type="submit" uri="register" value="登録する" />
      <n:submit type="button" uri="back" value="戻る" />
    </div>
  </n:form>
</body>
</html>
