// ---------------------------------------------
// Jenkins Pipeline - Sample Flask Application
// DevSecOps platform: Gitea -> Jenkins -> Docker -> Kubernetes
// Production practices:
//   - Trivy scans FAIL the build on HIGH/CRITICAL findings
//   - TLS verification enabled on kubectl (no --insecure-skip-tls-verify)
//   - Image deployed by immutable SHA256 digest
//   - Rollout status verified after deploy
//   - k6 smoke/load test runs against the deployed service and archives metrics
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
    }    // ------------------------------------------------------------------
    // VULNERABILITY SCAN: --exit-code 1 makes pipeline FAIL on findings
    // --ignore-unfixed skips CVEs with no available fix in the distro
    //   (e.g. Debian "will_not_fix" status). Accepted risks are documented
    //   in .trivyignore with justification.
    // ------------------------------------------------------------------
    stage('Security Scan - Image Vulnerabilities') {
        steps {
            sh """
                trivy image \
                    --severity HIGH,CRITICAL \
                    --exit-code 1 \
                    --ignore-unfixed \
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

        // ------------------------------------------------------------------
        // LOAD TEST: runs k6 inside the cluster so it hits the service DNS
        // and records a reproducible smoke/load summary for the build.
        // ------------------------------------------------------------------
        stage('Load Test with k6') {
                steps {
                        withCredentials([
                                file(credentialsId: 'kubeconfig-sa', variable: 'KUBECONFIG')
                        ]) {
                                script {
                                        def k6ConfigMapName = "k6-smoke-test-${BUILD_NUMBER}"
                                        def k6PodName = "flask-app-k6-load-test-${BUILD_NUMBER}"
                                        def k6LogFile = "${IMAGE_NAME}-${IMAGE_TAG}-k6.log"

                                        sh """#!/usr/bin/env bash
set -euo pipefail

K8S_NAMESPACE="${K8S_NAMESPACE}"
k6ConfigMapName="${k6ConfigMapName}"
k6PodName="${k6PodName}"
k6LogFile="${k6LogFile}"

cleanup() {
        kubectl delete -n \$K8S_NAMESPACE pod/\$k6PodName configmap/\$k6ConfigMapName --ignore-not-found=true
}

trap cleanup EXIT

kubectl create configmap \$k6ConfigMapName \
        --from-file=load-tests/k6-smoke.js \
        -n \$K8S_NAMESPACE \
        --dry-run=client -o yaml | kubectl apply -f -

cat > /tmp/k6-pod.yaml <<'YAMLEOF'
apiVersion: v1
kind: Pod
metadata:
    name: POD_NAME_PLACEHOLDER
spec:
    restartPolicy: Never
    containers:
        - name: k6
            image: grafana/k6:0.56.0
            command:
                - k6
                - run
                - /scripts/k6-smoke.js
            env:
                - name: K6_BASE_URL
                    value: http://flask-app-service.K8S_NAMESPACE_PLACEHOLDER.svc.cluster.local
                - name: K6_VUS
                    value: "5"
                - name: K6_DURATION
                    value: "15s"
            volumeMounts:
                - name: k6-script
                    mountPath: /scripts
    volumes:
        - name: k6-script
            configMap:
                name: CONFIGMAP_NAME_PLACEHOLDER
YAMLEOF

sed -i "s/POD_NAME_PLACEHOLDER/\$k6PodName/g; s/K8S_NAMESPACE_PLACEHOLDER/\$K8S_NAMESPACE/g; s/CONFIGMAP_NAME_PLACEHOLDER/\$k6ConfigMapName/g" /tmp/k6-pod.yaml

kubectl apply -n \$K8S_NAMESPACE -f /tmp/k6-pod.yaml

if ! kubectl wait -n \$K8S_NAMESPACE --for=jsonpath='{.status.phase}'=Succeeded pod/\$k6PodName --timeout=10m; then
        kubectl logs -n \$K8S_NAMESPACE pod/\$k6PodName || true
        exit 1
fi

kubectl logs -n \$K8S_NAMESPACE pod/\$k6PodName | tee \$k6LogFile
"""

                                        archiveArtifacts artifacts: k6LogFile, fingerprint: true
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
