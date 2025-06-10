.PHONY: help install serve build clean lint format check-deps

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	@echo "📦 Installing dependencies with uv..."
	@uv sync --all-groups --all-extras

serve: install ## Start development server with live reload
	@echo "🚀 Starting Material for MkDocs development server..."
	@echo "🌐 Documentation will be available at http://127.0.0.1:8000"
	@echo "📝 Auto-reload enabled - edit files and see changes instantly"
	@echo "❌ Press Ctrl+C to stop the server"
	@echo ""
	@uv run mkdocs serve --dev-addr=127.0.0.1:8000

build: install ## Build documentation for production
	@echo "🏗️  Building Material for MkDocs documentation for production..."
	@if [ -d "site" ]; then \
		echo "🧹 Cleaning previous build..."; \
		rm -rf site; \
	fi
	@echo "🔨 Building documentation..."
	@uv run mkdocs build
	@echo "✅ Build completed successfully!"
	@echo "📁 Static files are in the 'site' directory"
	@echo "🌐 You can deploy the 'site' directory to any web server"
	@if [ -d "site" ]; then \
		echo ""; \
		echo "📊 Build statistics:"; \
		echo "   - Total files: $$(find site -type f | wc -l)"; \
		echo "   - HTML files: $$(find site -name "*.html" | wc -l)"; \
		echo "   - CSS files: $$(find site -name "*.css" | wc -l)"; \
		echo "   - JS files: $$(find site -name "*.js" | wc -l)"; \
		echo "   - Total size: $$(du -sh site | cut -f1)"; \
	fi

clean: ## Clean build artifacts and cache
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf site/
	@rm -rf .venv/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@echo "✅ Clean completed!"

lint: install ## Check documentation for issues
	@echo "🔍 Checking documentation..."
	@uv run mkdocs build --strict --verbose

format: ## Format markdown files (if formatter is available)
	@echo "📝 Formatting would go here (add your preferred markdown formatter)"

check-deps: ## Check for dependency updates
	@echo "📋 Checking for dependency updates..."
	@uv tree

# Development helpers
dev-setup: ## Complete development environment setup
	@echo "🔧 Setting up development environment..."
	@make install
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  📖 Run 'make serve' to start the development server"
	@echo "  🏗️  Run 'make build' to build for production"

# Quick aliases
s: serve ## Alias for serve
b: build ## Alias for build
c: clean ## Alias for clean 