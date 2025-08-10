// ---------------------------------------------
// This is a Jenkins pipeline script for a sample Flask application.
// This is a personal project to demonstrate a complete CI/CD pipeline using Gitea, Jenkins, Docker, and Kubernetes.
// ---------------------------------------------
pipeline {
    agent any

    environment {
        REGISTRY_URL = 'localhost:5000'
        IMAGE_NAME = 'sample-flask-app'

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

        stage('Build and Push Docker Image') {
            steps {
                echo 'Building and pushing the Docker image...'
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                    docker.build(fullImageName, '.')

                    docker.image(fullImageName).push()
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to the K3s cluster!'

                // REMINDER: This 'withCredentials' block is the key to secure access
                // Dev note: It makes the 'kubeconfig-k3d' secret file available as a temp file
                // and sets the KUBECONFIG environment variable to its path.
                // FIX: change to kubeconfig-sa from kubeconfig-k3d (Dev).
                withCredentials([file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')]) {
                    script {
                        def imageTag = "build-${BUILD_NUMBER}"
                        def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                        echo "Updating Kubernetes deployment with new image: ${fullImageName}"

                        // Dev note: dynamically update the image in our deployment manifest.
                        sh "sed -i 's|image:.*|image: ${fullImageName}|' k8s/deployment.yaml"

                        echo 'Applying the new configuration to the cluster!'

                        // Dev note: '--insecure-skip-tls-verify' flag is used to bypass TLS verification.
                        // WARNING: This is not for prod env (DEV)

                        sh 'kubectl --insecure-skip-tls-verify apply -f k8s/'

                        echo 'Waiting for the deployment to complete!'
                        sh "kubectl --insecure-skip-tls-verify rollout status deployment/${K8S_DEPLOYMENT_NAME} --namespace ${K8S_NAMESPACE}"
                    }
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
