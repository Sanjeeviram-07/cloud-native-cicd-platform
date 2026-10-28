pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Environment Check') {
            steps {
                echo 'Checking CI environment...'

                sh 'python3 --version'
                sh 'git --version'
                sh 'docker --version'
                sh 'ansible --version'
                sh 'trivy --version'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Creating isolated Python environment...'

                sh '''
                    rm -rf .venv

                    python3 -m venv .venv

                    .venv/bin/python -m pip install --upgrade pip

                    .venv/bin/python -m pip install -r requirements.txt

                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'

                sh '''
                    docker build \
                        -t cloud-native-cicd-platform:${BUILD_NUMBER} \
                        .
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                echo 'Scanning Docker image for HIGH and CRITICAL vulnerabilities...'

                sh '''
                    trivy --config /dev/null image \
                        --scanners vuln \
                        --ignorefile /dev/null \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        --skip-version-check \
                        cloud-native-cicd-platform:${BUILD_NUMBER}
                '''
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USER" \
                            --password-stdin

                        docker tag \
                            cloud-native-cicd-platform:${BUILD_NUMBER} \
                            "$DOCKERHUB_USER/cloud-native-cicd-platform:${BUILD_NUMBER}"

                        docker push \
                            "$DOCKERHUB_USER/cloud-native-cicd-platform:${BUILD_NUMBER}"

                        docker logout
                    '''
                }
            }
        }

        stage('Docker Image Check') {
            steps {
                echo 'Checking Docker image...'

                sh '''
                    docker images cloud-native-cicd-platform
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed. Check the stage logs.'
        }

        always {
            echo "Build number: ${BUILD_NUMBER}"
        }
    }
}