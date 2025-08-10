// ---------------------------------------------
// This is a Jenkins pipeline script for a sample Flask application.
// This is a personal project to demonstrate a complete CI/CD pipeline using Gitea, Jenkins, Docker, and Kubernetes.
// ---------------------------------------------
pipeline {
    agent any

    environment {
        REGISTRY_URL = 'localhost:5000'
        IMAGE_NAME = 'sample-flask-app'

        AWS_Region = 'ap-south-1'
        ECR_REPO_URI = '008679543675.dkr.ecr.ap-south-1.amazonaws.com/sample-flask-app'
        K8S_NAMESPACE = 'default'
        K8S_DEPLOYMENT_NAME = 'flask-app-deployment'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out latest code from Gitea'
                git url: 'http://gitea-server:3000/admin/sample-flask-app.git', branch: 'main'
            }
        }

        stage('Build and Push to ECR') {
            steps {
                echo 'Building and pushing the Docker image to ECR...'
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    def fullImageName = "${ECR_REPO_URI}:${imageTag}"

                    docker.build(fullImageName, '.')

                    // Log in to ECR and push image
                    withAWS(region: AWS_REGION) {
                        sh """
                    aws ecr get-login-password --region ${AWS_REGION} \
                    | docker login --username AWS --password-stdin ${ECR_REPO_URI}
                """
                        docker.image(fullImageName).push()
                    }
                }
            }
            stage('Deploy') {
                // For now, this stage will be a placeholder.
                // We'll deploy to the K8s node in the next step.
                steps {
                    echo 'Deployment to K8s node would happen here.'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            script {
                sh 'docker image prune -f'
            }
        }
    }
}
