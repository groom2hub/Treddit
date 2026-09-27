FROM jenkins/jenkins:2.568.3-lts-jdk21

# docker CLI와 buildx 플러그인만 공식 이미지에서 복사해 온다 (데몬은 호스트 것을 사용)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker/buildx-bin:latest /buildx /usr/libexec/docker/cli-plugins/docker-buildx

# 플러그인을 이미지 빌드 시점에 설치한다 (Plugins as Code)
# 기본 다운로드 리다이렉터가 가끔 죽은 미러를 고르므로 일본 미러로 고정
ENV JENKINS_UC_DOWNLOAD=https://ftp.yz.yamagata-u.ac.jp/pub/misc/jenkins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt