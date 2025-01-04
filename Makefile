# Docker
up:
	docker-compose up -d

build:
	docker-compose build

down:
	docker-compose down

prune:
	docker system prune -a --volumes


# コンテナ
app:
	docker-compose exec app /bin/bash


# ログ
log-app:
	docker-compose logs -f app
