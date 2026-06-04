package com.cerealicious;

import android.app.Application;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.os.Build;

public class CerealiciousApp extends Application {

    public static final String CHANNEL_ORDERS   = "orders";
    public static final String CHANNEL_PROMOS   = "promos";

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannels();
    }

    private void createNotificationChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;

        NotificationManager nm = getSystemService(NotificationManager.class);

        NotificationChannel orders = new NotificationChannel(
            CHANNEL_ORDERS,
            "Order Updates",
            NotificationManager.IMPORTANCE_HIGH
        );
        orders.setDescription("Real-time updates about your shake order");

        NotificationChannel promos = new NotificationChannel(
            CHANNEL_PROMOS,
            "Deals & Rewards",
            NotificationManager.IMPORTANCE_DEFAULT
        );
        promos.setDescription("Loyalty points, deals, and birthday rewards");

        nm.createNotificationChannel(orders);
        nm.createNotificationChannel(promos);
    }
}
