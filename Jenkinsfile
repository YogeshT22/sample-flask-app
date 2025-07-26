pipeline {
    agent any

    environment {
        // Define variables that will be used across stages
        REGISTRY_URL = 'localhost:5000'
        IMAGE_NAME = 'sample-flask-app'
        // The K8s deployment is in the 'default' namespace
        K8S_NAMESPACE = 'default'
        // The name of the deployment resource in our deployment.yaml
        K8S_DEPLOYMENT_NAME = 'flask-app-deployment'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out latest code from Gitea.....'
                git url: 'http://gitea-server:3000/admin/sample-flask-app.git', branch: 'main'
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                echo 'Building and pushing the Docker image...'
                script {
                    // Create a unique tag for this build
                    def imageTag = "build-${BUILD_NUMBER}"
                    def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                    // Build the image
                    docker.build(fullImageName, '.')

                    // Push the image to our local registry
                    docker.image(fullImageName).push()
                }
            }
        }

        // --- Security Scan --- Trivy ---
        stage('Security Scan') {
            steps {
                echo 'Scanning Docker image for vulnerabilities...'
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                    // Run the Trivy scan.
                    // --exit-code 1: If vulnerabilities are found, the command will exit with an error code, failing the pipeline.
                    // --severity HIGH,CRITICAL: We only care about high-impact vulnerabilities for this gate.
                    // --no-progress: This cleans up the log output for a CI environment.
                    sh "trivy image --exit-code 1 --severity HIGH,CRITICAL --no-progress ${fullImageName}"
                }
            }
        }
    // --- END OF NEW STAGE ---

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to the K3s cluster...'
                // This 'withCredentials' block is the key to secure access
                // It makes the 'kubeconfig-k3d' secret file available as a temporary file
                // and sets the KUBECONFIG environment variable to its path.
                withCredentials([file(credentialsId: 'kubeconfig-k3d', variable: 'KUBECONFIG')]) {
                    script {
                        def imageTag = "build-${BUILD_NUMBER}"
                        def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                        echo "Updating Kubernetes deployment with new image: ${fullImageName}"

                        // CRITICAL STEP: Dynamically update the image in our deployment manifest.
                        // This 'sed' command finds the line with 'image:' in our YAML
                        // and replaces it with the new, uniquely tagged image name.
                        sh "sed -i 's|image:.*|image: ${fullImageName}|' k8s/deployment.yaml"

                        echo 'Applying the new configuration to the cluster...'
                        // 'kubectl' will automatically use the KUBECONFIG environment variable
                        // to connect to the correct cluster.
                        sh 'kubectl apply -f k8s/'

                        echo 'Waiting for the deployment to complete...'
                        // This command waits until the new version is rolled out successfully.
                        sh "kubectl rollout status deployment/${K8S_DEPLOYMENT_NAME} --namespace ${K8S_NAMESPACE}"
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
