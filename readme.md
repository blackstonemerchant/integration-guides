# Bpayd Documentation

📚 Developer documentation for Bpayd payment integration services.

## 🚀 Quick Start

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Python 3.12+
- Make

### Development

1. **Setup and start development server**:

   ```bash
   git clone https://github.com/blackstonemerchant/integration-guides.git
   cd integration-guides
   make dev-setup
   make serve
   ```

   Documentation will be available at <http://127.0.0.1:8000> with hot-reload.

2. **Build for production**:

   ```bash
   make build
   ```

## 📋 Available Commands

Run `make help` to see all available commands.

**Most common commands:**

- `make serve` (alias: `make s`) - Start development server
- `make build` (alias: `make b`) - Build documentation
- `make clean` (alias: `make c`) - Clean build artifacts
- `make generate-api-reference` - Regenerate native API pages from Swagger/OpenAPI

## 📖 Writing Documentation

1. Create markdown files in the `docs/` directory
2. Update the `nav` section in `zensical.toml` if needed
3. Use [Zensical](https://zensical.org/) features for enhanced formatting

The API reference under `docs/core-apis/api-reference/` is generated and must not be edited manually. `make serve`, `make build`, and `make lint` refresh it from `https://services.bmspay.com/swagger/docs/v1` before Zensical runs.

## 🚀 Deployment

The documentation is built with Zensical and deployed with Dokploy.

### Dokploy

Create an **Application** connected to the private `CyC-miami/bpayd-docs` repository and configure:

- Branch: `main`
- Build type: `Dockerfile`
- Dockerfile path: `Dockerfile`
- Container port: `8080`
- Health check path: `/healthz`
- Domain: `documentation.bmspay.com`
- Domain path: `/`

The Docker build downloads the published Swagger/OpenAPI contract, generates the native API reference, runs a strict Zensical build, and copies the resulting static site into a minimal Caddy image. The default OpenAPI source is `https://services.bmspay.com/swagger/docs/v1`; it can be overridden with the `BPAYD_OPENAPI_SOURCE` Docker build argument.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `make serve`
5. Submit a pull request

---

Built with [Zensical](https://zensical.org/) and [uv](https://github.com/astral-sh/uv)
