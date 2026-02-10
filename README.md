# ApkBuilder

ApkBuilder is a lightweight Android build tool designed for **Termux**.  
It bundles essential Android build utilities to compile and package APKs
without Android Studio or Gradle.

This project is focused on simplicity and portability, allowing Android apps
to be built directly from the command line on Android devices.

---

## Features

- [x] APK Compilation
- [ ] AAB Support
- [x] Java
- [x] Kotlin
- [ ] R8 / ProGuard
- [ ] ViewBinding (not supported yet)
- [ ] Jetpack Compose (not supported yet)

---

## Project Structure

Your Android project must follow this structure:

```text
Project/
 └── app/
     └── src/
         └── main/
             ├── assets/        (optional)
             ├── jniLibs/       (optional)
             ├── java/          (Java/Kotlin source files)
             ├── res/           (resources)
             └── AndroidManifest.xml
```

---

## Requirements (Android / Termux)

Before using ApkBuilder, make sure you have the following installed in Termux:

• OpenJDK 17

• Kotlin compiler (kotlinc)

• apksigner


You also need to make aapt2 executable:

```
chmod +x build_logic/tools/aapt2
```

---

## Building an APK

To compile your project, use the builder.py module:

```
python builder.py <APK_PATH> <MIN_SDK> <TARGET_SDK> <VERSION_CODE> <VERSION_NAME>
```

Example

```
python builder.py output.apk 21 34 1 "1.0"
```

This will compile the project, generate DEX files, package resources, and produce a signed APK.


---
