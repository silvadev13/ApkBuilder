# Cerealicious — Android Build

Gradle-free Android build system using `project.py` + `build.py`.

## Prerequisites

- Python 3.11+
- Android SDK installed (`$ANDROID_SDK` or `$ANDROID_HOME` set)
- `aapt2`, `javac`, `kotlinc`, `d8`, `apksigner` on PATH (or set in `project.yml`)

## Quick Start

```bash
cd android/build
pip install pyyaml

# Debug build
python build.py

# Release build
python build.py --release

# Clean then build
python build.py --clean
```

Output APK: `android/.build/cerealicious-debug.apk`

## project.yml fields

| Field | Default | Description |
|---|---|---|
| `sdk-min-api-version` | 21 | Minimum Android API level |
| `sdk-api-version` | 31 | Target API level |
| `build-type` | debug | `debug` or `release` |
| `view-binding` | false | Enable View Binding generation |
| `keystore-path` | — | Relative path to `.jks` file |
| `java-version` | 17 | Java source/target compatibility |

## Architecture

The app is a **WebView wrapper** around the Cerealicious React SPA.

```
SplashActivity (1.4s)
  └── MainActivity
        └── WebView → https://cerealicious.app
              └── AndroidBridge (JS ↔ Java)
                    ├── showOrderNotification()
                    ├── vibrate()
                    ├── isNativeApp()
                    └── getLocale()
```

### Calling the bridge from React

```ts
if ((window as any).AndroidBridge?.isNativeApp()) {
  (window as any).AndroidBridge.showOrderNotification(
    "Order Delivered! 🍨",
    "Your Cocoa Puff Delight has arrived."
  );
}
```

## Push Notifications

FCM is wired up in `FCMService.java`. After the user logs in, POST their FCM token to:
```
POST https://api.cerealicious.app/devices/register
{ "token": "<fcm_token>" }
```
