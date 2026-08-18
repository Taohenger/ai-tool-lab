# Nablarch ユーザー登録機能 端到端验证 (W11AC01)

> **目的**:验证 Agent 能否利用 **nabledge-5 Skill**(Nablarch 5 知识库)+ Python 自动化,完成"用户注册功能"从要件理解 → 外部设计 → 内部设计 → 代码生成 → 测试规格 → Excel 设计书产出的全流程,并把成果物无缝灌入 Excel 模版。

| 項目 | 値 |
|------|----|
| 画面ID | W11AC01 |
| 機能名 | ユーザー登録 (User Registration) |
| 対象フレームワーク | Nablarch 5 |
| 知識源 | `vendor/nabledge/plugins/nabledge-5/skills/nabledge-5/`(本仓库离线副本) |
| Excel 変換 | Python + openpyxl(officeCli 不可用のため) |
| 分支 | `feat/nablarch-user-registration-验证` |

---

## 一、验证成果物总览

### 1. 设计文档(Markdown / CSV)
| ファイル | 内容 |
|----------|------|
| [docs/01_External_Design_W11AC01.md](docs/01_External_Design_W11AC01.md) | 外部設計:画面遷移図(Mermaid)+ Nablarch Custom Tag JSP + バリデーション規則表 |
| [docs/02_Internal_Design_W11AC01.md](docs/02_Internal_Design_W11AC01.md) | 内部設計:Action/Form/Entity 責務配置 + SQL テンプレート + トランザクション/セッション設計 |
| [02_Screen_Item_List.csv](02_Screen_Item_List.csv) | 項目定義元数据(Excel 灌入用) |
| [03_Test_Cases.csv](03_Test_Cases.csv) | 単体テスト仕様(14 ケース、正常系 + 異常系境界値) |

### 2. 生成コード(Nablarch 5 規約準拠)
| ファイル | 内容 |
|----------|------|
| [src/main/java/com/example/app/form/UserRegistrationForm.java](src/main/java/com/example/app/form/UserRegistrationForm.java) | Form(@Required/@Length/@Email/@Pattern/@Domain) |
| [src/main/java/com/example/app/entity/User.java](src/main/java/com/example/app/entity/User.java) | Entity(@Table/@Id/@Version) |
| [src/main/java/com/example/app/action/UserRegistrationAction.java](src/main/java/com/example/app/action/UserRegistrationAction.java) | Action(@InjectForm/@OnError/@OnDoubleSubmission/PRG) |
| [src/main/resources/com/example/app/entity/User.sql](src/main/resources/com/example/app/entity/User.sql) | UniversalDao 用 SQL(FIND_BY_EMAIL / FIND_BY_ID) |
| [src/test/java/com/example/app/action/UserRegistrationActionTest.java](src/test/java/com/example/app/action/UserRegistrationActionTest.java) | JUnit + BasicHttpRequestTestTemplate 継承 |

### 3. Excel 設計書
| ファイル | 内容 |
|----------|------|
| [templates/Design_Doc_Template.xlsx](templates/Design_Doc_Template.xlsx) | 3 Sheet 空模版(画面レイアウト/項目定義/単体テスト仕様書) |
| [W11AC01_ユーザー登録機能_詳細設計書.xlsx](W11AC01_ユーザー登録機能_詳細設計書.xlsx) | **★ 最終成果物**:CSV+JSP 灌入済み |

### 4. 自動化スクリプト
| ファイル | 内容 |
|----------|------|
| [scripts/gen_template.py](scripts/gen_template.py) | Excel 模版生成 |
| [scripts/convert_to_excel.py](scripts/convert_to_excel.py) | 成果物 → Excel 灌入変換 |

---

## 二、5 階段 Prompt 実行記録

### Phase 2.1: 外部設計(要件理解 + Markdown 草稿)
- **入力**:要件(ユーザー名 50 字 / Email / パスワード 8 字以上半角英数 / 確認→登録遷移)
- **知識源**:`web-application-getting-started-project-update.md` / `web-application-client-create1.md`
- **成果**:画面遷移図(Mermaid stateDiagram)+ input/confirm/completeOfRegister の 3 JSP(Nablarch `<n:form>` / `<n:text>` / `<n:button>` / `<n:submit useToken="true" allowDoubleSubmission="false">`)+ バリデーション規則表

### Phase 2.2: 内部設計(データ抽取 + CSV/JSON 元数据)
- **知識源**:`web-application-application-design.md`(責務配置)+ `libraries-universal-dao.md`(Entity/SQL 規約)
- **成果**:`UserRegistrationForm` / `UserRegistrationAction` / `User` Entity 設計 + `02_Screen_Item_List.csv`(3 項目)+ `User.sql`(FIND_BY_EMAIL 重複チェック SQL)

