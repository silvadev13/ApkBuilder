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
     ├── libs/ (project libraries)
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

• AAPT2

• D8

• apksigner

```
pkg install -y openjdk-17 kotlinc aapt2 d8 apksigner
```

---

## Building an APK

To compile your project, use the builder.py module:

```
python builder.py <PROJECT_PATH> --min-sdk <MIN_SDK> --target-sdk <TARGET_SDK> --version-code <VERSION_CODE> --version-name <VERSION_NAME>
```

Example

```
python builder.py example_project/ --min-sdk 21 --target-sdk 34 --version-code 1 --version-name "1.0"
```

This will compile the project, generate DEX files, package resources, and produce a signed APK.


---
