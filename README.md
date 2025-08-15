# Terravision UI

A modern web interface for [Terravision](https://github.com/patrickchugh/terravision) - visualize your Terraform infrastructure as beautiful diagrams. Built with Next.js and Flask, this application provides an intuitive way to generate, validate, and view Terraform resource graphs.

## ✨ Features

- 🎨 **Interactive Terraform Editor** - Edit your configuration files in the browser
- 📊 **Graph Visualization** - Generate beautiful architecture diagrams from Terraform code
- ✅ **Configuration Validation** - Validate Terraform syntax and configuration
- 🐳 **Docker Ready** - Complete containerized setup with Docker Compose
- 🔄 **Real-time Updates** - Live console output during graph generation
- 📱 **Responsive Design** - Works on desktop and mobile devices

## 📸 Screenshots

### Main Application Interface

![Terravision UI](./public/terravision-ui.png)

### Example Generated Diagram

![Example Architecture Diagram](./public/diagram.png)

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- Node.js v18+ and pnpm (for local development)

### Get Running in 30 seconds

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd terravision-ui
   ```

2. **Start all services**

   ```bash
   # Build and start both frontend and backend
   docker compose up --build -d
   ```

3. **Access the application**
   - 🌐 **Frontend**: http://localhost:3000
   - 🔧 **Backend API**: http://localhost:8001
   - ❤️ **Health Check**: http://localhost:8001/health

### Verify Installation

Run the automated integration test:

```bash
# Run complete workflow test
./scripts/integration-test.sh
```

## 🛠️ Development Setup

### Local Development

```bash
# Install dependencies
pnpm install

# Start development server (frontend only)
pnpm dev

# Start backend separately
cd terravision && python app.py
```

### Docker Development

```bash
# Start with live reloading
docker compose -f docker-compose.dev.yml up --build

# View logs
docker compose logs -f

# Rebuild after changes
docker compose down -v --remove-orphans
docker compose up --build -d
```

## 📡 API Usage

### Endpoints Overview

| Endpoint                    | Method | Description                            |
| --------------------------- | ------ | -------------------------------------- |
| `/api/terravision/graph`    | POST   | Generate Terraform graph visualization |
| `/api/terravision/validate` | POST   | Validate Terraform configuration       |
| `/api/terravision/output`   | GET    | Download generated diagram image       |

### Example Usage

#### 1. Generate Infrastructure Diagram

```bash
curl -X POST http://localhost:3000/api/terravision/graph \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json \
  -o graph-output.txt
```

#### 2. Validate Configuration

```bash
curl -X POST http://localhost:3000/api/terravision/validate \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json \
  -o validation-output.txt
```

#### 3. Download Generated Diagram

```bash
# Get the diagram image
curl -X GET http://localhost:3000/api/terravision/output \
  -o infrastructure-diagram.png

# Check if diagram is ready
curl -I http://localhost:3000/api/terravision/output
```

### Sample Terraform Configuration

The repository includes example configurations in `examples/`:

- `terraform-aws-s3.json` - AWS S3 bucket with versioning

**Example payload structure:**

```json
{
  "main.tf": {
    "name": "main.tf",
    "language": "hcl",
    "value": "terraform {\n  required_providers {\n    aws = {\n      source = \"hashicorp/aws\"\n      version = \"~> 5.0\"\n    }\n  }\n}\n\nprovider \"aws\" {\n  region = \"us-east-1\"\n}\n\nresource \"aws_s3_bucket\" \"example\" {\n  bucket = var.bucket_name\n}"
  },
  "variables.tf": {
    "name": "variables.tf",
    "language": "hcl",
    "value": "variable \"bucket_name\" {\n  description = \"S3 bucket name\"\n  type = string\n  default = \"my-terraform-bucket\"\n}"
  }
}
```

## 🧪 Testing & Verification

### Automated Integration Test

Run the complete workflow test:

```bash
./scripts/integration-test.sh
```

This script will:

- ✅ Start all services with fresh containers
- ✅ Wait for services to be healthy
- ✅ Test graph generation endpoint
- ✅ Test validation endpoint
- ✅ Test diagram output retrieval
- 📊 Generate test result files

### Manual Testing Sequence

```bash
# 1. Start services
docker compose down -v --remove-orphans
docker compose up --build -d

# 2. Wait for health check
sleep 30 && curl http://localhost:8001/health

# 3. Test endpoints
curl -X POST http://localhost:3000/api/terravision/graph \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json

curl -X POST http://localhost:3000/api/terravision/validate \
  -H "Content-Type: application/json" \
  -d @examples/terraform-aws-s3.json

# 4. Check diagram output
curl -I http://localhost:3000/api/terravision/output
```

### Test Results

After running tests, you'll find these generated files:

- `graph-output.txt` - Terraform graph generation logs
- `validation-output.txt` - Configuration validation results
- `infrastructure-diagram.png` - Generated architecture diagram

## 🔧 Service Management

### Docker Compose Commands

```bash
# Start services (with rebuild)
docker compose down -v --remove-orphans && docker compose up --build -d

# Stop all services
docker compose down -v --remove-orphans

# View service status
docker compose ps

# Follow logs (all services)
docker compose logs -f

# Follow logs (specific service)
docker compose logs -f terravision-api
docker compose logs -f terravision-ui

# Restart specific service
docker compose restart terravision-api
```

### Health Monitoring

```bash
# Check backend health
curl http://localhost:8001/health

# Check service status
docker compose ps

# Monitor resource usage
docker stats terravision-api terravision-ui
```

## 🐛 Troubleshooting

### Common Issues

**Services won't start:**

```bash
# Check for port conflicts
netstat -tlnp | grep :3000
netstat -tlnp | grep :8001

# Force clean restart
docker compose down -v --remove-orphans
docker system prune -f
docker compose up --build --force-recreate -d
```

**Network connectivity issues:**

```bash
# Test backend from frontend container
docker exec -it terravision-ui curl http://terravision-api:8001/health

# Test backend directly
docker exec -it terravision-api curl http://localhost:8001/health

# Check Docker network
docker network ls
docker network inspect terravision-ui_terravision-network
```

**Missing diagram output:**

```bash
# Check if terraform/graphviz tools are available
docker exec -it terravision-api terraform --version
docker exec -it terravision-api dot -V

# Check shared volume
docker exec -it terravision-api ls -la /data/
docker volume inspect terravision-ui_shared-data
```

### Debug Commands

```bash
# Container logs with timestamp
docker compose logs -f --timestamps

# Execute commands in containers
docker exec -it terravision-api bash
docker exec -it terravision-ui sh

# Check container processes
docker exec -it terravision-api ps aux
docker exec -it terravision-ui ps aux

# Inspect container environment
docker exec -it terravision-api env
docker exec -it terravision-ui env
```

## 🏗️ Architecture

### Components

- **Frontend (Next.js)**: User interface and API proxy
  - Monaco Editor for Terraform file editing
  - Real-time console output display
  - Responsive design with Tailwind CSS

- **Backend (Flask)**: Terraform processing and graph generation
  - Terraform validation and graph generation
  - File I/O for configuration management
  - Stream processing for real-time output

- **Shared Volume**: Data persistence between containers
  - Terraform configuration files
  - Generated diagrams and outputs
  - Temporary processing files

### Network Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser       │    │   Frontend       │    │   Backend       │
│   :3000         ├────┤   terravision-ui ├────┤   terravision-  │
│                 │    │   (Next.js)      │    │   api (Flask)   │
└─────────────────┘    └──────────────────┘    │   :8001         │
                                               └─────────────────┘
                                                         │
                                                ┌─────────────────┐
                                                │  Shared Volume  │
                                                │  /data          │
                                                │  - configs/     │
                                                │  - outputs/     │
                                                │  - examples/    │
                                                └─────────────────┘
```

## 🔒 Security Notes

- The application is designed for local development and testing
- Terraform configurations are processed in isolated containers
- No sensitive data is persisted beyond container lifecycle
- All API endpoints are intended for local network access only

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request