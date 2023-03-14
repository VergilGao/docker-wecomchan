FROM python:3.10-alpine as build-stage

# Official Python base image is needed or some applications will segfault.
# PyInstaller needs zlib-dev, gcc, libc-dev, and musl-dev
RUN apk --update --no-cache add \
    zlib-dev \
    musl-dev \
    libc-dev \
    gcc \
    g++ \
    git \
    make \
    cmake \
    upx \
    # download utils
    wget && \
    # update pip
    pip install --upgrade pip

ARG PYINSTALLER_SOURCE_VERISON
ENV PYINSTALLER_SOURCE_VERISON=${PYINSTALLER_SOURCE_VERISON:-4222dc4d623633df713e69b03df66ec10a27df93}

# build bootloader for alpine
RUN mkdir -p /tmp/pyinstaller && \
    wget -O- https://github.com/pyinstaller/pyinstaller/archive/$PYINSTALLER_SOURCE_VERISON.tar.gz | tar xz -C /tmp/pyinstaller --strip-components 1 && \
    cd /tmp/pyinstaller/bootloader && \
    CFLAGS="-Wno-stringop-overflow -Wno-stringop-truncation" python ./waf configure --no-lsb all && \
    pip install .. && \
    rm -Rf /tmp/pyinstaller

ADD /root/ /pyinstaller/
RUN chmod a+x /pyinstaller/*

ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
ADD src/ /tmp/app/
RUN cd /tmp/app/ && \
    /pyinstaller/pyinstaller.sh \
        -n wecomchan \
        --onedir main.py \
        --python-option u \
        --hidden-import server.py
ADD config.template /tmp/app/dist/config.template
ADD docker-entrypoint.sh /tmp/app/dist/docker-entrypoint.sh
RUN chmod +x -R /tmp/app/dist

FROM alpine:3.16

LABEL maintainer="VergilGao"
LABEL org.opencontainers.image.source="https://github.com/VergilGao/docker-wecomchan"

ENV TZ="Asia/Shanghai"
ENV UID=99
ENV GID=100
ENV UMASK=022

RUN apk add --no-cache --update \
      ffmpeg \
      coreutils \
      shadow \
      su-exec && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /app && \
    mkdir -p /data && \
    mkdir -p /config && \
    useradd -d /config -s /bin/sh abc && \
    chown -R abc /config && \
    chown -R abc /data
    
COPY --from=build-stage /tmp/app/dist/ /app/

VOLUME [ "/data", "/config" ]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
