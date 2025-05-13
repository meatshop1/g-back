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
        GITHUB_TOKEN = credentials('git_hub_token'); 
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
                    python3 -m pip install pip-audit
                    pip install -r requirements.txt
                    python3 -m pip install drf-spectacular
                '''
            }
        }
        stage('Audit Dependencies') {
            steps {
                 catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        . venv/bin/activate
                        pip-audit > pip-audit-report.txt
                    '''
                }
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
                timeout(time: 120, unit: 'SECONDS') {
                    echo 'Running static code analysis....'
                    withSonarQubeEnv('SonarQube-backend') {
                        sh '''
                        $SONAR_SCANNER_HOME/bin/sonar-scanner \
                            -Dsonar.projectKey=g-back \
                            -Dsonar.sources=core/,tags/,likes/,meatshop/,shop/,Dockerfile/ \
                            -Dsonar.python.coverage.reportPaths=coverage.xml 
                        '''
                    }
                    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }
         stage('Building Docke Image'){
            steps{
                script {
                    echo 'building docker image....'
                    sh '''
                        docker build -t eladwy/backend:$GIT_COMMIT .
                    '''
                }
            }
        }

        stage('Trivy Vulnarability Scanner'){
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                       sh '''
                            trivy image eladwy/backend:$GIT_COMMIT \
                                    --severity LOW,MEDIUM \
                                    --exit-code 0 \
                                    --quiet \
                                    --format json -o trivy-success.json
                                
                            
                                trivy image eladwy/backend:$GIT_COMMIT \
                                    --severity HIGH,CRITICAL \
                                    --exit-code 1 \
                                    --quiet \
                                    --format json -o trivy-fail.json
                        '''
                    }
            }
            post {
                always {
                    sh '''
                        trivy convert \
                            --format template --template "@/usr/local/share/trivy/templates/html.tpl" \
                            --output trivy-image-MEDIUM-results.html trivy-success.json

                        trivy convert \
                            --format template --template "@/usr/local/share/trivy/templates/html.tpl" \
                            --output trivy-image-CRITICAL-results.html trivy-fail.json

                        trivy convert \
                            --format template --template "@/usr/local/share/trivy/templates/junit.tpl" \
                            --output trivy-image-MEDIUM-results.xml trivy-success.json

                        trivy convert \
                            --format template --template "@/usr/local/share/trivy/templates/junit.tpl" \
                            --output trivy-image-CRITICAL-results.xml trivy-fail.json
                    '''
                }
            }
        }
        stage('Push Docker Image'){
            steps{
                    withDockerRegistry(credentialsId: 'docker-hub', url: "https://index.docker.io/v1/") {
                        echo 'pushing docker image...'
                        sh '''
                            docker push eladwy/backend:$GIT_COMMIT
                        '''
                    }
                }
        }
         stage('Deploy to aws'){
            when{
                branch 'features'
            }
            steps {
                script {
                    def gitCommit = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    sshagent(['aws-dev-deploy']) {
                        sh '''
                            ssh -o StrictHostKeyChecking=no ubuntu@157.175.177.0 "
                                sudo docker image prune -a -f
                                sudo docker network create meatshop-net || true
                                # Only remove containers if they exist
                                CONTAINERS=\$(sudo docker ps -q)
                                if [ ! -z \"\$CONTAINERS\" ]; then
                                    sudo docker rm -f \$CONTAINERS
                                fi
                                
                                if docker ps -a | grep -q \\"mymysql\\"; then
                                    echo \\"Container Found, Stopping...\\"
                                    docker stop \\"mymysql\\" && docker rm \\"mymysql\\"
                                    echo \\"Container stopped and removed\\"
                                fi
                                
                                docker run -d --name mymysql --network meatshop-net -e MYSQL_ROOT_PASSWORD=mypass -e MYSQL_DATABASE=meatshop -p 3306:3306 -v mysql_data:/var/lib/mysql mysql
                                
                                if sudo docker ps -a | grep -q \\"backend\\"; then
                                    echo \\"Container Found, Stopping...\\"
                                    sudo docker stop \\"backend\\" && sudo docker rm \\"backend\\"
                                    echo \\"Container stopped and removed\\"
                                fi
                                
                                sudo docker run -d --network meatshop-net -e DJANGO_SETTINGS_MODULE=meatshop.settings -e LOCAL_DB_NAME=meatshop -e LOCAL_DB_PORT=3306 -e LOCAL_DB_HOST=mymysql -e LOCAL_DB_USER=root -e LOCAL_DB_PASSWORD=mypass -e ALLOWED_HOSTS=* -p 80:8000 --name backend eladwy/backend:$GIT_COMMIT
                            "
                        '''
                    }
                }
            }
        }
        stage('K8S Update Image Tag') {
            when {
                branch 'PR*'
            }
            steps {
                script {
                    echo 'updating image tag in k8s...'
                    sh 'git clone -b main https://github.com/abdelrahman-eladwy/meatshop-k8s.git'
                    dir('meatshop-k8s') {
                        sh '''
                            echo "12345"
                            git checkout main
                            git checkout -b feature$BUILD_ID
                            sed -E -i "s-(eladwy|borhom11)/backend:.*-eladwy/backend:$GIT_COMMIT-g" backend/deployment.yaml
                            cat frontend/deployment.yaml

                            git config --global user.email "abdoahmed32522@gmail.com"
                            git remote set-url origin https://$GITHUB_TOKEN@github.com/abdelrahman-eladwy/meatshop-k8s.git
                            git add .
                            git commit -m "updating image tag to $GIT_COMMIT"
                            git push -u origin feature$BUILD_ID
                        '''
                    }
                }
            }
        }

        stage('K8S - Raise PR') {
            when {
                branch 'PR*'
            }
            steps {
                script {
                    def branchName = "feature${BUILD_ID}"
                    sh """
                        curl -L \\
                            -X POST \\
                            -H "Accept: application/vnd.github+json" \\
                            -H "Authorization: Bearer \$GITHUB_TOKEN" \\
                            -H "X-GitHub-Api-Version: 2022-11-28" \\
                            https://api.github.com/repos/abdelrahman-eladwy/meatshop-k8s/pulls \\
                            -d '{"title":"Update docker image to latest version","body":"Automated PR to update the backend image tag to commit $GIT_COMMIT","head":"${branchName}","base":"main"}'
                    """
                }
            }
        }

        stage('DAST - OWASP ZAP') {
            when {
                branch 'PR*'
            }
            steps {
                sh '''
                    echo "Trigger"
                    chmod 777 $(pwd)
                    docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
                        -t http://157.175.177.0/schema/?format=json \
                        -r zap_report.html \
                        -f openapi \
                        -w zap_report.md \
                        -x zap_report.xml \
                        -J zap_report.json
                '''
            }
        }




    }
    post {
        always {
            script {
                if (fileExists('meatshop-k8s')) {
                    sh 'rm -rf meatshop-k8s'
                }
            }
        }
    
        success {
            echo 'Tests passed! The build is ready for deployment.'
        }
        failure {
            echo 'Tests failed! Please check the logs for details.'
        }
        cleanup {
            echo 'Cleaning up the virtual environment..'
            sh '''
                if [ -d "$VENV_DIR" ]; then
                    rm -rf $VENV_DIR
                fi
            '''
        }
    }
}