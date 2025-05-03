pipeline {
    agent any

    stages {
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    ./venv/bin/pip install --upgrade pip
                    ./venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    . venv/bin/activate
                    ./venv/bin/pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }
    }

    post {
        always {
            sh 'rm -rf venv'
        }
    }
}
