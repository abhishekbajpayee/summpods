FROM gcr.io/bazel-public/bazel:latest

# upgrade pip
RUN python3 -m pip install --upgrade pip

USER root

# generic dependencies
RUN apt install -y gnupg gpg curl lsb-release wget

# install MongoDB and mongoengine
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt update && \
    apt install -y mongodb-org && \
    pip3 install mongoengine==0.27.0 \
                 flask-mongoengine==1.0.0

# install supervisor
RUN apt install supervisor

# install Flask and related libs
RUN pip3 install Flask==2.2.5 \
                 Flask-Admin==1.6.1 \
                 Jinja2>=2.10.1 \
                 Werkzeug>=0.15 \
                 itsdangerous>=0.24 \
                 click>=5.1 \
                 MarkupSafe==2.0.1 \
                 Blinker>=1.6 \
                 Flask-Material>=0.1

# install general pip dependencies
RUN pip3 install requests==2.30.0 \
                 urllib3>=2.0 \
                 chardet>=5.0 \
                 idna==3.4 \
                 certifi==2023.7.22 \
                 PyYAML==6.0 \
                 openai==0.27.8 \
                 Flake8==6.1.0 \
                 pyflakes==3.1.0 \
                 pycodestyle==2.11.0 \
                 tiktoken==0.4.0

# install ffmpeg and pydub
RUN apt install -y ffmpeg && \
    pip3 install pydub==0.25.1

USER ubuntu

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
