@echo off
REM Test runner script for PCA Yield Curve Application (Windows)
REM Runs all tests with coverage reporting

echo ==================================================
echo PCA Yield Curve App - Test Suite
echo ==================================================
echo.

REM Install test dependencies
echo 📦 Installing test dependencies...
pip install -q -r requirements-dev.txt
echo ✅ Dependencies installed
echo.

REM Run unit tests
echo ==================================================
echo Running Unit Tests
echo ==================================================
pytest -v -m unit --cov=app --cov=services --cov-report=term-missing --cov-report=html
echo.

REM Run integration tests
echo ==================================================
echo Running Integration Tests
echo ==================================================
pytest -v -m integration --cov=app --cov=services --cov-append --cov-report=term-missing --cov-report=html
echo.

REM Run all tests
echo ==================================================
echo Running All Tests
echo ==================================================
pytest -v --cov=app --cov=services --cov-report=term-missing --cov-report=html --cov-fail-under=80
echo.

REM Code quality checks
echo ==================================================
echo Code Quality Checks
echo ==================================================

echo 🔍 Checking code formatting (Black)...
black --check app.py services\ tests\
echo.

echo 🔍 Linting (Flake8)...
flake8 app.py services\ tests\ --max-line-length=127 --exclude=venv,vendor
echo.

REM Summary
echo ==================================================
echo Test Summary
echo ==================================================
echo ✅ All tests completed!
echo.
echo 📊 Coverage report: htmlcov\index.html
echo    Open the file in your browser
echo.
echo ==================================================

pause
