pipeline{
    agent any
     environment {
        VENV_DIR = 'venv'
    }

    stages {
        stage('Installing Dependencies'){
            steps{
                script {
                    echo 'Installing Python dependencies...'
                    sh '''
                        python3 -m venv $VENV_DIR
                        source $VENV_DIR/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        stage('Running Tests'){
            steps{
                script {
                    echo 'Running tests...'
                    sh '''
                        source $VENV_DIR/bin/activate
                         python manage.py test
                    '''
                }
            }
        }
    }

    post {
        always {
            junit 'reports/**/*.xml'
        }
    }
}
