FROM alpine:3.6

MAINTAINER Anthony Almarza <anthony.almarza@gmail.com>

# ENV PYENV_ROOT /root/.pyenv
ENV PATH /root/.pyenv/shims:/root/.pyenv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV DOCKERIZE_VERSION v0.3.0

RUN apk add --no-cache --update \
    musl \
    linux-headers \
    build-base \
    bash \
    git \
    ca-certificates \
    python2 \
    python2-dev \
    py-setuptools \
    py-virtualenv \
    curl \
    bzip2-dev \
    ncurses-dev \
    openssl \
    openssl-dev \
    readline-dev \
    sqlite-dev \
    openssh \
    docker \

    && curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash \

    && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \

    && rm -rf /var/cache/apk/* \

    && pyenv install -s -v 2.7.14 \
    && pyenv install -s -v 3.5.4 \
    && pyenv install -s -v 3.6.3

CMD ['/bin/bash']
