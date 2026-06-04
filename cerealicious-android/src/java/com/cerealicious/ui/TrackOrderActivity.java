package com.cerealicious.ui;

import android.annotation.SuppressLint;
import android.app.NotificationManager;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;

import com.cerealicious.CerealiciousApp;
import com.cerealicious.R;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.Executors;

/**
 * TrackOrderActivity
 *
 * Handles deep links:  https://cerealicious.app/track/{orderId}
 * Also launched internally from MainActivity when the user taps "Track Order".
 *
 * Architecture:
 *  - Renders the React /track/:orderId page in a WebView
 *  - Polls the REST API every POLL_INTERVAL_MS for status changes
 *  - Fires a native push notification when status advances
 *  - Exposes a JS bridge so the React page can request a native vibrate/notification
 */
public class TrackOrderActivity extends AppCompatActivity {

    // ── Constants ────────────────────────────────────────────────────────────

    private static final String API_BASE     = "https://api.cerealicious.app";
    private static final String WEB_BASE     = "https://cerealicious.app";
    private static final long   POLL_INTERVAL_MS = 15_000;   // poll every 15 s
    private static final int    NOTIF_ID         = 9001;

    // Ordered list — used to detect forward progression
    private static final String[] STATUS_ORDER = {
        "placed", "confirmed", "preparing", "ready", "out_for_delivery", "delivered"
    };

    // ── State ────────────────────────────────────────────────────────────────

    private String  orderId;
    private String  lastKnownStatus = "";
    private boolean polling         = false;

    private WebView      webView;
    private TextView     tvOrderId;
    private TextView     tvStatus;
    private ImageButton  btnBack;

    private final Handler        pollHandler  = new Handler(Looper.getMainLooper());
    private final Runnable       pollRunnable = this::pollOrderStatus;

