pipeline{
    
    agent any

    stages {
        stage('Installing Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                 sh '''
                        python -m pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
            }
        }
    }
        
}