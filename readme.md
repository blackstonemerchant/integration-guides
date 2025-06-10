# Blackstone Payment Integration Guides

📚 Comprehensive developer documentation for Blackstone payment integration services, built with Material for MkDocs.

## 🚀 Quick Start

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Python 3.12+
- Make (usually pre-installed on macOS/Linux)

### Installation & Development

1. **Clone and setup**:

   ```bash
   git clone <your-repo-url>
   cd integration-guides
   make dev-setup
   ```

2. **Start development server**:

   ```bash
   make serve
   # or the short alias:
   make s
   ```

   📝 Documentation will be available at <http://127.0.0.1:8000> with live reload

3. **Build for production**:

   ```bash
   make build
   # or the short alias:
   make b
   ```

   🎉 Static files will be in the `site/` directory

## 📋 Available Commands

Run `make help` to see all available commands:

| Command | Description |
|---------|-------------|
| `make serve` | Start development server with live reload |
| `make build` | Build documentation for production |
| `make clean` | Clean build artifacts and cache |
| `make lint` | Check documentation for issues |
| `make install` | Install dependencies using uv |
| `make dev-setup` | Complete development environment setup |
| `make check-deps` | Check for dependency updates |

### Quick Aliases

- `make s` → `make serve`
- `make b` → `make build`
- `make c` → `make clean`

## 📁 Project Structure

```
integration-guides/
├── docs/                          # Documentation source
│   ├── index.md                   # Homepage
│   ├── payment-integration/       # Payment integration guides
│   │   ├── payment-links.md       # Payment Links API guide
│   │   └── ath-mobile-payment-button.md
│   ├── security/                  # Security guides
│   │   └── three-domain-secure.md # 3D Secure integration
│   ├── api/                       # API reference
│   │   ├── authentication.md      # Authentication guide
│   │   └── error-codes.md         # Error codes reference
│   ├── stylesheets/              # Custom CSS
│   │   └── extra.css
│   └── javascripts/              # Custom JavaScript
│       └── mathjax.js
├── mkdocs.yml                    # MkDocs configuration
├── pyproject.toml               # uv project configuration
├── Makefile                     # Build automation
└── README.md                    # This file
```

## 🎨 Features

### Material for MkDocs Features

- **Modern Design**: Beautiful, responsive Material Design
- **Dark/Light Mode**: Automatic theme switching
- **Code Highlighting**: Syntax highlighting for multiple languages
- **Search**: Full-text search functionality
- **Navigation**: Tabbed navigation with auto-generated ToC
- **Mobile Friendly**: Fully responsive design

### Custom Enhancements

- **Grid Cards**: Interactive card layouts for better UX
- **Code Tabs**: Multi-language code examples
- **Custom Styling**: Enhanced visual design
- **MathJax Support**: Mathematical expressions
- **Admonitions**: Warning, tip, and info blocks

## 🔧 Configuration

### MkDocs Configuration

The site is configured via `mkdocs.yml`:

- **Theme**: Material with custom color scheme
- **Extensions**: Code highlighting, tabs, admonitions, MathJax
- **Navigation**: Organized by feature areas
- **Plugins**: Search, minify for optimization

### uv Configuration

Dependencies are managed via `pyproject.toml`:

- **Core Dependencies**: MkDocs, Material theme, extensions
- **Dev Dependencies**: Additional development tools
- **Python Version**: 3.8+ requirement

## 📖 Writing Documentation

### Adding New Pages

1. Create markdown files in the appropriate `docs/` subdirectory
2. Update the `nav` section in `mkdocs.yml`
3. Use Material for MkDocs features:

```markdown
# Page Title

## Section with Admonition

!!! tip "Pro Tip"
    This is a helpful tip for developers

## Code Examples with Tabs

=== "JavaScript"
    ```javascript
    const response = await fetch('/api/endpoint');
    ```

=== "Python"
    ```python
    response = requests.get('/api/endpoint')
    ```
```

### Markdown Extensions

Available extensions:

- **Admonitions**: `!!! tip`, `!!! warning`, `!!! info`
- **Code Blocks**: Syntax highlighting and line numbers
- **Tables**: Enhanced table formatting
- **Tabs**: `=== "Tab Name"`
- **Grid Cards**: Custom card layouts
- **Icons**: Material Design icons

## 🚀 Deployment

### GitHub Pages

1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Push to main branch - GitHub Actions will build and deploy

### Manual Deployment

1. Build the site: `make build`
2. Deploy the `site/` directory to your web server
3. Configure your web server to serve static files

### Docker Deployment

```dockerfile
FROM nginx:alpine
COPY site/ /usr/share/nginx/html/
EXPOSE 80
```

## 🔍 Development Tips

### Live Reload

The development server (`make serve`) automatically reloads when you edit files.

### Checking for Issues

Use `make lint` to build with strict mode and catch configuration issues.

### Performance

The built site is optimized with:

- Minified HTML/CSS/JS
- Optimized images
- Efficient navigation structure

## 🆘 Troubleshooting

### Common Issues

**uv not found**:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Make not found (Windows)**:

- Install [Make for Windows](http://gnuwin32.sourceforge.net/packages/make.htm)
- Or use [Chocolatey](https://chocolatey.org/): `choco install make`

**Build failures**:

```bash
make clean  # Clean build artifacts
make lint   # Check for issues
```

## 📄 License

Copyright © 2024 Blackstone Payment Integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `make serve`
5. Build with `make build`
6. Submit a pull request

---

Built with ❤️ using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and [uv](https://github.com/astral-sh/uv)
