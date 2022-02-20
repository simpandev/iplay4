FROM python:3.9-alpine

ENV IPLAY=/opt/iplay4
ENV IPLAY_BIN=$IPLAY/bin
ENV WEB=$IPLAY/web
ENV PLAYLISTS=$WEB/playlists
ENV ARCHIVE=/media/arch
ENV PATH=$PATH:$IPLAY_BIN

WORKDIR $IPLAY

RUN mkdir -p $PLAYLISTS
RUN mkdir -p IPLAY_BIN
RUN mkdir -p $ARCHIVE

COPY py/requirements.txt $IPLAY/
RUN pip install -r $IPLAY/requirements.txt

COPY py/command.py $IPLAY_BIN/
COPY py/http_server.py $IPLAY_BIN/
COPY py/iplay_processor.py $IPLAY_BIN/
COPY py/iplay-cli.py $IPLAY_BIN/
RUN chmod u+x $IPLAY_BIN/*

COPY dist/iplay4* $WEB/

CMD http_server.py -b 0.0.0.0 -d $WEB
