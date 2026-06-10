pipeline {
    agent any

    environment {
        APP_NAME    = "flask-bg"
        BUILD_VER   = "2.0.${BUILD_NUMBER}"
        GREEN_PORT  = "5002"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Starting Blue-Green deployment version ${BUILD_VER}"
            }
        }

        stage('Build Green image') {
            steps {
                echo "Building new Green image..."
                sh "docker build -t ${APP_NAME}:green ."
                sh "docker tag ${APP_NAME}:green ${APP_NAME}:${BUILD_VER}"
                echo "Green image built: ${APP_NAME}:green"
            }
        }

        stage('Start Green container') {
            steps {
                echo "Starting Green container on port ${GREEN_PORT}..."
                sh "docker stop green || true"
                sh "docker rm green || true"
                sh """
                    docker run -d \
                        --name green \
                        --network blue-green-demo_bg-network \
                        -e APP_VERSION=${BUILD_VER} \
                        -e APP_COLOR=green \
                        -p ${GREEN_PORT}:5000 \
                        ${APP_NAME}:green
                """
                echo "Green container started"
            }
        }

        stage('Health check Green') {
            steps {
                echo "Running health check on Green..."
                sh "sleep 5"
                sh """
                    docker exec green python3 -c "
import urllib.request, json
res = urllib.request.urlopen('http://localhost:5000/health')
data = json.loads(res.read())
print('Health check response:', data)
assert data['status'] == 'healthy', 'Health check failed!'
assert data['color'] == 'green', 'Wrong container!'
print('Green health check PASSED!')
"
                """
            }
        }

        stage('Switch traffic to Green') {
            steps {
                echo "Switching Nginx traffic from Blue to Green..."
                sh '''
                    docker exec nginx-proxy sh -c "cat > /etc/nginx/conf.d/default.conf << NGINX
upstream active {
    server green:5000;
}
server {
    listen 80;
    location / {
        proxy_pass http://active;
    }
}
NGINX"
                '''
                sh "docker exec nginx-proxy nginx -s reload"
                echo "Traffic switched to Green!"
            }
        }

        stage('Verify live traffic') {
            steps {
                echo "Verifying Green is serving live traffic..."
                sh "sleep 3"
                sh "docker exec nginx-proxy wget -qO- http://localhost/health"
                echo "Green is live and serving traffic!"
            }
        }

        stage('Decommission Blue') {
            steps {
                echo "Decommissioning Blue..."
                sh "docker stop blue || true"
                sh "docker rm blue || true"
                sh "docker tag ${APP_NAME}:green ${APP_NAME}:blue"
                echo "Blue updated. Ready for next deployment."
            }
        }
    }

    post {
        success {
            echo "Blue-Green deployment SUCCESS! Version ${BUILD_VER} is live."
        }
        failure {
            echo "Deployment FAILED — Blue environment remains live!"
            sh "docker stop green || true"
            sh "docker rm green || true"
            echo "Green rolled back. Blue is still serving traffic."
        }
        always {
            echo "Pipeline complete."
        }
    }
}