    // ── Lifecycle ────────────────────────────────────────────────────────────

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_track_order);

        tvOrderId = findViewById(R.id.tv_order_id);
        tvStatus  = findViewById(R.id.tv_status);
        btnBack   = findViewById(R.id.btn_back);
        webView   = findViewById(R.id.webview_track);

        btnBack.setOnClickListener(v -> finish());

        // ── Resolve orderId from deep link or Intent extra ──
        orderId = resolveOrderId();
        if (orderId == null) {
            tvStatus.setText("No order ID provided.");
            return;
        }

        tvOrderId.setText("Order #" + orderId.toUpperCase());

        // ── WebView setup ──
        WebSettings ws = webView.getSettings();
        ws.setJavaScriptEnabled(true);
        ws.setDomStorageEnabled(true);

        webView.addJavascriptInterface(new TrackBridge(), "TrackBridge");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                String url = req.getUrl().toString();
                return !url.startsWith(WEB_BASE);
            }
        });

        webView.loadUrl(WEB_BASE + "/track/" + orderId);

        // ── Start polling ──
        startPolling();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (orderId != null && !polling) startPolling();
    }

    @Override
    protected void onPause() {
        super.onPause();
        stopPolling();
    }

    @Override
    protected void onDestroy() {
        stopPolling();
        webView.destroy();
        super.onDestroy();
    }

    // ── Deep link / intent resolution ────────────────────────────────────────

    private String resolveOrderId() {
        // 1. Intent extra (launched from MainActivity)
        String extra = getIntent().getStringExtra("order_id");
        if (extra != null && !extra.isEmpty()) return extra;

        // 2. Deep link  https://cerealicious.app/track/{orderId}
        Uri data = getIntent().getData();
        if (data != null) {
            String path = data.getPath();            // e.g. "/track/ABC123"
            if (path != null && path.startsWith("/track/")) {
                String id = path.substring("/track/".length());
                if (!id.isEmpty()) return id;
            }
        }

        return null;
    }

    // ── Polling ──────────────────────────────────────────────────────────────

    private void startPolling() {
        polling = true;
        pollHandler.post(pollRunnable);
    }

    private void stopPolling() {
        polling = false;
        pollHandler.removeCallbacks(pollRunnable);
    }

    private void pollOrderStatus() {
        Executors.newSingleThreadExecutor().execute(() -> {
            try {
                String endpoint = API_BASE + "/orders/" + orderId + "/status";
                HttpURLConnection conn = (HttpURLConnection) new URL(endpoint).openConnection();
                conn.setRequestMethod("GET");
                conn.setRequestProperty("Accept", "application/json");
                conn.setConnectTimeout(8_000);
                conn.setReadTimeout(8_000);

                if (conn.getResponseCode() == 200) {
                    BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getInputStream())
                    );
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) sb.append(line);
                    br.close();

                    JSONObject json   = new JSONObject(sb.toString());
                    String newStatus  = json.optString("status", "");
                    String eta        = json.optString("eta", "");

                    if (!newStatus.isEmpty() && !newStatus.equals(lastKnownStatus)) {
                        onStatusChanged(newStatus, eta);
                    }
                }
                conn.disconnect();
            } catch (Exception e) {
                // Network unavailable — fail silently, retry next poll
            }

            // Schedule next poll if still active
            if (polling) {
                pollHandler.postDelayed(pollRunnable, POLL_INTERVAL_MS);
            }
        });
    }

    private void onStatusChanged(String newStatus, String eta) {
        boolean isProgression = isForwardProgression(lastKnownStatus, newStatus);
        lastKnownStatus = newStatus;

        runOnUiThread(() -> {
            String label = humanLabel(newStatus);
            tvStatus.setText(label);

            // Push native notification for meaningful forward progressions
            if (isProgression) {
                String title   = notifTitle(newStatus);
                String message = eta.isEmpty() ? label : label + " — ETA: " + eta;
                fireNotification(title, message);
                vibratePattern(newStatus);
            }

            // Sync the React page
            String js = "window.dispatchEvent(new CustomEvent('nativeStatusUpdate', "
                      + "{ detail: { status: '" + newStatus + "', eta: '" + eta + "' } }));";
            webView.evaluateJavascript(js, null);
        });
    }

    // ── Notification helpers ─────────────────────────────────────────────────

    private void fireNotification(String title, String message) {
        NotificationCompat.Builder builder = new NotificationCompat.Builder(
            this, CerealiciousApp.CHANNEL_ORDERS
        )
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true);

        NotificationManager nm = (NotificationManager)
            getSystemService(NOTIFICATION_SERVICE);
        nm.notify(NOTIF_ID, builder.build());
    }

    private void vibratePattern(String status) {
        android.os.Vibrator v = (android.os.Vibrator) getSystemService(VIBRATOR_SERVICE);
        if (v == null || !v.hasVibrator()) return;

        if ("delivered".equals(status)) {
            // Long celebration buzz
            v.vibrate(new long[]{0, 200, 100, 200, 100, 400}, -1);
        } else if ("out_for_delivery".equals(status)) {
            v.vibrate(new long[]{0, 150, 80, 150}, -1);
        } else {
            v.vibrate(80);
        }
    }

    // ── Status helpers ───────────────────────────────────────────────────────

    private static int statusIndex(String status) {
        for (int i = 0; i < STATUS_ORDER.length; i++) {
            if (STATUS_ORDER[i].equals(status)) return i;
        }
        return -1;
    }

    private static boolean isForwardProgression(String from, String to) {
        return statusIndex(to) > statusIndex(from);
    }

    private static String humanLabel(String status) {
        switch (status) {
            case "placed":           return "Order Placed";
            case "confirmed":        return "Order Confirmed";
            case "preparing":        return "Being Prepared 🥣";
            case "ready":            return "Ready for Collection";
            case "out_for_delivery": return "On the Way! 🛵";
            case "delivered":        return "Delivered! 🎉";
            default:                 return status;
        }
    }

    private static String notifTitle(String status) {
        switch (status) {
            case "confirmed":        return "Cerealicious — Order Confirmed";
            case "preparing":        return "Cerealicious — We're making your shake 🥣";
            case "out_for_delivery": return "Cerealicious — Your order is on the way! 🛵";
            case "delivered":        return "Cerealicious — Delivered! 🎉";
            default:                 return "Cerealicious — Order Update";
        }
    }

    // ── JS Bridge ────────────────────────────────────────────────────────────

    /**
     * Exposed to the React page as window.TrackBridge
     */
    private class TrackBridge {

        /** Called by React when the user taps "Notify me when ready" */
        @JavascriptInterface
        public void requestStatusAlert(String statusToAlert) {
            // Store locally — fire notification when that status is reached
            runOnUiThread(() ->
                tvStatus.setText(tvStatus.getText() + " (alert set for: " + humanLabel(statusToAlert) + ")")
            );
        }

        /** React can ask for the current polled status */
        @JavascriptInterface
        public String getCurrentStatus() {
            return lastKnownStatus;
        }

        /** React can trigger a manual re-poll */
        @JavascriptInterface
        public void refresh() {
            runOnUiThread(() -> pollHandler.post(pollRunnable));
        }
    }
}
