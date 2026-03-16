
permissions:
	chmod +x docker/localstack/init/*.sh

up: permissions
	docker-compose up --build

build:
	docker-compose build

down:
	docker-compose down

logs:
	docker-compose logs -f

test: build
	docker-compose run --rm test

format:
	black .
