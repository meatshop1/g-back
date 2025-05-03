pipeline{
    
    agent any

    stages {
         stage('Installing Dependencies'){
            steps{
                script {
                    echo 'Installing Python dependencies...'
                    sh '''
                        python3 -m venv venv
                        source venv/bin/activate
                        python3 -m pip install --upgrade pip
                        pip install -r requirements.txt
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