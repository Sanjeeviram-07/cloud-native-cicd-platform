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
                sh 'python3 --version'
                sh 'git --version'
                sh 'docker --version'
                sh 'ansible --version'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running application tests...'
                sh 'python3 -m pip install -r requirements.txt'
                sh 'python3 -m pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t cloud-native-cicd-platform:${BUILD_NUMBER} .'
            }
        }

        stage('Docker Image Check') {
            steps {
                sh 'docker images'
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
    }
}