package com.nablarch.example.app.batch.action;

import java.io.File;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.Date;

import nablarch.core.date.SystemTimeUtil;
import nablarch.core.log.Logger;
import nablarch.core.log.LoggerManager;
import nablarch.core.repository.SystemRepository;
import nablarch.core.util.DateUtil;
import nablarch.core.util.FileUtil;
import nablarch.core.util.annotation.Published;
import nablarch.fw.DataReader;
import nablarch.fw.ExecutionContext;
import nablarch.fw.Result;
import nablarch.fw.Result.Success;
import nablarch.fw.action.BatchAction;

import com.nablarch.example.app.batch.reader.DeleteTargetFileReader;

/**
 * ファイル削除クラス。
 * <p>
 * 本検証版では、バッチ起動時に 1 度だけ外部 API（HTTP GET）を呼び出す処理を追加している。
 * 呼び出し先 URL とタイムアウトは {@code batch-config/file-delete.properties} の
 * {@code externalApi.helloUrl} / {@code externalApi.timeoutMs} で設定する。
 *
 * @author Nabu Rakutaro
 *
 */
@Published
public class FileDeleteAction extends BatchAction<File> {

    /** ロガー */
    private static final Logger LOGGER = LoggerManager.get(FileDeleteAction.class);

    /** 設定キー：ファイルパス */
    private static final String FILE_PATH_KEY = "RegistrationPdfFile.batch.work";

    /** 設定キー：外部 API 呼び出し先 URL */
    private static final String EXTERNAL_API_URL_KEY = "externalApi.helloUrl";

    /** 設定キー：外部 API 呼び出しタイムアウト(ms) */
    private static final String EXTERNAL_API_TIMEOUT_KEY = "externalApi.timeoutMs";

    /** 外部 API 呼び出しの既定タイムアウト(ms) */
    private static final int DEFAULT_TIMEOUT_MS = 3000;

    @Override
    public DataReader<File> createReader(ExecutionContext ctx) {
        // バッチ起動時に 1 度だけ外部 API を呼び出す（検証用）
        callExternalApi();
        return new DeleteTargetFileReader(Paths.get(SystemRepository.getString(FILE_PATH_KEY)));
    }

    @Override
    public Result handle(File inputData, ExecutionContext ctx) {

        String dateFileUpdateTime = DateUtil.formatDate(new Date(inputData.lastModified()), "yyyyMMdd");
        String yesterday = DateUtil.addDay(SystemTimeUtil.getDateString(), -1);
        // 更新日時が前日の日付より前だったらファイル削除
        if (dateFileUpdateTime.compareTo(yesterday) < 0) {
            FileUtil.deleteFile(inputData);
        }

        return new Success();
    }

    /**
     * 外部 API（HTTP GET）を呼び出し、ステータスコードとレスポンスボディを
     * 標準出力およびロガーに出力する。
     * <p>
     * 実装は JDK 11+ 標準の {@link HttpClient} を使用する。
     * Nablarch 標準の HTTP Messaging（{@code MessagingProvider} +
     * {@code HttpMessagingClient}）を用いる方法もあるが、本検証では
     * バッチ本体への差分を最小化するため JDK 標準 API を使用する。
     * 設定キー {@code externalApi.helloUrl} が未設定の場合は呼び出しをスキップする。
     */
    private void callExternalApi() {
        String url = SystemRepository.getString(EXTERNAL_API_URL_KEY);
        if (url == null || url.isEmpty()) {
            LOGGER.logInfo("externalApi.helloUrl is not configured, skip external API call.");
            return;
        }
        int timeoutMs = DEFAULT_TIMEOUT_MS;
        String timeoutRaw = SystemRepository.getString(EXTERNAL_API_TIMEOUT_KEY);
        if (timeoutRaw != null && !timeoutRaw.isEmpty()) {
            try {
                timeoutMs = Integer.parseInt(timeoutRaw);
            } catch (NumberFormatException e) {
                LOGGER.logWarn("invalid externalApi.timeoutMs='" + timeoutRaw
                        + "', use default " + DEFAULT_TIMEOUT_MS + " ms.");
            }
        }

        HttpClient client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofMillis(timeoutMs))
                .build();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .timeout(Duration.ofMillis(timeoutMs))
                .header("Accept", "application/json")
                .GET()
                .build();

        try {
            long start = System.currentTimeMillis();
            HttpResponse<String> response = client.send(request,
                    HttpResponse.BodyHandlers.ofString());
            long elapsed = System.currentTimeMillis() - start;
            String line = "external API called: url=" + url
                    + " status=" + response.statusCode()
                    + " elapsedMs=" + elapsed
                    + " body=" + response.body();
            System.out.println("[FileDeleteAction] " + line);
            LOGGER.logInfo(line);
        } catch (Exception e) {
            throw new IllegalStateException("failed to call external API: " + url, e);
        }
    }

}
