pipeline {
    agent any

    stages {
        stage('Install Python') {
            steps {
                sh '''
                     sudo apt-get update
                     sudo apt-get install -y python3 python3-pip
                '''
            }
        }
        stage('Installing Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m pip install --upgrade pip
                    python3 -m pip install -r requirements.txt
                '''
            }
        }
    }
}
