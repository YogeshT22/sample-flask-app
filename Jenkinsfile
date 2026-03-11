// ---------------------------------------------
// Jenkins Pipeline - Sample Flask Application
// DevSecOps platform: Gitea -> Jenkins -> Docker -> Kubernetes
// Production practices:
//   - Trivy scans FAIL the build on HIGH/CRITICAL findings
//   - TLS verification enabled on kubectl (no --insecure-skip-tls-verify)
//   - Image deployed by immutable SHA256 digest
//   - Rollout status verified after deploy
//   - Workspace cleaned up on every run
// ---------------------------------------------
pipeline {

agent any

environment {

    REGISTRY         = 'local-docker-registry:5000'
    IMAGE_NAME       = 'sample-flask-app'
    IMAGE_TAG        = "build-${BUILD_NUMBER}"
    FULL_IMAGE       = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

    K8S_NAMESPACE        = 'default'
    K8S_DEPLOYMENT_NAME  = 'flask-app-deployment'

    GIT_REPO   = 'http://gitea-server:3000/admin/sample-flask-app.git'
    GIT_BRANCH = 'main'
}

stages {

    stage('Checkout') {
        steps {
            git url: "${GIT_REPO}", branch: "${GIT_BRANCH}"
        }
    }

    // ------------------------------------------------------------------
    // SECRET SCAN: fails the build if hardcoded secrets are found
    // ------------------------------------------------------------------
    stage('Security Scan - Hardcoded Secrets') {
        steps {
            sh """
                trivy fs \
                    --scanners secret \
                    --exit-code 1 \
                    --no-progress \
                    .
            """
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

                echo "Image digest: ${IMAGE_DIGEST}"
            }
        }
    }

    // ------------------------------------------------------------------
    // VULNERABILITY SCAN: --exit-code 1 makes pipeline FAIL on findings
    // ------------------------------------------------------------------
    stage('Security Scan - Image Vulnerabilities') {
        steps {
            sh """
                trivy image \
                    --severity HIGH,CRITICAL \
                    --exit-code 1 \
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
                        export COSIGN_PASSWORD=${COSIGN_PASSWORD}
                        cosign sign \
                            --yes \
                            --tlog-upload=false \
                            --key ${COSIGN_PRIVATE_KEY} \
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

    // ------------------------------------------------------------------
    // DEPLOY: uses immutable digest, no --insecure-skip-tls-verify,
    //         only applies app manifests (not service-account RBAC),
    //         verifies rollout completes successfully
    // ------------------------------------------------------------------
    stage('Deploy to Kubernetes') {

        steps {

            withCredentials([
                file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')
            ]) {
                script {

                    // Patch only the container image line precisely - avoid broad sed match
                    sh """
                        kubectl set image deployment/${K8S_DEPLOYMENT_NAME} \
                            flask-app-container=${IMAGE_DIGEST} \
                            -n ${K8S_NAMESPACE}
                    """

                    // Apply only service and ingress - RBAC is applied separately, not on every deploy
                    sh """
                        kubectl apply \
                            -n ${K8S_NAMESPACE} \
                            -f k8s/service.yaml \
                            -f k8s/ingress.yaml
                    """

                    // Wait for rollout to complete - fails the build if pods don't come up
                    sh """
                        kubectl rollout status deployment/${K8S_DEPLOYMENT_NAME} \
                            -n ${K8S_NAMESPACE} \
                            --timeout=120s
                    """
                }
            }
        }
    }
}

post {

    success {
        echo "Pipeline succeeded. Build: ${BUILD_NUMBER} | Image: ${IMAGE_DIGEST}"
    }

    failure {
        echo "Pipeline FAILED at build: ${BUILD_NUMBER}. Check logs above."
    }

    always {
        // Clean up dangling images to save disk space.
        // '|| true' prevents a docker socket permission error from masking the real build result.
        sh "docker image prune -f || true"
        // Clean Jenkins workspace after every run
        cleanWs()
    }

}
}
