pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install dependencies and test') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m pip install -r requirements.txt'
                        sh 'python3 -m pytest -q --junitxml=pytest-report.xml'
                    } else {
                        bat 'py -m pip install -r requirements.txt'
                        bat 'py -m pytest -q --junitxml=pytest-report.xml'
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'pytest-report.xml'
                }
            }
        }
    }
}
