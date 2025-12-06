# Test Suite Documentation

Comprehensive test suite for the PCA Yield Curve Application with unit tests, integration tests, and end-to-end tests.

## 📋 Overview

The test suite ensures:
- ✅ **Code Quality**: 80%+ code coverage
- ✅ **Reliability**: All critical paths tested
- ✅ **Regression Prevention**: Automated testing on CI/CD
- ✅ **Documentation**: Tests serve as usage examples

## 🏗️ Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                     # Pytest configuration (in root)
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_ecb_api.py           # ECB API service tests
│   ├── test_pca_analysis.py      # PCA analysis tests
│   └── test_stress_scenarios.py  # Stress scenario tests
└── integration/                   # Integration tests (slower)
    ├── test_api_endpoints.py     # Flask API endpoint tests
    └── test_full_workflow.py     # End-to-end workflow tests
```

## 🚀 Running Tests

### Quick Start

**All Tests:**
```bash
# Linux/Mac
./run_tests.sh

# Windows
run_tests.bat
```

### Specific Test Categories

**Unit Tests Only:**
```bash
pytest -m unit
```

**Integration Tests Only:**
```bash
pytest -m integration
```

**Specific Test File:**
```bash
pytest tests/unit/test_ecb_api.py
```

**Specific Test Function:**
```bash
pytest tests/unit/test_ecb_api.py::TestECBDataService::test_fetch_yield_curve_success
```

### With Coverage

**Coverage Report:**
```bash
pytest --cov=app --cov=services --cov-report=html
```

Open `htmlcov/index.html` in your browser to view detailed coverage.

**Coverage with Missing Lines:**
```bash
pytest --cov=app --cov=services --cov-report=term-missing
```

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation with mocked dependencies.

**test_ecb_api.py**: 20+ tests
- API initialization
- Data fetching with mocked responses
- Error handling (timeout, HTTP errors, parsing errors)
- Response parsing logic
- Edge cases

**test_pca_analysis.py**: 25+ tests
- PCA computation
- Component analysis
- Variance calculation
- Yield curve reconstruction
- Plot generation
- Edge cases (small datasets, more components than features)

**test_stress_scenarios.py**: 20+ tests
- Stress scenario generation
- Rolling quantile calculation
- Up/down scenario creation
- Plot generation
- Parameter variations

### Integration Tests (`@pytest.mark.integration`)

Test component interactions and complete workflows.

**test_api_endpoints.py**: 25+ tests
- Flask app configuration
- Health check endpoint
- Main analyze endpoint
- Request validation
- Error responses
- JSON structure validation

**test_full_workflow.py**: 15+ tests
- Complete PCA pipeline
- API request to response flow
- Data transformation through all components
- Error propagation
- Performance tests
- Robustness tests

## 📊 Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| services/ecb_api.py | 85% | ✅ |
| services/pca_analysis.py | 90% | ✅ |
| services/stress_scenarios.py | 85% | ✅ |
| app.py | 80% | ✅ |
| **Overall** | **80%** | **✅** |

## 🔧 Fixtures

### Data Fixtures (conftest.py)

**`sample_yield_data`**
- 100 observations, 32 maturities
- Realistic yield curve structure
- Used for comprehensive tests

**`small_yield_data`**
- 30 observations, 5 maturities
- Used for quick tests

**`mock_ecb_response`**
- Mocked ECB API JSON response
- Realistic structure for testing parsing

### Service Fixtures

**`ecb_service`** - ECB API service instance
**`pca_analyzer`** - PCA analyzer instance
**`stress_generator`** - Stress scenario generator

### Flask Fixtures

**`app`** - Flask application in test mode
**`client`** - Flask test client for API requests

## 🏷️ Test Markers

Use markers to run specific test categories:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow-running tests
@pytest.mark.api           # Tests requiring API access
```

**Run by marker:**
```bash
pytest -m "unit and not slow"
pytest -m "integration"
```

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

### Stop at First Failure
```bash
pytest -x
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Debug with PDB
```bash
pytest --pdb
```

## 📝 Writing New Tests

### Unit Test Template

```python
import pytest

@pytest.mark.unit
class TestYourComponent:
    """Test suite for YourComponent"""

    def test_basic_functionality(self, your_fixture):
        """Test description"""
        # Arrange
        expected = "something"

        # Act
        result = your_fixture.do_something()

        # Assert
        assert result == expected
```

### Integration Test Template

```python
import pytest
from unittest.mock import patch

@pytest.mark.integration
class TestYourWorkflow:
    """Integration test for your workflow"""

    @patch('module.external_dependency')
    def test_complete_workflow(self, mock_dep, client):
        """Test complete workflow"""
        # Mock external dependency
        mock_dep.return_value = "mocked_data"

        # Make request
        response = client.post('/api/endpoint', json={})

        # Verify
        assert response.status_code == 200
```

## 🔍 Code Quality Checks

### Linting (Flake8)
```bash
flake8 app.py services/ tests/
```

### Code Formatting (Black)
```bash
# Check formatting
black --check app.py services/ tests/

# Auto-format
black app.py services/ tests/
```

### Type Checking (MyPy)
```bash
mypy app.py services/ --ignore-missing-imports
```

## 🎯 CI/CD Integration

Tests run automatically on:
- Every push to `main`, `develop`, or `claude/*` branches
- Every pull request

**GitHub Actions Workflow:**
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Generates coverage reports
- Uploads to Codecov
- Code quality checks

**View Results:**
- GitHub Actions tab
- Pull request checks
- Codecov dashboard

## 🚦 Pre-Commit Checklist

Before committing code:

```bash
# 1. Run all tests
pytest

# 2. Check coverage
pytest --cov=app --cov=services --cov-fail-under=80

# 3. Format code
black app.py services/ tests/

# 4. Lint code
flake8 app.py services/ tests/

# 5. Run full test script
./run_tests.sh
```

## 📚 Best Practices

### ✅ Do's

- Write tests for all new features
- Mock external dependencies (ECB API)
- Use descriptive test names
- Keep tests fast and isolated
- Test both success and error cases
- Use fixtures to reduce duplication
- Maintain 80%+ code coverage

### ❌ Don'ts

- Don't test external APIs directly
- Don't write slow tests without `@pytest.mark.slow`
- Don't commit failing tests
- Don't skip tests without good reason
- Don't duplicate test code (use fixtures)

## 🔧 Troubleshooting

### Import Errors

```bash
# Ensure you're in the right directory
cd python-webapp

# Install all dependencies
pip install -r requirements-dev.txt
```

### Coverage Not Working

```bash
# Reinstall pytest-cov
pip install --upgrade pytest-cov
```

### Tests Failing Locally

```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements-dev.txt
```

## 📖 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)

---

**Maintained by**: PCA Yield Curve App Team
**Last Updated**: 2025-12-06
