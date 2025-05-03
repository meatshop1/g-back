pipeline{
    
    agent any

    stages {
        stage('Installing Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                 sh '''
                        pip install -r requirements.txt
                    '''
            }
        }
    }
        
}