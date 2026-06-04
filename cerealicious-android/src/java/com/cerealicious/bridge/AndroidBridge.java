package com.cerealicious.bridge;

import android.app.NotificationManager;
import android.content.Context;
import android.webkit.JavascriptInterface;
import androidx.core.app.NotificationCompat;
import com.cerealicious.CerealiciousApp;
import com.cerealicious.R;

/**
 * JavaScript ↔ Android bridge.
 * Call from the React app via: window.AndroidBridge.methodName(args)
 */
public class AndroidBridge {

    private final Context ctx;
    private static int notifId = 1000;

    public AndroidBridge(Context ctx) {
        this.ctx = ctx;
    }

    /** Show a local push notification for an order update. */
    @JavascriptInterface
    public void showOrderNotification(String title, String message) {
        NotificationManager nm = (NotificationManager)
            ctx.getSystemService(Context.NOTIFICATION_SERVICE);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(ctx, CerealiciousApp.CHANNEL_ORDERS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true);

        nm.notify(notifId++, builder.build());
    }

    /** Vibrate the device (e.g. when order is delivered). */
    @JavascriptInterface
    public void vibrate(int durationMs) {
        android.os.Vibrator v = (android.os.Vibrator)
            ctx.getSystemService(Context.VIBRATOR_SERVICE);
        if (v != null && v.hasVibrator()) {
            v.vibrate(durationMs);
        }
    }

    /** Returns true so the React app knows it's running inside the Android wrapper. */
    @JavascriptInterface
    public boolean isNativeApp() {
        return true;
    }

    /** Returns the device's current locale (e.g. "en_GB"). */
    @JavascriptInterface
    public String getLocale() {
        return ctx.getResources().getConfiguration().getLocales().get(0).toString();
    }
}
