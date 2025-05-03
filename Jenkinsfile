pipeline {
    agent any

    stages {
        stage('Install Python Dependencies') {
            steps {
                echo 'Creating virtual environment and installing requirements...'
                sh '''
                    python3 -m venv venv
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh './venv/bin/pytest --maxfail=1 --disable-warnings -q'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up virtual environment...'
            sh 'rm -rf venv'
        }
    }
}
