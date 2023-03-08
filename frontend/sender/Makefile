run:
	docker rm fastapi || true
	docker rmi fastapi || true
	docker build -t fastapi .
	docker run --name fastapi -p 80:80 fastapi