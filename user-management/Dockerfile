FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py  
ENV FLASK_ENV=development   
ENV FLASK_DEBUG=1   

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]