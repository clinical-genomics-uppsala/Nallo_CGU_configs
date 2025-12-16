# Tests

This directory contains automated tests for the Nallo CGU configs repository.

## Test Files

### `test_create_nallo_samplesheet.py`
Tests for the `create_nallo_samplesheet.py` script that generates Nallo-compatible samplesheets.

**Tests include:**
- Basic samplesheet generation
- Handling of missing arguments
- Sex column conversion (Male/Female/NA/Unknown)
- Column validation
- Custom output paths
- Numeric sample ID prefixing (e.g., `52662` → `D-52662`)
- Mixed numeric and alphanumeric sample IDs

### `test_params_validation.py`
Tests for validating Nallo params JSON files against pipeline requirements.

**Tests include:**
- JSON syntax validation
- Nextflow config parsing (requires Nextflow installed)
- Required parameter presence
- File path parameter format validation
- Boolean parameter type validation
- Preset value validation

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run specific test file:
```bash
pytest tests/test_create_nallo_samplesheet.py -v
pytest tests/test_params_validation.py -v
```

### Run specific test:
```bash
pytest tests/test_params_validation.py::test_params_json_syntax -v
```

## Requirements

Install test dependencies:
```bash
pip install -r requirements.txt pytest
```

For Nextflow config parsing tests, you also need:
- Nextflow installed and available in PATH

## CI/CD

Tests are automatically run on pull requests to `main` and `develop` branches via GitHub Actions.
See `.github/workflows/run_tests.yml` for the CI configuration.
