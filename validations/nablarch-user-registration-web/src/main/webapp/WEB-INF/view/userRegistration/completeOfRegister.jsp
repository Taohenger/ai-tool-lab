<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8"/>
  <title>ユーザー登録 — 完了</title>
  <style>
    body { font-family: "Hiragino Sans", sans-serif; max-width: 720px; margin: 32px auto; color:#333; }
    h1 { font-size: 20px; border-left: 4px solid #2c3e50; padding-left: 8px; }
    .done { margin-top:24px; padding:24px; background:#f0f8ff; border:1px solid #cfe2f3; text-align:center; }
    a.btn { display:inline-block; margin-top:16px; padding:8px 24px; background:#2c3e50; color:#fff; text-decoration:none; }
  </style>
</head>
<body>
  <h1>ユーザー登録 — 完了画面</h1>

  <div class="done">
    ユーザー登録が完了しました。<br/>
    ご登録いただいた情報は USERS テーブルに保存されています。
  </div>

  <p style="text-align:center;">
    <a class="btn" href="/action/userRegistration">もう一度登録する</a>
  </p>
</body>
</html>
