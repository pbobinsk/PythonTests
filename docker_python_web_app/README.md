1.
flask run

2.
docker build -t my-flask-app .
docker run --name moja-apka -d -p 5000:5000  my-flask-app

UWAGA:
docker network create moja-siec
docker run --name moja-apka --network moja-siec -d -p 5000:5000  my-flask-app
NODE_API_URL = "http://moje-api:3000/api/data"
przez env
docker run  -e NODE_API_URL=http://moje-api:3000/api/data --name moja-apka --network moja-siec -d -p 5000:5000  my-flask-app

docker stop moja-apka
docker rm moja-apka

3.
docker-compose