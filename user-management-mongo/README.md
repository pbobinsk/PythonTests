1.
flask run
config w .flaskenv

2.
docker-compose.exe  up --build
docker-compose.exe  down

3.
docker build -t user-management-mongo:latest .
docker stack deploy -c swarm.yml user-flask-slack

docker build -t user-management-mongo:v2 .
docker service update --image user-management-mongo:v2 user-flask-slack_flask_app

docker stack rm  user-flask-slack