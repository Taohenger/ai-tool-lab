<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c"   uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="n"   uri="http://tis.co.jp/nablarch" %>
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8"/>
  <title>ユーザー登録 — 入力</title>
  <style>
    body { font-family: "Hiragino Sans", sans-serif; max-width: 720px; margin: 32px auto; color:#333; }
    h1 { font-size: 20px; border-left: 4px solid #2c3e50; padding-left: 8px; }
    table { width:100%; border-collapse: collapse; margin-top:16px; }
    th, td { padding: 8px 12px; border: 1px solid #ddd; }
    th { background:#f5f5f5; text-align:left; width:30%; }
    input[type=text], input[type=password] { width: 100%; padding: 6px; box-sizing: border-box; }
    .buttons { margin-top: 24px; text-align: center; }
    .buttons input { padding: 8px 24px; font-size: 14px; }
    .error { color: #c00; font-size: 12px; }
  </style>
</head>
<body>
  <h1>ユーザー登録 — 入力画面</h1>

  <n:write name="form" />

  <n:errors filter="global" cssClass="error" />

  <n:form action="/action/userRegistration/confirm" method="post" useToken="true">
    <table>
      <tr>
        <th>ユーザー名</th>
        <td>
          <n:text name="form.userName" />
          <n:error name="form.userName" errorCss="error" />
        </td>
      </tr>
      <tr>
        <th>メールアドレス</th>
        <td>
          <n:text name="form.email" />
          <n:error name="form.email" errorCss="error" />
        </td>
      </tr>
      <tr>
        <th>パスワード</th>
        <td>
          <n:password name="form.password" />
          <n:error name="form.password" errorCss="error" />
        </td>
      </tr>
    </table>

    <div class="buttons">
      <n:submit type="submit" uri="confirm" value="確認画面へ" />
    </div>
  </n:form>

  <p style="margin-top:24px;font-size:12px;color:#999;">
    ※ 8 文字以上 100 文字以下の半角英数字。メールアドレスは重複不可。
  </p>
</body>
</html>
