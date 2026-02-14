// ---------------------------------------------
// This is a Jenkins pipeline script for a sample Flask application.
// This is a personal project to demonstrate a complete CI/CD pipeline using Gitea, Jenkins, Docker, and Kubernetes.
// Using Docker Pipeline Plugin, Plugin runs the 'docker build -t ...'.
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
                git url: 'http://gitea-server:3000/admin/sample-flask-app.git', branch: 'feature/v2.0'
            }
        }

        // --- ADD THIS NEW STAGE ---
        stage('Security Scan - Hardcoded Secrets') {
            steps {
                echo "Scanning source code for hardcoded secrets..."
                // Use Trivy to scan the filesystem for secrets.
                // We will keep it non-blocking for now.
                sh "trivy fs --scanners secret --no-progress --exit-code 1."
            }
        }
        // --- END OF NEW STAGE ---

        // // --- Dependency Scan STAGE ---

        // stage('Dependency Scan') {
        //     steps {
        //         echo "Scanning application dependencies for vulnerabilities..."
        //         // Use Trivy to scan the filesystem, focusing on the requirements.txt
        //         // We'll keep it non-blocking for now to see the report.
        //         sh "trivy fs --severity HIGH,CRITICAL --no-progress ."
        //     }
        // }
        // // --- END OF Dependency Scan STAGE ---

        stage('Build and Push Docker Image') {
            steps {
                echo 'Building and pushing the Docker image...'
                script {
                    def imageTag = "build-${BUILD_NUMBER}" // so we calculate image tag using build number
                    def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}" // we calculate full image name with tag

                     // Force a clean build with no cache to ensure all layers are fresh
                    echo "Building with --no-cache to guarantee fresh dependencies..."
                    docker.build(fullImageName, "--no-cache .")

                     // Push the image to the local registry

                    docker.image(fullImageName).push()

                }
            }
        }
        // --- NEW Trivy FOR SECURITY SCAN ---
        stage('Security Scan - Image Vulnerabilities') {
            steps {
                echo "Scanning Docker image for vulnerabilities..."
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                    // We will allow the build to continue even if vulnerabilities are found for now
                    // The goal is to see a CORRECT report first.
                    echo "Running Trivy scan... (non-blocking)"
                    sh "trivy image --severity HIGH,CRITICAL --exit-code 1 --no-progress ${fullImageName}"
                    //sh "trivy image --severity HIGH,CRITICAL --exit-code 1 --no-progress ${fullImageName}" // Uncomment this line to make the build fail on vulnerabilities (DEV).
                }
            }
        }
        // --- END OF Trivy STAGE ---

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to the K3s cluster!'

                // REMINDER: This 'withCredentials' block is the key to secure access
                // Dev note: It makes the 'kubeconfig-k3d' secret file available as a temp file
                // and sets the KUBECONFIG environment variable to its path.
                // FIX: change to kubeconfig-sa from kubeconfig-k3d (Dev).
                withCredentials([file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')]) {
                    script {

                        // Ensure the kubectl binary we mounted is executable
                        echo "Setting execute permissions on kubectl..."
                        sh "chmod +x /usr/local/bin/kubectl"

                        def imageTag = "build-${BUILD_NUMBER}"
                        def fullImageName = "${REGISTRY_URL}/${IMAGE_NAME}:${imageTag}"

                        echo "Updating Kubernetes deployment with new image: ${fullImageName}"

                        // Dev note: dynamically update the image in our deployment manifest.
                        // Dev note: for demo 'sed' is ok, but i should use kubectl set image or Helm in future release.

                        sh "sed -i 's|image:.*|image: ${fullImageName}|' k8s/deployment.yaml"

                        echo 'Applying the new configuration to the cluster!'

                        // Dev note: '--insecure-skip-tls-verify' flag is used to bypass TLS verification.
                        // WARNING: This is not for prod env (DEV)

                        // here, kubelet on the cluster's worker node instructs the underlying container runtime (using Docker) to pull the image from the registry and create a new container (a Pod) from that image.

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
