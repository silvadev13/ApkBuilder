# ApkBuilder

- ApkBuilder is a lightweight Android Project builder CLI.

# Documentation

- See project.yml docs at [Docs](https://github.com/silvadev13/ApkBuilder/blob/main/docs/config.rst)

## Features

- [x] APK Compilation
- [ ] AAB Support
- [x] Java
- [x] Kotlin
- [ ] R8 / ProGuard
- [x] ViewBinding
- [ ] Jetpack Compose (not supported yet)

## System dependencies

- `python`
- `aapt2`
- `javac`
- `kotlinc`
- `d8`
- `apksigner`

## Python dependencies

- `pip install -r requirements.txt`

## Building an APK

To compile your project, use the builder module:

example:

```
python -m cli.builder example/
```

## Deployment (BorderP45 App)

BorderP45 web application can be deployed using Docker and Gunicorn.

### Docker Deployment

To build and run using Docker Compose:

```bash
docker-compose up --build -d
```

Or using standard Docker commands:

```bash
docker build -t borderp45 .
docker run -p 5000:5000 borderp45
```
This is the GitHub repository for ApkBuilder, a lightweight Android project builder CLI created by user mikeraymonf13-creator.

Here's a summary of what the project is about:

Purpose & Features

· It's a command-line tool for building Android projects, compiling them into APK (and AAB) files.
· Supports Java and Kotlin, R8/ProGuard, and ViewBinding.
· Jetpack Compose is listed as not supported yet.

System Dependencies Required
python, aapt2, javac, kotlinc, d8, apksigner
Plus Python packages via pip install -r requirements.txt.

Basic Usage
To compile a project:

```
python -m cli.builder example/
```

Repository Structure
The repo contains several directories including:

· cli – the builder command-line module
· core – core logic
· BorderP45 – a related web application
· ton-wallet-dashboard – TON API/frontend integration
· docs, example, tests, utils, .github/workflows

Deployment (BorderP45 App)
The BorderP45 web app can be deployed with Docker/Gunicorn:

```
docker-compose up --build -d
# or
docker build -t borderp45 .
docker run -p 5000:5000 borderp45
```

Activity
The project has been actively maintained through 2026, with recent commits involving performance optimizations, CI updates (actions/checkout v5 with Node 24), and Docker/Gunicorn deployment setup.

One thing worth noting: the repository description calls it "A BorderP45 Android Project builder CLI," and it appears to combine an Android build tool with a related web app (BorderP45) and TON wallet integration — so the scope is a bit broader than just APK building.

Would you like me to dig into any specific part, such as the project.yml configuration docs, the CLI implementation, or the BorderP45 web app?