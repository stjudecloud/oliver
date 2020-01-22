# Development

If you are interested in contributing to the code, please first review
our [CONTRIBUTING.md](../CONTRIBUTING.md) document. To bootstrap a 
development environment, please use the following commands.

```bash
# Clone the repository
git clone git@github.com:stjudecloud/oliver.git
cd oliver

# Link the package with your current Python environment
python setup.py develop

# Ensure pre-commit is installed to automatically format
# code using `black`.
brew install pre-commit
pre-commit install
```