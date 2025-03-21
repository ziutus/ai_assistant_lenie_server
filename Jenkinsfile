pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
    }
    environment {
        INSTANCE_ID = "${params.INSTANCE_ID}"
        AWS_REGION = "${params.AWS_REGION}"
    }

    stages {
        stage('Check and Start AWS Machine') {
            agent {
                label 'built-in'
            }

            steps {
                script {
                    def instanceID = env.INSTANCE_ID

                    echo "Using instance ID: ${instanceID}"

                    def instanceState = sh(
                        script: """
                            aws ec2 describe-instances \
                                --instance-ids ${instanceID} \
                                --query "Reservations[0].Instances[0].State.Name" \
                                --output text \
                                --region ${env.AWS_REGION}
                            """,
                        returnStdout: true
                    ).trim()

                    echo "Current state of AWS instance ${instanceID}: ${instanceState}"

                    if (instanceState == "terminated") {
                        error "AWS instance ${instanceID} has been terminated. Cannot start it. Please recreate the instance."
                    } else if (instanceState != "running") {
                        echo "Starting AWS instance..."
                        sh """
                            aws ec2 start-instances --instance-ids ${instanceID} --region ${env.AWS_REGION}
                            """
                        sh """
                            aws ec2 wait instance-running --instance-ids ${instanceID} --region ${env.AWS_REGION}
                            """
                        echo "AWS instance ${instanceID} is now running."
                    } else {
                        echo "AWS instance ${instanceID} is already running."
                    }
                }
            }
        }

        stage('Code checkout from GitHub') {
            agent {
                label 'aws-ec2-runner'
            }
            steps {
                script {
                    cleanWs()
                    git credentialsId: 'github-token', url: 'https://github.com/ziutus/ai_assistant_lenie_server', branch: "${env.BRANCH_NAME}"
                    sh "ls -l ${WORKSPACE}"
                }
            }
        }

        stage('report dir creation') {
            agent {
                label 'aws-ec2-runner'
            }
            steps {
                echo 'create directory for reports'
                sh 'mkdir ${WORKSPACE}/results/'
            }
        }

        stage('Run Semgrep Security Check') {
            agent {
                label 'aws-ec2-runner'
            }
            steps {
                script {
                    echo 'Running Semgrep Security Check'

                    sh '''
                        pip install semgrep
                    '''

                    sh '''
                        semgrep --config=auto --output semgrep-report.json || true
                    '''

                    echo 'Storing Semgrep report as an artifact'
                    sh '''
                        mkdir -p ${WORKSPACE}/results/
                        mv semgrep-report.json ${WORKSPACE}/results/
                    '''
                }
            }
            post {
                always {
                    echo 'Archiving Semgrep report'
                    archiveArtifacts artifacts: 'results/semgrep-report.json', fingerprint: true
                }
            }
        }

        stage('Run TruffleHog Scan') {
            agent {
                label 'aws-ec2-runner'
            }
            steps {
                script {
                    echo 'Running TruffleHog Secret Detection'

                    echo 'Ensuring results directory exists...'
                    sh 'mkdir -p results/'

                    sh '''
                    docker run --rm --name trufflehog \
                        trufflesecurity/trufflehog:latest git file://. \
                        --only-verified --bare 2>&1 | tee results/trufflehog.txt
                '''
                }
            }
            post {
                always {
                    echo 'Archiving TruffleHog report'
                    archiveArtifacts artifacts: 'results/trufflehog.txt', fingerprint: true
                }
            }
        }

        //    NIE DZIAŁA, trzeba sprawdzić
        //stage('Run OSV Scanner') {
        //    agent {
        //        label 'aws-ec2-runner' // Agregat, który był używany w twoich innych zadaniach
        //    }
        //    steps {
        //        script {
        //            echo 'Running OSV Scanner'
        //
        //            // Tworzymy katalog na wyniki skanowania
        //            sh 'mkdir -p results/'
        //
        //            // Uruchamiamy OSV Scanner z zależnościami określonymi w requirements.txt
        //            sh '''
        //                /usr/local/bin/osv-scanner scan --lockfile requirements.txt
        //            '''
        //        }
        //    }
        //    post {
        //        always {
        //            // Archiwizowanie wygenerowanego raportu OSV Scanner
        //            echo 'Archiving OSV Scanner results'
        //            archiveArtifacts artifacts: 'results/osv_scan_results.json', fingerprint: true
        //        }
        //        cleanup {
        //            // Oczyszczanie przestrzeni roboczej po zakończeniu
        //            echo 'Cleaning up workspace after OSV scan'
        //            cleanWs()
        //        }
        //    }
        //}

        stage('Python tests') {
            parallel {

                stage('Run Pytest') {
                    agent {
                        label 'aws-ec2-runner'
                    }
                    steps {
                        script {
                            echo 'Installing requirements...'
                            sh "pwd; ls -l"
                            sh """
                        pip install -r requirements.txt
                        """

                            echo 'Ensuring results directory exists...'
                            sh """
                        mkdir -p pytest-results
                        """

                            echo 'Running Pytest...'
                            sh """
                        pytest --self-contained-html --html=pytest-results/report.html || true
                        """


                        }

                        echo 'Archiving test results...'
                        archiveArtifacts artifacts: 'pytest-results/**/*', allowEmptyArchive: true
                    }
                    post {
                        always {
                            echo 'Pytest stage completed. Results saved as artifacts.'
                        }
                    }
                }

                stage('Run Flake8 Style Check') {
                    agent {
                        label 'aws-ec2-runner'
                    }
                    steps {
                        script {
                            echo 'Running Flake8 Style Check'

                            echo 'Installing flake8-html'
                            sh '''
                        python3 -m pip install --upgrade pip
                        pip3 install flake8-html
                    '''

                            echo 'Running Flake8 and generating HTML report'
                            sh '''
                        mkdir -p flake_reports
                        flake8 --format=html --exclude=ai_dev3 --htmldir=flake_reports/
                    '''
                        }
                    }
                    post {
                        always {
                            echo 'Archiving Flake8 HTML Report'
                            archiveArtifacts artifacts: 'flake_reports/**', fingerprint: true
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            node('built-in') {

                script
                {
                    echo"Attempting to stop AWS EC2 instance..."
                    try {
                        sh """
                        aws ec2 stop-instances --instance-ids ${env.INSTANCE_ID} --region ${env.AWS_REGION}
                        """
                        sh """
                            aws ec2 wait instance-stopped --instance-ids ${env.INSTANCE_ID} --region ${env.AWS_REGION}
                        """
                        echo " AWS instance ${env.INSTANCE_ID} has been successfully stopped."
                    } catch (err) {
                    echo "Failed to stop instance ${env.INSTANCE_ID}: ${err.getMessage()}"
                    }
                }
            }
        }
    }
}
