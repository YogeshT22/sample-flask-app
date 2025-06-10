# Sample Python Flask Application for CI/CD

This repository contains a simple "Hello, World" web application built with Python and the Flask framework.

Its primary purpose is to serve as the application component for a full, end-to-end CI/CD pipeline project. The repository includes the application code (`app.py`), its dependencies (`requirements.txt`), a `Dockerfile` for containerization, and a `Jenkinsfile` that defines the entire CI/CD process.

---

## Companion CI/CD Platform Repository

This application is designed to be built, tested, and deployed by the CI/CD platform defined in the following repository:

**[https://github.com/YogeshT22/end-to-end-ci-cd-jenkins-docker](https://github.com/YogeshT22/end-to-end-ci-cd-jenkins-docker)**

---

## File Structure

*   **`app.py`**: The main Flask application file. It exposes a single web endpoint on `/`.
*   **`requirements.txt`**: Lists the Python dependencies required by the application (just `Flask`).
*   **`Dockerfile`**: A multi-stage Dockerfile that builds a container image for the application. It ensures a small and efficient final image.
*   **`Jenkinsfile`**: The heart of the automation. This is a "pipeline-as-code" script that tells a Jenkins server exactly how to process this application.

---

## The CI/CD Pipeline (`Jenkinsfile`)

The `Jenkinsfile` in this repository defines the following automated stages:

1.  **Checkout:** Clones the source code from the Git repository.
2.  **Build Docker Image:** Builds a new Docker container image using the provided `Dockerfile`. The image is tagged with the Jenkins build number for versioning (e.g., `build-1`, `build-2`).
3.  **Push to Local Registry:** Pushes the newly built image to a private Docker Registry, making the build artifact available for deployment.
4.  **Deploy Application:** Stops and removes any old version of the application container and then runs a new container using the image that was just pushed to the registry.
5.  **Post Actions:** Performs cleanup tasks, such as pruning old, unused Docker images to save disk space.

---

## How to Use

This repository is not intended to be run standalone. It should be:

1.  Pushed to a Gitea repository running as part of the companion CI/CD platform.
2.  Configured as the source code repository for a "Pipeline" job in the platform's Jenkins server.

When a `git push` is made to the Gitea repository, a webhook will trigger the Jenkins pipeline, which reads the `Jenkinsfile` and executes the automated CI/CD process.
