pipeline{
    
    agent any

    stages {
         stage('Installing Dependencies'){
            steps{
                script {
                    echo 'Installing Python dependencies...'
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
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
                        . venv/bin/activate
                        pytest --maxfail=1 --disable-warnings -q
                    '''
                }
            }
        }
        
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
                echo "Cleaning up resources..."
                rm -rf venv
            '''
        }
    }
}