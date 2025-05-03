pipeline {
    agent any
    environment {
        VENV_DIR = 'venv'
        LOCAL_DB_NAME = 'meatshop'
        LOCAL_DB_HOST = 'localhost'
        LOCAL_DB_USER = 'root'
        LOCAL_DB_PASSWORD = credentials('LOCAL_DB_PASSWORD')
        LOCAL_DB_PORT = '3306'
        SONAR_SCANNER_HOME = tool 'sonarqube-scanner';
    }
    stages {
        stage('Installing Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    python3 -m pip install --upgrade pip
                    pip install coverage 
                    pip install -r requirements.txt
                '''
            }
        }
        stage('Start MySQL') {
            steps {
                sh '''
                    if [ $(docker ps -aq -f name=test-mysql) ]; then
                        docker rm -f test-mysql
                    fi

                    docker run --name test-mysql \
                        -e MYSQL_ROOT_PASSWORD=${LOCAL_DB_PASSWORD} \
                        -e MYSQL_DATABASE=meatshop \
                        -e MYSQL_USER=eladwy \
                        -e MYSQL_PASSWORD=${LOCAL_DB_PASSWORD} \
                        -p 3306:3306 -d mysql:8.0

                    echo "Waiting for MySQL to be ready..."
                    sleep 60
                '''
            }
        }
        stage('Running Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    . $VENV_DIR/bin/activate

                    export DB_NAME=$LOCAL_DB_NAME
                    export DB_HOST=$LOCAL_DB_HOST
                    export DB_USER=$LOCAL_DB_USER
                    export DB_PASSWORD=$LOCAL_DB_PASSWORD
                    export DB_PORT=$LOCAL_DB_PORT

                    python manage.py test
                '''
            }
        }
        stage('Code Coverage') {
            steps {
                echo 'Generating code coverage report...'
                sh '''
                    . $VENV_DIR/bin/activate
                    export DB_NAME=$LOCAL_DB_NAME
                    export DB_HOST=$LOCAL_DB_HOST
                    export DB_USER=$LOCAL_DB_USER
                    export DB_PASSWORD=$LOCAL_DB_PASSWORD
                    export DB_PORT=$LOCAL_DB_PORT

                    coverage run manage.py test
                    coverage report
                    coverage xml
                    coverage html -d coverage_html
                '''
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'coverage_html',
                    reportFiles: 'index.html',
                    reportName: 'Code Coverage Report'
                ])
            }
        }

        stage('SAST') {
            steps {
                echo 'Running static code analysis...'
                sh '''
                    $SONAR_SCANNER_HOME/bin/sonar-scanner \
                        -Dsonar.projectKey=g-back \
                        -Dsonar.sources=core/,tags/,likes/,meatshop/,shop/,Dockerfile/ \
                        -Dsonar.host.url=http://192.168.1.83:9000 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.token=sqp_e4b42065beefe21022b0107aad6ce9fe3768d8fb \
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
            sh '''
                if [ -d "$VENV_DIR" ]; then
                    rm -rf $VENV_DIR
                fi
            '''
        }
    }
}
