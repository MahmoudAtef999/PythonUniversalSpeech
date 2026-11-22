# Contributing to UniversalSpeech

Thank you for contributing to UniversalSpeech! This document outlines the process for development, running tests, building packages, and managing releases.

---

## 1. Development Setup

UniversalSpeech supports **Windows**, **Linux**, and **macOS** on Python 3.8+ with **zero external dependencies**.

### Clone the repository
```bash
git clone https://github.com/MahmoudAtef999/PythonUniversalSpeech.git
cd PythonUniversalSpeech
```

### Create and activate a virtual environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **Linux & macOS (Bash/Zsh)**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Install development dependencies
```bash
python -m pip install --upgrade pip
python -m pip install pytest pytest-cov mypy build twine
```

---

## 2. Running Tests

The test suite can be run using either Python's built-in `unittest` runner or `pytest`.

### Using unittest
```bash
# Windows PowerShell:
$env:PYTHONPATH = "."
python -m unittest discover -s tests -t . -v

# Linux / macOS:
PYTHONPATH=. python -m unittest discover -s tests -t . -v
```

### Using pytest
```bash
# Windows PowerShell:
$env:PYTHONPATH = "."
python -m pytest tests -v --cov=UniversalSpeech

# Linux / macOS:
PYTHONPATH=. pytest tests -v --cov=UniversalSpeech
```

All 85 automated unit tests must pass before submitting any changes.

---

## 3. Building the Package

We use the standard PyPA `build` tool to create both source distributions (`sdist`) and wheels (`wheel`).

```bash
python -m build
```

The built distributions will appear in `dist/`:
- `dist/universalspeech-<version>-py3-none-any.whl`
- `dist/universalspeech-<version>.tar.gz`

### Validating the built wheel
```bash
twine check dist/*
```

---

## 4. Code Quality & Standards

- **Zero External Dependencies**: UniversalSpeech must not introduce mandatory third-party runtime dependencies. Everything must be implemented using the Python standard library (`ctypes`, `socket`, `subprocess`).
- **Typing**: Keep complete type annotations across all modules; verify with `mypy UniversalSpeech`.
- **Cross-Platform Compatibility**: Ensure features cleanly adapt or raise `UnsupportedError` across Windows, Linux, and macOS.
- **Documentation**: All public classes, methods, and properties must have clear docstrings.

---

## 5. Submitting Changes

1. Create a feature branch from `main`: `git checkout -b feature/my-new-feature`
2. Commit changes with clear, descriptive commit messages adhering to Conventional Commits:
   - `feat(...)`: New features or backends.
   - `fix(...)`: Bug fixes.
   - `refactor(...)`: Architectural improvements without behavior changes.
   - `test(...)`: Adding or updating test cases.
   - `docs(...)`: Documentation updates.
3. Push to your fork and submit a Pull Request.
