# Blue-Green Deployment Demo

A production-grade Blue-Green deployment pipeline built with Jenkins, Docker, and Nginx.

## What it does
- Deploys a new version (Green) alongside the live version (Blue)
- Runs automated health checks on Green before any traffic is shifted
- Switches 100% of traffic instantly via Nginx upstream config reload
- Rolls back automatically if health check fails — Blue stays live
- Zero downtime for end users throughout the entire deployment

## Architecture

User → Nginx (port 8090)
↓
Points to either:
├── Blue container (port 5001) ← previous version
└── Green container (port 5002) ← new version

## Tech Stack
- Python 3.11 + Flask (web application)
- Nginx (reverse proxy / traffic switcher)
- Docker (containerization)
- Jenkins (CI/CD pipeline orchestration)
- GitHub (Pipeline as Code via Jenkinsfile)

## Pipeline Stages
1. **Checkout SCM** — pulls latest Jenkinsfile and code from GitHub
2. **Build Green image** — builds new Docker image tagged as green and versioned
3. **Start Green container** — runs Green on port 5002, hidden from users
4. **Health check Green** — validates Green is healthy before any traffic shift
5. **Switch traffic to Green** — updates Nginx upstream config and reloads
6. **Verify live traffic** — confirms Green is responding correctly
7. **Decommission Blue** — stops Blue, tags Green as new Blue for next cycle

## Rollback Strategy
If any stage fails after Green starts:
- Green container is automatically stopped and removed
- Blue continues serving 100% of traffic uninterrupted
- No manual intervention required

## How to run locally

### Prerequisites
- Docker Desktop
- Jenkins running via Docker

### Bootstrap Blue environment (first time only)
```bash
docker build -t flask-bg:blue .
docker network create blue-green-demo_bg-network
docker run -d \
    --name blue \
    --network blue-green-demo_bg-network \
    -e APP_VERSION=1.0.0 \
    -e APP_COLOR=blue \
    -p 5001:5000 \
    flask-bg:blue
docker run -d \
    --name nginx-proxy \
    --network blue-green-demo_bg-network \
    -p 8090:80 \
    -v $(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
    nginx:alpine
```

### Trigger deployment
Run the Jenkins pipeline — app switches from Blue to Green automatically.

## Key Concepts Demonstrated
- Zero downtime deployment via instant traffic switching
- Automated health gate before traffic shift
- Automatic rollback on failure
- Nginx as a dynamic reverse proxy
- Docker networking between containers
- Pipeline as Code with Jenkinsfile