### Phase 2.3: 自動コード生成
- **成果**:Form.java(@Required/@Length/@Email/@Pattern/@Domain)+ Action.java(@InjectForm/@OnError/@OnDoubleSubmission/PRG 303 リダイレクト)+ User.sql(UniversalDao 規約)

### Phase 2.4: テスト规格 + JUnit
- **知識源**:`testing-framework-02-RequestUnitTest.md`(HttpRequestTestSupport / BasicHttpRequestTestTemplate / setValidToken / assertApplicationMessageId)
- **成果**:`03_Test_Cases.csv`(14 ケース:正常系 3 + 異常系 11、境界値含む)+ `UserRegistrationActionTest.java`(JUnit、テンプレート継承)

### Phase 2.5: Excel 変換(核心環節)
- **方式**:Python + openpyxl(officeCli は環境不可用のため代替)
- **成果**:`W11AC01_ユーザー登録機能_詳細設計書.xlsx` —— 3 Sheet に灌入済み
  - 項目定義 Sheet ← 02_Screen_Item_List.csv(3 行)
  - 単体テスト仕様書 Sheet ← 03_Test_Cases.csv(14 行)
  - 画面レイアウト Sheet ← 01_External_Design_W11AC01.md の JSP コード塊

---

## 三、验证成功判定 Checklist

| 判定項目 | 結果 | 証跡 |
|----------|------|------|
| ✅ 最終成果物:目録下に正常に開ける .xlsx 生成 | **PASS** | `W11AC01_ユーザー登録機能_詳細設計書.xlsx`(12,356 bytes、3 Sheet 全て正常) |
| ✅ 数据对齐:Excel「項目名/物理名/精査規則」== Form.java 注解 100% 一致 | **PASS** | [Form.java](src/main/java/com/example/app/form/UserRegistrationForm.java) L37-L51 与 [項目定義 Sheet R4-R6](W11AC01_ユーザー登録機能_詳細設計書.xlsx) 的精査ルール列完全一致 |
| ✅ 完整性:Excel 同時含「内部/外部画面設計」+「単体テスト Specification 矩陣」 | **PASS** | 画面レイアウト Sheet(JSP 3 画面)+ 項目定義 Sheet(3 項目)+ 単体テスト仕様書 Sheet(14 ケース) |
| ✅ Nablarch 5 規約準拠 | **PASS** | 全てのコード/JSP/SQL が nabledge-5 知識源のパターンを踏襲(@InjectForm/@OnDoubleSubmission/UniversalDao/SessionUtil/PRG/<n:form useToken>) |
| ✅ 知識源トレーサビリティ | **PASS** | 各成果物のヘッダに参照した nabledge-5 資産パスを明記 |

### 数据对齐の詳細検証(抜粋)

| 項目 | Excel 項目定義 Sheet | Form.java 注解 | 一致 |
|------|---------------------|----------------|------|
| userName | `@Required + @Length(max=50) + @Domain("userName")` | L38-40: `@Required @Length(max=50) @Domain("userName")` | ✅ |
| email | `@Required + @Email + @Length(max=254) + @Domain("email")` | L43-46: 同上 | ✅ |
| password | `@Required + @Length(min=8, max=100) + @Pattern(regexp="[0-9a-zA-Z]+") + @Domain("password")` | L49-52: 同上 | ✅ |

---

## 四、Phase 3: 离线部署打包清单

离线環境で同一成果物を再現するために必要な資産:

### 1. 模型与 API
- `qwen2.5-coder:32b` 重み(Ollama / vLLM で稼働)
- ローカル API 実行環境(Ollama serve または vLLM OpenAI 互換サーバ)

### 2. 知識库 Skill 資産
- 本仓库 `vendor/nabledge/`(191 MB、nablarch/nabledge 完整 clone)
- 重点:`plugins/nabledge-5/skills/nabledge-5/`(38 MB、Nablarch 5 専用)

### 3. 自動化変換チェーン
- 本仓库 `validations/nablarch-user-registration/scripts/`
  - `gen_template.py` —— Excel 模版生成
  - `convert_to_excel.py` —— CSV/MD → Excel 灌入
- Excel 模版:`templates/Design_Doc_Template.xlsx`
- Python 環境:Python 3.x + `pip install openpyxl pandas`

### 4. Prompt 指令集
- Phase 2.1 ~ 2.5 の 5 プロンプトは本 README の「二、5 階段 Prompt 実行記録」に集約
- 各 Phase の入力(要件)と出力(成果物)の対応関係も記録済み

