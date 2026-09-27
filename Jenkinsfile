pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        // 빌드마다 고유한 테스트 이미지 태그 (브랜치 이름의 '/' 등 docker 태그에 못 쓰는 문자는 '-'로)
        CI_TAG   = "${env.BUILD_TAG}".replaceAll('[^A-Za-z0-9_.-]', '-').toLowerCase()
        REGISTRY = 'ghcr.io/groom2hub'
        // GHCR 패키지를 이 레포와 연결하는 라벨
        SOURCE_LABEL = 'org.opencontainers.image.source=https://github.com/groom2hub/Treddit'
    }

    stages {
        stage('Test') {
            parallel {
                stage('server') {
                    steps {
                        sh 'docker build --target test -t treddit-server-test:$CI_TAG server'
                        sh 'docker run --rm treddit-server-test:$CI_TAG'
                    }
                }
                stage('pipeline') {
                    steps {
                        sh 'docker build --target test -t treddit-pipeline-test:$CI_TAG pipeline'
                        sh 'docker run --rm treddit-pipeline-test:$CI_TAG'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    // 커밋 SHA 앞 7자리를 이미지 태그로 쓴다
                    env.IMAGE_TAG = sh(script: 'git rev-parse --short=7 HEAD', returnStdout: true).trim()
                }
                sh 'docker build --label $SOURCE_LABEL -t $REGISTRY/treddit-server:$IMAGE_TAG server'
                sh 'docker build --label $SOURCE_LABEL -t $REGISTRY/treddit-pipeline:$IMAGE_TAG pipeline'
                sh 'docker build --label $SOURCE_LABEL -t $REGISTRY/treddit-frontend:$IMAGE_TAG frontend'
            }
        }

        stage('Push') {
            when { branch 'main' }   // main에 머지된 코드만 레지스트리에 올린다
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-token',
                                                  usernameVariable: 'GH_USER',
                                                  passwordVariable: 'GH_TOKEN')]) {
                    sh '''
                        echo "$GH_TOKEN" | docker login ghcr.io -u "$GH_USER" --password-stdin
                        for svc in server pipeline frontend; do
                            docker push "$REGISTRY/treddit-$svc:$IMAGE_TAG"
                        done
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker logout ghcr.io || true
                docker rmi treddit-server-test:$CI_TAG treddit-pipeline-test:$CI_TAG || true
                docker rmi $REGISTRY/treddit-server:$IMAGE_TAG $REGISTRY/treddit-pipeline:$IMAGE_TAG $REGISTRY/treddit-frontend:$IMAGE_TAG || true
            '''
        }
    }
}