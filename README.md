# Sample Python Flask Application for an Advanced CI/CD Pipeline

This repository contains a simple "Hello, World" web application built with Python and the Flask framework.

Its primary purpose is to serve as the **application component** for a full, end-to-end DevOps platform. The repository includes not just the application code, but all the necessary **automation and configuration-as-code artifacts** to enable a sophisticated CI/CD workflow, including:

- A multi-stage `Dockerfile` for efficient containerization.
- A declarative `Jenkinsfile` that defines the entire CI/CD process.
- A full suite of Kubernetes manifests (`k8s/`) for deployment and traffic management.

---

## Companion CI/CD Platform Repository

This application is designed to be automatically built, secured, and deployed by the advanced DevOps platform defined in the following repository:

**[https://github.com/YogeshT22/end-to-end-ci-cd-jenkins-docker](https://github.com/YogeshT22/end-to-end-ci-cd-jenkins-docker)**

---

## Repository Structure

- **`app.py`**: The main Flask application file, exposing a single web endpoint.
- **`requirements.txt`**: Lists the Python dependencies required by the application.
- **`Dockerfile`**: A multi-stage Dockerfile that builds a minimal, secure, and efficient container image for the application.
- **`Jenkinsfile`**: **The heart of the automation.** This is a "pipeline-as-code" script that instructs a Jenkins server on the exact steps to process this application.
- **`load-tests/`**: k6 scripts used by the pipeline to smoke-test the deployed service and capture metrics artifacts.
- **`k8s/`**: A directory containing all Kubernetes manifest files required for deployment.
  - **`deployment.yaml`**: Defines the desired state for running the application on the cluster (e.g., number of replicas).
  - **`service.yaml`**: Creates a stable internal network endpoint for the application pods.
  - **`ingress.yaml`**: Configures the cluster's Ingress controller to expose the application to external traffic.
  - **`service-account.yaml`**: Creates a dedicated, secure identity for Jenkins to interact with the cluster.
  - **`jenkins-token-secret.yaml`**: A manifest for creating the authentication token secret for the Jenkins service account.
  - **`k8s/service-account.yaml`**: Creates a dedicated, secure identity (`ServiceAccount`) for Jenkins to interact with the cluster.
  - **`k8s/jenkins-token-secret.yaml`**: A manifest for creating the authentication token secret for the Jenkins service account (for K8s v1.24+).

---

## The Automated CI/CD Pipeline (`Jenkinsfile`)

The `Jenkinsfile` in this repository defines a modern, multi-stage pipeline with a focus on security and best practices:

1.  **Checkout:** Clones the source code from the Gitea repository.
2.  **Build and Push Docker Image:** Builds a new Docker container image using the `Dockerfile` and tags it with the unique Jenkins build number for versioning. The image is then pushed to a private Docker Registry.
3.  **Security Scan (DevSecOps Gate):** Uses **Trivy** to scan the newly built image for `HIGH` and `CRITICAL` severity vulnerabilities. **If any are found, the pipeline fails, preventing the insecure image from being deployed.**
4.  **Deploy to Kubernetes:** If the security scan passes, this stage connects to the Kubernetes cluster using a secure **Service Account Token**. It then uses `kubectl apply` to update the `Deployment` with the new image tag, triggering a **zero-downtime rolling update**.
5.  **Load Test with k6:** Runs a short in-cluster k6 smoke/load test against the deployed service, checks the homepage and health endpoint, and archives the k6 output as a build artifact.
6.  **Post Actions:** Performs cleanup tasks, such as pruning old, unused Docker images to save disk space.

### k6 Test Output

The k6 stage exercises the deployed service inside Kubernetes so the test sees the same service DNS that production traffic would use. It records:

- request failure rate
- request duration percentiles
- endpoint checks for `/` and `/health`

The raw k6 summary is archived with each Jenkins build, which makes it easy to compare runs when you are describing the platform on a resume or in a walkthrough.

### k6 Integration Summary

The k6 stage was implemented as an in-cluster smoke/load test to keep traffic realistic and avoid host networking edge-cases.

- A k6 script at `load-tests/k6-smoke.js` validates both `/` and `/health` endpoints.
- Jenkins creates a temporary `ConfigMap` and short-lived test `Pod` for each build.
- Test output is streamed into Jenkins console logs and archived as a build artifact.
- RBAC in `k8s/service-account.yaml` includes the required permissions for `pods`, `pods/log`, and `configmaps`.

For full implementation notes including design choices, rollout steps, and issues faced during debugging, see:

- [`k6-implementation-notes.md`](k6-implementation-notes.md)

---

## How to Use

This repository is not intended to be run standalone. Its lifecycle is managed by the companion CI/CD platform. The intended workflow is:

1.  Push this repository's code to the Gitea server running as part of the platform.
2.  Configure a "Pipeline" job in the platform's Jenkins server to point to this Gitea repository.
3.  When a developer executes a `git push` to the Gitea repository, a webhook automatically triggers the Jenkins pipeline, which reads the `Jenkinsfile` and executes the entire CI/CD process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
