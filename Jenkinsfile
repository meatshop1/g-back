pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Installing Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Running Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    . $VENV_DIR/bin/activate
                    python manage.py test
                '''
            }
        }
    }

    post {
        always {
            junit 'reports/**/*.xml'
        }
    }
}
