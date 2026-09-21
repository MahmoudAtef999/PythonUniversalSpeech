# Contributing to UniversalSpeech

Thank you for contributing to UniversalSpeech! This document outlines the process for development, running tests, building packages, and managing releases.

---

## 1. Development Setup

UniversalSpeech is compatible with Windows (32-bit and 64-bit) and Python 3.8+.

### Clone the repository
```bash
git clone https://github.com/MahmoudAtef999/PythonUniversalSpeech.git
cd PythonUniversalSpeech
```

### Create and activate a virtual environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install development dependencies
```bash
python -m pip install --upgrade pip
python -m pip install pytest build twine
```

---

## 2. Running Tests

The test suite can be run using either Python's built-in `unittest` runner or `pytest`.

### Using unittest
```bash
$env:PYTHONPATH = "."
python -m unittest discover -s tests -t . -v
```

### Using pytest
```bash
$env:PYTHONPATH = "."
pytest tests -v
```

All 30 unit tests must pass before submitting any changes.

---

## 3. Building the Package

We use the standard PyPA `build` tool to create both source distributions (`sdist`) and wheels (`wheel`).

```bash
python -m build
```

The built distributions will appear in `dist/`:
- `dist/universalspeech-<version>-py3-none-any.whl`
- `dist/universalspeech-<version>.tar.gz`

### Verifying Package Metadata
Run `twine check` with `--strict` to ensure metadata conforms to PyPA standards:
```bash
python -m twine check --strict dist/*
```

---

## 4. Release and Publishing Workflow

UniversalSpeech uses **GitHub Actions** and **PyPI Trusted Publishing** (OpenID Connect / OIDC) for secure, automated releases.

> **Note:** Never commit PyPI API tokens or passwords to the repository. Trusted Publishing handles authentication automatically without secrets.

### Release Flow:
```text
Git Tag (e.g., v2.0.0)
       ↓
GitHub Release
       ↓
GitHub Actions (publish.yml)
       ↓
Build & Security Checks
       ↓
Publish to PyPI via Trusted Publishing
```

### Step-by-Step Release Process:

1. **Update Version Number:**
   - In `UniversalSpeech/__init__.py`: update `__version__ = "X.Y.Z"`.
   - In `pyproject.toml`: update `version = "X.Y.Z"`.
   - In `tests/test_constants.py`: update expected version test.

2. **Run Tests and Build Verification:**
   ```bash
   python -m unittest discover -s tests -t . -v
   python -m build
   python -m twine check --strict dist/*
   ```

3. **Commit and Push Changes:**
   ```bash
   git commit -am "release: bump version to vX.Y.Z"
   git push origin main
   ```

4. **Create a Git Tag:**
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

5. **Create a GitHub Release:**
   - Go to **Releases** on GitHub.
   - Click **Draft a new release**.
   - Choose the tag `vX.Y.Z`.
   - Add title (e.g., `UniversalSpeech vX.Y.Z`) and release notes.
   - Click **Publish release**.

6. **Automated Publishing:**
   - The `Publish to PyPI` workflow will automatically trigger on GitHub Actions.
   - It will build the distributions, verify metadata, check archive contents, and upload to PyPI using PyPI Trusted Publishing.

---

## 5. Security and Architecture Notes

- **ZDSRAPI.dll:** This library is intentionally **not** bundled with UniversalSpeech. The C library includes safe fallback handling if the DLL is absent.
- **Native DLLs:** All native DLLs (`UniversalSpeech.dll`, `dolapi.dll`, `jfwapi.dll`, `nvdaControllerClient.dll`, `SAAPI32.dll`) are bundled in `lib/` (32-bit) and `lib64/` (64-bit) for seamless runtime execution on Windows.
