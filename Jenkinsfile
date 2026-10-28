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
                echo 'Scanning Docker image for vulnerabilities...'
                sh '''
                    trivy --config /dev/null image \
                        --scanners vuln \
                        --ignorefile /dev/null \
                        --severity HIGH,CRITICAL \
                        --exit-code 1 \
                        cloud-native-cicd-platform:${BUILD_NUMBER}
                '''
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
            echo 'CI Pipeline completed successfully!'
        }

        failure {
            echo 'CI Pipeline failed. Check the stage logs.'
        }

        always {
            echo "Build number: ${BUILD_NUMBER}"
        }
    }
}