pipeline {
    agent {
        docker { image 'python' }
    }

    stages {
        stage('Setup workspace'){
            steps{
                sh "echo Configure workspace"
            }
        }
        stage('Validate') {
            steps {
                sh "echo Validate Code"
            }
        }
        stage('Unit tests') {
            steps {
                sh "echo Runs unit tests"
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