package com.cerealicious.notifications;

import android.app.NotificationManager;
import android.content.Context;
import androidx.core.app.NotificationCompat;
import com.cerealicious.CerealiciousApp;
import com.cerealicious.R;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class FCMService extends FirebaseMessagingService {

    private static int notifId = 0;

    @Override
    public void onMessageReceived(RemoteMessage message) {
        String title = "Cerealicious";
        String body  = "You have an update";
        String channel = CerealiciousApp.CHANNEL_ORDERS;

        if (message.getNotification() != null) {
            title = message.getNotification().getTitle() != null
                ? message.getNotification().getTitle() : title;
            body  = message.getNotification().getBody() != null
                ? message.getNotification().getBody() : body;
        }

        // Promo messages go to the promo channel
        String type = message.getData().get("type");
        if ("promo".equals(type)) {
            channel = CerealiciousApp.CHANNEL_PROMOS;
        }

        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, channel)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true);

        NotificationManager nm = (NotificationManager)
            getSystemService(Context.NOTIFICATION_SERVICE);
        nm.notify(notifId++, builder.build());
    }

    @Override
    public void onNewToken(String token) {
        // TODO: send token to your backend so you can target this device
        // POST https://api.cerealicious.app/devices/register { token }
    }
}
