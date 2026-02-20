# Contributing to Veditor AI 🎬

Thank you for your interest in contributing to Veditor AI! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

## Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/yourusername/Veditor.git
cd Veditor
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Set Up Development Environment

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Development Workflow

### Backend Development

1. Make changes to Python files
2. Test locally: `python app.py`
3. Run linting: `pylint backend/`
4. Commit with clear messages

### Frontend Development

1. Make changes to TypeScript/React files
2. Test locally: `npm run dev`
3. Check for TypeScript errors: `npm run type-check`
4. Commit with clear messages

## Areas for Contribution

### High Priority
- [ ] GPU optimization and CUDA support
- [ ] Performance profiling and optimization
- [ ] Bug fixes (see Issues)
- [ ] Documentation improvements

### Medium Priority
- [ ] Additional AI models
- [ ] UI/UX enhancements
- [ ] Test coverage
- [ ] Error handling improvements

### Nice to Have
- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] CI/CD pipeline improvements
- [ ] Example scripts and tutorials

## Submitting Changes

### 1. Commit Guidelines

```bash
# Good commit messages
git commit -m "feat: add GPU support for inference"
git commit -m "fix: resolve audio sync issue in FFmpeg"
git commit -m "docs: update installation guide"

# Format: type(scope): description
# Types: feat, fix, docs, style, refactor, perf, test, chore
```

### 2. Push & Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots/videos if applicable
- Testing instructions

### 3. Code Review

- Address feedback promptly
- Ask questions if unclear
- Be open to suggestions
- Update PR based on review

## Testing

### Backend Tests

```bash
# Run tests
pytest backend/tests/

# With coverage
pytest --cov=backend backend/tests/
```

### Frontend Tests

```bash
# Run tests
npm run test

# With coverage
npm run test:coverage
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions
- Update ROADMAP.md for feature additions
- Include examples for new features

## Performance Considerations

- Profile code before optimizing
- Benchmark changes against baseline
- Document performance improvements
- Consider memory usage

## Security

- Don't commit secrets or API keys
- Use environment variables for sensitive data
- Report security issues privately
- Follow OWASP guidelines

## Questions?

- Open an issue for discussions
- Join our Discord community
- Check existing documentation
- Ask in PR comments

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in community channels

---

Thank you for making Veditor AI better! 🚀
