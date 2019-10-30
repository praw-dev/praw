pipeline {
    agent {
        docker { image 'python' }
    }

    stages {
        stage('Setup workspace'){
            steps{
                sh "echo Configures the workspace"
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Validate') {
            steps {
                sh "echo Validates the source code using flake8"
                sh 'pip install flake8'
                sh 'python -m flake8 praw/'
                sh 'python -m flake8 --select=DUO praw/'
            }
        }
        stage('Unit tests') {
            steps {
                sh "echo Runs unit tests using pytests"
                sh 'pip install -r test-requirements.txt'
                sh 'python -m pytest tests/unit/'
            }
        }
        stage('Integration tests') {
            steps {
                sh "echo Runs integration tests"
            }
        }
        stage('Package') {
            steps {
                sh "echo Builds the project"
            }
        }
        stage('Verify') {
            steps {
                sh "echo Checks for bugs in the project"
            }
        }
        stage('Deploy') {
            steps {
                sh "echo Uploads an artifact to jenkins"
            }
        }
    }
    
    post { 
        always { 
            cleanWs()
        }
    }
}