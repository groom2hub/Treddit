pipeline {
    agent any

    options {
        timestamps()                                    // 로그 줄마다 시간 표시
        timeout(time: 30, unit: 'MINUTES')              // 무한 대기 방지
        buildDiscarder(logRotator(numToKeepStr: '20'))  // 빌드 기록은 최근 20개만 보관
    }

    environment {
        // 빌드마다 고유한 이미지 태그. 여러 브랜치가 동시에 빌드돼도 이름이 겹치지 않게 한다.
        // BUILD_TAG 예: jenkins-Treddit-phase3%2Fjenkins-3 → docker 태그에 못 쓰는 문자를 '-'로 바꾼다
        CI_TAG = "${env.BUILD_TAG}".replaceAll('[^A-Za-z0-9_.-]', '-').toLowerCase()
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
    }

    post {
        always {
            // 테스트 이미지는 CI에서만 쓰므로 지운다 (호스트 디스크가 쌓이지 않게)
            sh 'docker rmi treddit-server-test:$CI_TAG treddit-pipeline-test:$CI_TAG || true'
        }
    }
}