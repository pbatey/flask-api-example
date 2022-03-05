from python:3.9.7

RUN pip install uwsgi

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY service.wsgi service.wsgi
COPY app app

# copy frontend
#RUN rm -rf app/public
#COPY frontend/dist app/public

EXPOSE 80
ENV PORT 80

USER 1001
CMD uwsgi --master --enable-threads --http :$PORT --wsgi-file service.wsgi

