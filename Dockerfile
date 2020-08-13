FROM python:alpine

WORKDIR /app

RUN chown nobody:nogroup /app \
	&& apk add --no-cache --virtual .build-deps gcc build-base python-dev libffi-dev libressl-dev

ADD requirements.txt .
RUN pip install -r requirements.txt \
	&& apk del .build-deps

COPY --chown=nobody:nogroup . .
USER nobody

ENTRYPOINT [ "python", "main.py" ]
