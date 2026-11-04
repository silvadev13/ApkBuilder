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
