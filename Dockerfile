FROM python:3.7

ENV FLASK_APP "flaskr"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

EXPOSE 5000
CMD flask run --host=0.0.0.0