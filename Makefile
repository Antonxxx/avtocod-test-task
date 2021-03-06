.EXPORT_ALL_VARIABLES:
PROJECT ?= ''
export PYTHONPATH := $(shell pwd):$(PYTHONPATH)

build:
	docker-compose -p ${PROJECT} build


up:
	docker-compose -p ${PROJECT} up -d

down:
	docker-compose -p ${PROJECT} down

clear:
	find . -name \*.pyc -delete &&  find . -name "__pycache__" -delete

pip:
	pip install --upgrade pip && pip install -r ./requirements.txt

logging:
	docker-compose logs -f ${PROJECT}

ps:
	docker-compose ps

restart:
	docker-compose restart ${PROJECT}

load:
	docker-compose run --rm task python /app/avtocod-test-task/app.py --command load --depth ${DEPTH} --root ${ROOT}

get:
	docker-compose run --rm task python /app/avtocod-test-task/app.py --command get --number ${NUMBER} --root ${ROOT}
