# Contributing to Safety Checker

Thank you for your interest in contributing! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/safetychecker.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Set up development environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use Black for formatting: `black safety_checker.py`
- Use isort for imports: `isort safety_checker.py`
- Run flake8: `flake8 safety_checker.py`

### Testing
- Write tests for new features
- Run tests: `pytest tests/`
- Check coverage: `pytest --cov=safety_checker tests/`

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb: "Add", "Fix", "Update", "Remove"
- Example: "Add JWT token vulnerability detection"

### Pull Requests
- Describe what your changes do
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed

## Reporting Issues

- Use GitHub Issues for bug reports
- Include:
  - Python version
  - Operating system
  - Steps to reproduce
  - Expected vs actual behavior

## Feature Requests

- Describe the feature clearly
- Explain the use case
- Provide examples if possible

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
