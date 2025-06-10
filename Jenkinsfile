pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from Gitea...'
                git url: 'http://gitea-server:3000/admin/sample-flask-app.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building the Docker image...'
                script {
                    // Define the image name and tag
                    def imageName = "localhost:5000/sample-flask-app"
                    def imageTag = "build-${BUILD_NUMBER}"
                    
                    // Build the Docker image
                    docker.build("${imageName}:${imageTag}", ".")
                }
            }
        }
        
        stage('Push to Local Registry') {
            steps {
                echo 'Pushing the Docker image to the local registry...'
                script {
                    def imageName = "localhost:5000/sample-flask-app"
                    def imageTag = "build-${BUILD_NUMBER}"
                    
                    // Push the image
                    docker.image("${imageName}:${imageTag}").push()
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying the new version of the application...'
                script {
                    def imageName = "localhost:5000/sample-flask-app"
                    def imageTag = "build-${BUILD_NUMBER}"
                    def containerName = "running-flask-app"
                    
                    // Stop and remove any old container with the same name
                    sh "docker stop ${containerName} || true"
                    sh "docker rm ${containerName} || true"
                    
                    // Run the new container
                    sh "docker run -d --name ${containerName} -p 8081:5000 ${imageName}:${imageTag}"
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished.'
            // Clean up old images to save space
            script {
                sh "docker image prune -f"
            }
        }
    }
}
