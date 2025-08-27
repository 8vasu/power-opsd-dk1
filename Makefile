APP=opsd_app

.PHONY: build up down logs fetch optimize plot run clean

build:
	docker compose up --build -d

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f $(APP)

fetch:
	docker exec -it $(APP) bash -lc "cd src && python fetch_and_store.py"

optimize:
	docker exec -it $(APP) bash -lc "cd src && python optimize.py"

plot:
	docker exec -it $(APP) bash -lc "cd src && python plot.py"

run:
	docker exec -it $(APP) bash -lc "cd src && python fetch_and_store.py && python optimize.py && python plot.py"

clean:
	docker compose down -v
