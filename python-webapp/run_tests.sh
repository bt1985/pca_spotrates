#!/bin/bash

# Test runner script for PCA Yield Curve Application
# Runs all tests with coverage reporting

set -e  # Exit on error

echo "=================================================="
echo "PCA Yield Curve App - Test Suite"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
    echo ""
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -q -r requirements-dev.txt
echo "✅ Dependencies installed"
echo ""

# Run unit tests
echo "=================================================="
echo "Running Unit Tests"
echo "=================================================="
pytest -v -m unit --cov=app --cov=services --cov-report=term-missing --cov-report=html
echo ""

# Run integration tests
echo "=================================================="
echo "Running Integration Tests"
echo "=================================================="
pytest -v -m integration --cov=app --cov=services --cov-append --cov-report=term-missing --cov-report=html
echo ""

# Run all tests
echo "=================================================="
echo "Running All Tests"
echo "=================================================="
pytest -v --cov=app --cov=services --cov-report=term-missing --cov-report=html --cov-fail-under=80
echo ""

# Code quality checks
echo "=================================================="
echo "Code Quality Checks"
echo "=================================================="

echo "🔍 Checking code formatting (Black)..."
black --check app.py services/ tests/ || echo "⚠️  Code formatting issues found. Run: black app.py services/ tests/"
echo ""

echo "🔍 Linting (Flake8)..."
flake8 app.py services/ tests/ --max-line-length=127 --exclude=venv,vendor || echo "⚠️  Linting issues found"
echo ""

# Summary
echo "=================================================="
echo "Test Summary"
echo "=================================================="
echo "✅ All tests completed!"
echo ""
echo "📊 Coverage report: htmlcov/index.html"
echo "   Open with: open htmlcov/index.html (Mac) or xdg-open htmlcov/index.html (Linux)"
echo ""
echo "=================================================="
