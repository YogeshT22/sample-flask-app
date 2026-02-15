// ---------------------------------------------
// This is a Jenkins pipeline script for a sample Flask application.
// This is a personal project to demonstrate a complete CI/CD pipeline using Gitea, Jenkins, Docker, and Kubernetes.
// Using Docker Pipeline Plugin, Plugin runs the 'docker build -t ...'.
// ---------------------------------------------
pipeline {
    agent any

    environment {
        REGISTRY_URL = 'https://localhost:5000'
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
                sh "trivy fs --scanners secret --no-progress ."
            }
        }
        // --- END OF NEW STAGE ---

        // --- Build and Push Stage ---
        stage('Build and Push') {
            steps {
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    // 1. The tag used for local docker commands (NO https://)
                    def dockerTag = "localhost:5000/${IMAGE_NAME}:${imageTag}"

                    echo "Building: ${dockerTag}"
                    sh "docker build -t ${dockerTag} --no-cache ."

                    // 2. The registry URL used for the actual upload (HAS https://)
                    docker.withRegistry("${REGISTRY_URL}") {
                        sh "docker push ${dockerTag}"
                    }

                    // 3. Capture the digest
                    def digest = sh(script: "docker inspect --format='{{index .RepoDigests 0}}' ${dockerTag}", returnStdout: true).trim()
                    env.IMAGE_DIGEST = digest
                }
            }
        }
        // --- END OF Build and Push Stage ---

        // --- NEW Trivy FOR SECURITY SCAN ---
        stage('Security Scan - Image Vulnerabilities') {
            steps {
                echo "Scanning Docker image for vulnerabilities..."
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    // Trivy needs to talk to the internal container name
                    def internalImage = "local-docker-registry:5000/${IMAGE_NAME}:${imageTag}"

                    echo "Running Trivy scan... (non-blocking)"
                    sh "trivy image --severity HIGH,CRITICAL --no-progress ${internalImage}"
                }
            }
        }
        // --- END OF Trivy STAGE ---

        // SBOM (Software Bill of Materials) Generation Stage
        stage('SBOM Generation') {
            steps {
                echo "Generating Software Bill of Materials (SBOM) for the image..."
                script {
                    def imageTag = "build-${BUILD_NUMBER}"
                    def internalImage = "local-docker-registry:5000/${IMAGE_NAME}:${imageTag}"
                    def sbomFileName = "${IMAGE_NAME}-${imageTag}-sbom.json"

                    // Use Trivy to generate the SBOM in CycloneDX JSON format
                    sh "trivy image --format cyclonedx --output ${sbomFileName} ${internalImage}"

                    // Archive the SBOM file in Jenkins
                    archiveArtifacts artifacts: sbomFileName, fingerprint: true
                    echo "SBOM generated and archived: ${sbomFileName}"
                }
            }
        }
        // --- END OF SBOM STAGE ---

stage('Image Signing') {
            steps {
                script {
                    withCredentials([
                        file(credentialsId: 'cosign-private-key', variable: 'COSIGN_PRIVATE_KEY'),
                        string(credentialsId: 'cosign-password', variable: 'COSIGN_PASSWORD')
                    ]) {
                        def signTarget = env.IMAGE_DIGEST.replace("localhost:5000", "local-docker-registry:5000")
                        echo "Signing image digest: ${signTarget}"

                        sh """
                        export COSIGN_PASSWORD=${COSIGN_PASSWORD}
                        cosign sign --yes --tlog-upload=false --key ${COSIGN_PRIVATE_KEY} ${signTarget}
                        """

                        echo "Verifying signature..."
                        // CHANGE: Added --insecure-ignore-tlog flag
                        sh "cosign verify --key cosign.pub --insecure-ignore-tlog ${signTarget}"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')]) {
                    script {
                        def imageTag = "build-${BUILD_NUMBER}"
                        // 1. MUST NOT HAVE HTTPS. Only the registry hostname.
                        def k8sImage = "local-docker-registry:5000/${IMAGE_NAME}:${imageTag}"

                        echo "Updating deployment with image: ${k8sImage}"

                        // 2. Update the manifest
                        sh "sed -i 's|image:.*|image: ${k8sImage}|' k8s/deployment.yaml"

                        echo 'Applying manifest...'
                        sh "kubectl apply --insecure-skip-tls-verify=true -f k8s/"
                        sh "sed -i 's|image:.*|image: ${k8sImage}|' k8s/deployment.yaml"
                    }
                }
            }
        }
    }

    // --- NEW STAGE FOR CLEANUP ---
    post {
        always {
            echo 'Pipeline finished.'
            script {
                sh 'docker image prune -f'
            }
        }
    }
}
