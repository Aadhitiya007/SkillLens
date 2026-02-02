# Contributing to SkillLens

Thank you for your interest in contributing to SkillLens! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## 🐛 Reporting Issues

Before creating an issue, please:
- Check if the issue already exists
- Provide a clear and descriptive title
- Include steps to reproduce the problem
- Specify your environment (OS, Python version, Node.js version)
- Include relevant logs or error messages

## 💡 Suggesting Features

We welcome feature suggestions! Please:
- Check if the feature has already been suggested
- Clearly describe the feature and its benefits
- Explain how it aligns with SkillLens's goals
- Provide examples or mockups if applicable

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose (optional)

### Local Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SkillLens.git
   cd SkillLens
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Backend setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Frontend setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Database setup**
   - See [LOCAL_SETUP_WINDOWS.md](LOCAL_SETUP_WINDOWS.md) for detailed instructions
   - Or use Docker: `docker-compose up -d`

## 📝 Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Open a pull request on GitHub
   - Provide a clear description of changes
   - Link related issues
   - Wait for review

## 🎨 Code Style Guidelines

### Python (Backend)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions and classes

### TypeScript/React (Frontend)
- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Keep components small and focused
- Use meaningful component and variable names

### General
- Write self-documenting code
- Add comments for complex logic
- Keep functions small and single-purpose
- Avoid code duplication

## 🧪 Testing Guidelines

- Write unit tests for new features
- Maintain or improve code coverage
- Test edge cases and error handling
- Use descriptive test names

## 📚 Documentation

When adding features:
- Update relevant README sections
- Add API documentation for new endpoints
- Update type definitions
- Include examples where helpful

## 🔍 Review Process

All pull requests require:
- Passing CI/CD checks
- Code review approval
- No merge conflicts
- Updated documentation

## 🚀 Release Process

Releases are managed by maintainers. Contributors should:
- Keep PRs focused and atomic
- Follow semantic versioning principles
- Update CHANGELOG.md if applicable

## ❓ Questions?

- Open an issue for general questions
- Check existing documentation first
- Be patient and respectful

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to SkillLens!** 🎉
