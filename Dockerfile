FROM gcr.io/bazel-public/bazel:latest

# upgrade pip
RUN python3 -m pip install --upgrade pip

# install aiohttp for openai
RUN pip3 install aiohttp==3.8.5

USER root

# generic dependencies
RUN apt install -y gnupg gpg curl lsb-release wget

# install MongoDB and mongoengine
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt update && \
    apt install -y mongodb-org && \
    pip3 install mongoengine==0.27.0

# install Redis
RUN curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list && \
    apt-get update && \
    apt-get install -y redis redis-server && \
    pip3 install rq==1.15.1 redis==5.0.0

# install supervisor
RUN apt install supervisor

USER ubuntu

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
