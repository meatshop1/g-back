pipeline {
    agent any

    stages {
        stage('Installing Dependencies') {
            steps {
                script {
                    echo 'Installing Python dependencies...'
                    sh '''
                        python3 -m pip install --upgrade pip
                        python3 -m pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    . venv/bin/activate
                    pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }
    }
}
