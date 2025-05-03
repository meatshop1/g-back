pipeline {
    agent any
    environment {
        VENV_DIR = 'venv'
        // Direct environment variables for database connection
        DB_NAME = 'meatshop'
        DB_HOST = 'localhost'
        DB_USER = 'eladwy'
        DB_PASSWORD = credentials('LOCAL_DB_PASSWORD')
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
                    # Export environment variables for Django
                    export DB_NAME=$DB_NAME
                    export DB_HOST=$DB_HOST
                    export DB_USER=$DB_USER
                    export DB_PASSWORD=$DB_PASSWORD
                    
                    # Run Django tests
                    python manage.py test
                '''
            }
        }
    }
    post {
        success {
            echo 'Tests passed! The build is ready for deployment.'
        }
        failure {
            echo 'Tests failed! Please check the logs for details.'
        }
        cleanup {
            echo 'Cleaning up the virtual environment...'
            sh 'rm -rf $VENV_DIR'
        }
    }
}