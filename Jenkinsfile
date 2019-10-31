pipeline {
    agent {
        docker { image 'python' }
    }

    stages {
        stage('Setup workspace'){
            steps{
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Validate') {
            steps {
                sh 'pip install flake8'
                sh 'python -m flake8 praw/'
                sh 'python -m flake8 --select=DUO praw/'
            }
        }
        stage('Unit tests') {
            steps {
                sh 'pip install -r test-requirements.txt'
                sh 'python -m pytest tests/unit/'
            }
        }
        stage('Integration tests') {
            steps {
                sh 'python -m pytest tests/integration/'
            }
        }
        stage('Package') {
            steps {
                sh 'python setup.py build'
            }
        }
        stage('Verify') {
            steps {
                sh 'pip install bandit'
                sh 'bandit -ll -r praw'
            }
        }
        stage('Deploy') {
            steps {
                sh 'tar -cvf praw.tar build'
                archiveArtifacts artifacts: 'praw.tar', fingerprint: true
            }
        }
    }
    
    post { 
        always { 
            cleanWs()
        }
    }
}