### 5. 離線再現手順
```bash
# 1. 离线環境に本仓库をクローン済みの状態で
cd /workspace
git checkout feat/nablarch-user-registration-验证

# 2. Python 依存インストール(事前に wheel を离线環境へ持込)
pip install --no-index --find-links=./wheels openpyxl pandas

# 3. Excel 模版再生成
cd validations/nablarch-user-registration
python3 scripts/gen_template.py

# 4. 成果物から Excel 設計書再生成
python3 scripts/convert_to_excel.py

# 5. ローカル LLM + nabledge-5 で新規機能設計を再実行する場合:
#    Claude Code 等で vendor/install-offline.sh -v 5 . を実行し、
#    /n5 <Phase プロンプト> で各段階を再実行可能
```

---

## 五、検証から得られた知見

### 5.1 nabledge Skill の有効性
- ✅ Nablarch 5 の **Form/Action/UniversalDao/SessionUtil/JSP カスタムタグ/テストフレームワーク** の全パターンを知識源から即時参照できた
- ✅ 特に `@InjectForm` / `@OnDoubleSubmission` / `useToken="true"` / PRG リダイレクト等の Nablarch 固有イディオムを正確に適用できた
- ✅ SQL ファイル規約(`NAME = SELECT ...`)と Entity パッケージ配置規約を守って生成できた

### 5.2 officeCli 代替としての Python + openpyxl
- ✅ officeCli 非可用環境でも Python + openpyxl で同等の Excel 生成・灌入が可能
- ✅ Mermaid 図は Excel に直接描画できないため、JSP コード塊を画面レイアウト Sheet に展開する方式で代替(設計意図は保持)
- ⚠ 本件では Markdown → Excel の「画面レイアウト」は JSP 構造テキスト展開方式。真の WYSIWYG レイアウトは別途 HTML ダンプ等が必要

### 5.3 改善余地
- Excel「画面レイアウト」Sheet を JSP テキストではなく HTML ダンプ画像で埋める場合、`testing-framework-02-RequestUnitTest.md` の HTML ダンプ機能を利用して screenshot を生成 → openpyxl の `add_image` で挿入可能
- Form.java の `@Domain("xxx")` は `app.xml` の `<domain>` 設定と連動するため、完全な型検証には `app.xml` のドメイン定義もセットで生成すべき

---

## 六、参照した nabledge-5 知識資産 一覧

| 資産パス | 用途 |
|----------|------|
| `docs/processing-pattern/web-application/web-application-getting-started-project-update.md` | 登録/更新フロー・Form/Action/SessionUtil/PRG パターン・SQL ファイル形式 |
| `docs/processing-pattern/web-application/web-application-client-create1.md` | 登録画面初期表示・`<n:form>` / `<n:text>` / `<n:button>` / routes.xml |
| `docs/processing-pattern/web-application/web-application-application-design.md` | アプリケーション責務配置原則 |
| `docs/component/libraries/libraries-bean-validation.md` | Bean Validation + DB 相関バリデーション戦略 |
| `docs/component/libraries/libraries-universal-dao.md` | Entity/楽観ロック/SQL ファイル規約 |
| `docs/development-tools/testing-framework/testing-framework-02-RequestUnitTest.md` | リクエスト単体テスト・HttpRequestTestSupport・BasicHttpRequestTestTemplate |
| `docs/javadoc/javadoc-nablarch-common-web-interceptor-InjectForm.md` | `@InjectForm` |
| `docs/javadoc/javadoc-nablarch-common-web-token-OnDoubleSubmission.md` | `@OnDoubleSubmission` |
| `docs/javadoc/javadoc-nablarch-common-handler-TransactionManagementHandler.md` | トランザクション管理 |

---

## 七、ディレクトリ構成

```
validations/nablarch-user-registration/
├── README.md                                           # 本文件
├── W11AC01_ユーザー登録機能_詳細設計書.xlsx              # ★ 最終成果物 Excel
├── 02_Screen_Item_List.csv                             # 項目定義元数据
├── 03_Test_Cases.csv                                    # 単体テスト仕様
├── docs/
│   ├── 01_External_Design_W11AC01.md                    # 外部設計 MD
│   └── 02_Internal_Design_W11AC01.md                    # 内部設計 MD
├── src/
│   ├── main/
│   │   ├── java/com/example/app/
│   │   │   ├── action/UserRegistrationAction.java       # Action
│   │   │   ├── form/UserRegistrationForm.java           # Form
│   │   │   └── entity/User.java                         # Entity
│   │   └── resources/com/example/app/entity/
│   │       └── User.sql                                 # SQL ファイル
│   └── test/java/com/example/app/action/
│       └── UserRegistrationActionTest.java             # JUnit テスト
├── templates/
│   └── Design_Doc_Template.xlsx                         # Excel 模版
└── scripts/
    ├── gen_template.py                                  # 模版生成
    └── convert_to_excel.py                             # 成果物 → Excel 灌入
```
