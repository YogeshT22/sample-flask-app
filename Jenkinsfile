// ---------------------------------------------
// This is a Jenkins pipeline script for a sample Flask application.
// This is a personal project to demonstrate a complete CI/CD pipeline using Gitea, Jenkins, Docker, and Kubernetes.
// Using Docker Pipeline Plugin, Plugin runs the 'docker build -t ...'.
// ---------------------------------------------
pipeline {

agent any

environment {

    REGISTRY = 'local-docker-registry:5000'
    IMAGE_NAME = 'sample-flask-app'
    IMAGE_TAG = "build-${BUILD_NUMBER}"
    FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

    K8S_NAMESPACE = 'default'
    K8S_DEPLOYMENT_NAME = 'flask-app-deployment'

    GIT_REPO = 'http://gitea-server:3000/admin/sample-flask-app.git'
    GIT_BRANCH = 'main'
}

stages {

    stage('Checkout') {
        steps {
            git url: "${GIT_REPO}", branch: "${GIT_BRANCH}"
        }
    }

    stage('Security Scan - Hardcoded Secrets') {
        steps {
            sh "trivy fs --scanners secret --no-progress ."
        }
    }

    stage('Build and Push Image') {
        steps {
            script {

                sh """
                    docker build -t ${FULL_IMAGE} --no-cache .
                    docker push ${FULL_IMAGE}
                """

                env.IMAGE_DIGEST = sh(
                    script: "docker inspect --format='{{index .RepoDigests 0}}' ${FULL_IMAGE}",
                    returnStdout: true
                ).trim()

                echo "Digest: ${IMAGE_DIGEST}"
            }
        }
    }

    stage('Security Scan - Image Vulnerabilities') {
        steps {
            sh """
                trivy image \
                --severity HIGH,CRITICAL \
                --no-progress \
                ${FULL_IMAGE}
            """
        }
    }

    stage('Generate SBOM') {
        steps {
            script {

                def sbomFile = "${IMAGE_NAME}-${IMAGE_TAG}-sbom.json"

                sh """
                    trivy image \
                    --format cyclonedx \
                    --output ${sbomFile} \
                    ${FULL_IMAGE}
                """

                archiveArtifacts artifacts: sbomFile, fingerprint: true
            }
        }
    }

    stage('Sign and Verify Image') {

        steps {

            script {

                withCredentials([
                    file(credentialsId: 'cosign-private-key', variable: 'COSIGN_PRIVATE_KEY'),
                    string(credentialsId: 'cosign-password', variable: 'COSIGN_PASSWORD')
                ]) {

                    sh """
                        export COSIGN_PASSWORD=$COSIGN_PASSWORD
                        cosign sign \
                            --yes \
                            --tlog-upload=false \
                            --key $COSIGN_PRIVATE_KEY \
                            ${IMAGE_DIGEST}
                    """

                    sh """
                        cosign verify \
                            --key cosign.pub \
                            --insecure-ignore-tlog \
                            ${IMAGE_DIGEST}
                    """
                }
            }
        }
    }

    stage('Deploy to Kubernetes') {

        steps {

            withCredentials([
                file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')
            ]) {

                sh """
                    sed -i 's|image:.*|image: ${IMAGE_DIGEST}|' k8s/deployment.yaml
                """

                sh """
                    kubectl apply \
                        --insecure-skip-tls-verify=true \
                        -n ${K8S_NAMESPACE} \
                        -f k8s/
                """
            }
        }
    }
}

post {

    always {
        sh "docker image prune -f"
    }

}
}
