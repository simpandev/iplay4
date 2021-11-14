FROM python:3.9-alpine
WORKDIR /opt/iplay4
ENV IPLAY4_DIR=/opt/iplay4
ENV IPLAY4_ARCH_DIR=/media/arch
COPY dist/iplay4* ./
RUN mkdir playlists
RUN mkdir -p /media/arch
COPY py/iplay-cli.py /usr/bin
RUN chmod u+x /usr/bin/iplay-cli.py
COPY py/http_server.py /usr/bin
RUN chmod u+x /usr/bin/http_server.py
COPY py/requirements.txt ./
RUN pip install -r requirements.txt
CMD http_server.py -b 0.0.0.0 -d $IPLAY4_DIR
