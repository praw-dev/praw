pipeline {
    agent {
        docker { image 'python' }
    }

    stages {
        stage('Setup workspace'){
            steps{
                sh 'pip install -r requirements.txt'
                sh 'mkdir reports'
            }
        }
        stage('Validate') {
            steps {
                sh 'pip install flake8'
                sh 'python -m flake8 --tee --output-file=reports/flake8.txt praw/'
                sh 'python -m flake8 --tee --output-file=reports/flake8_dlint.txt --select=DUO praw/'
            }
        }
        stage('Unit tests') {
            steps {
                sh 'pip install -r test-requirements.txt'
                sh 'python -m pytest --junitxml reports/unit_tests.xml tests/unit/'
            }
        }
        stage('Integration tests') {
            steps {
                sh 'python -m pytest --junitxml reports/integration_tests.xml tests/integration/'
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
                sh 'bandit -ll -f txt -o "reports/bandit.txt" -r praw'
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
            sh 'tar -cvf reports.tar reports'
            archiveArtifacts artifacts: 'reports.tar', fingerprint: true
            cleanWs()
        }
    }
}