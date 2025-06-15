# TravelPal - AI-Powered Travel Assistant

## Project Structure

```
.
├── backend/           # FastAPI backend application
├── frontend/          # React frontend application
├── infra/             # Infrastructure as Code (Terraform)
│   └── terraform/
│       ├── k8s/      # Kubernetes configurations
│       ├── db/        # Database configurations
│       └── storage/   # Storage configurations
└── .github/workflows/ # GitHub Actions workflows
```

## Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Terraform 1.5+

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/AINative-Studio/travelpal.git
   cd travelpal
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

4. Start the development environment:
   ```bash
   docker-compose up -d
   ```

## CI/CD

GitHub Actions workflows are configured for:
- Linting (Python & JavaScript/TypeScript)
- Testing
- Docker image building
- Infrastructure deployment (on main branch)

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `make test`
4. Push your branch and open a Pull Request
