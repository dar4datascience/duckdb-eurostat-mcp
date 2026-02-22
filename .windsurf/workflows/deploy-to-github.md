---
description: Deploy the DuckDB Eurostat MCP server to GitHub and set up CI/CD
auto_execution_mode: 2
---

# Deploy to GitHub Workflow

This workflow guides you through pushing your code to GitHub and setting up continuous integration.

## Steps

### 1. Initialize Git repository (if not already done)

// turbo
```bash
git init
```

### 2. Add all files to Git

// turbo
```bash
git add .
```

### 3. Create initial commit

```bash
git commit -m "Initial commit: DuckDB Eurostat MCP server with natural language query support"
```

### 4. Create GitHub repository

Go to https://github.com/new and create a new repository named `duckdb-eurostat-mcp`.

**Do not** initialize with README, .gitignore, or license (we already have these).

### 5. Add GitHub remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/duckdb-eurostat-mcp.git
```

Replace `YOUR_USERNAME` with your GitHub username.

### 6. Push to GitHub

```bash
git branch -M main
git push -u origin main
```

### 7. Set up GitHub Actions for CI

The repository should include a `.github/workflows/ci.yml` file. If not, create it with the workflow configuration.

### 8. Add repository secrets

Go to your GitHub repository settings → Secrets and variables → Actions, and add:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (for integration tests)

### 9. Enable GitHub Pages (optional)

For hosting test coverage reports:
1. Go to repository Settings → Pages
2. Select source: GitHub Actions
3. Coverage reports will be available after CI runs

### 10. Create a release

```bash
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

### 11. Update README badges

Add status badges to your README.md:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/duckdb-eurostat-mcp/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/duckdb-eurostat-mcp/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

## Continuous Integration

The CI workflow will:
- Run on every push and pull request
- Test on Python 3.10, 3.11, and 3.12
- Run linting (ruff, black)
- Run type checking (mypy)
- Run all tests with coverage
- Generate coverage reports

## Publishing to PyPI (Optional)

### 12. Build the package

```bash
pip install build
python -m build
```

### 13. Upload to PyPI

```bash
pip install twine
twine upload dist/*
```

You'll need PyPI credentials. Consider using API tokens for security.

## Collaboration

### 14. Set up branch protection

In GitHub repository settings → Branches:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date

### 15. Create CONTRIBUTING.md

Add guidelines for contributors on how to:
- Set up development environment
- Run tests
- Submit pull requests
- Code style requirements
