# Contributing to Kubernetes-Project-2026

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🎯 Ways to Contribute

- **Report bugs** and request features via Issues
- **Improve documentation** with clearer explanations or examples
- **Submit code** improvements or new features via Pull Requests
- **Share knowledge** by helping others in Discussions
- **Spread the word** by starring the repo and sharing with others

## 🚀 Getting Started

1. **Fork the repository**
   - Click the "Fork" button at the top right of this page

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Kubernetes-Project-2026.git
   cd Kubernetes-Project-2026
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
   ```

4. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

### Prerequisites

- Docker
- Minikube or Kind
- kubectl
- Git

### Local Development

```bash
# Start with Docker Compose for fast iteration
docker-compose up -d

# Make your changes in apps/frontend or apps/backend

# Test your changes
docker-compose restart backend
docker-compose logs -f backend
```

### Testing in Kubernetes

```bash
# Start Minikube
minikube start

# Use Minikube's Docker
eval $(minikube docker-env)

# Build images
docker build -t backend:latest ./apps/backend
docker build -t frontend:latest ./apps/frontend

# Deploy
kubectl apply -f k8s/dev/

# Test
kubectl get pods -n ecommerce-dev
```

## 📝 Pull Request Process

1. **Ensure your code works**
   - Test locally with Docker Compose
   - Test in Minikube/Kind
   - Check logs for errors

2. **Update documentation**
   - Update README if adding features
   - Add comments to complex code
   - Update relevant .md files in docs/

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Submit

## ✅ Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New feature or file
- **Update**: Modification to existing feature
- **Fix**: Bug fix
- **Refactor**: Code restructuring without behavior change
- **Docs**: Documentation changes
- **Style**: Code style/formatting changes
- **Test**: Adding or updating tests

Examples:
```
Add: New API endpoint for product search
Update: Improve error handling in backend
Fix: Database connection timeout issue
Docs: Add troubleshooting section to README
```

## 🎨 Code Style

### Python Code
- Follow PEP 8 style guide
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and small

### Kubernetes Manifests
- Use consistent indentation (2 spaces)
- Add comments for complex configurations
- Follow naming conventions:
  - lowercase with hyphens
  - descriptive names

### Shell Scripts
- Add comments explaining complex logic
- Use meaningful variable names
- Include error handling
- Make scripts executable

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:
   - OS (Linux/Mac/Windows)
   - Kubernetes version
   - Docker version
   - Minikube/Kind version
6. **Logs**: Relevant error logs
7. **Screenshots**: If applicable

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
1. Go to '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: Ubuntu 22.04
- Kubernetes: v1.28
- Docker: 24.0.6
- Minikube: v1.32.0

**Logs**
```
Paste relevant logs here
```

**Screenshots**
If applicable, add screenshots.
```

## 💡 Suggesting Features

When suggesting features, include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Additional context**: Any other relevant information

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Any other context about the feature request.
```

## 📚 Documentation Contributions

Documentation is just as important as code!

- Fix typos and grammar
- Add missing information
- Improve clarity of explanations
- Add examples and use cases
- Create tutorials or guides

## 🧪 Testing

Before submitting PR:

1. **Test locally**
   ```bash
   docker-compose up -d
   # Test the application
   docker-compose down
   ```

2. **Test in Minikube**
   ```bash
   ./scripts/setup-minikube.sh
   # Verify everything works
   ```

3. **Check logs**
   ```bash
   kubectl logs -f deployment/backend -n ecommerce-dev
   ```

4. **Verify functionality**
   - Test all modified features
   - Check for error messages
   - Verify health checks

## 🔐 Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email the maintainers directly
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## 💬 Questions?

- Open a GitHub Discussion for general questions
- Check existing Issues and PRs
- Read the documentation in `/docs`
- Review the [QUICKSTART.md](QUICKSTART.md) guide

## 🌟 Recognition

Contributors will be:
- Listed in the project's contributors page
- Mentioned in release notes (for significant contributions)
- Appreciated in the community!

Thank you for contributing to make this project better! 🚀

---

**Quick Links:**
- [README](README.md)
- [Quick Start](QUICKSTART.md)
- [Documentation](docs/)
- [Issues](https://github.com/Dhananjaiah/Kubernetes-Project-2026/issues)
- [Pull Requests](https://github.com/Dhananjaiah/Kubernetes-Project-2026/pulls)
