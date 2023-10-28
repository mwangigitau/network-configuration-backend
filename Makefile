install:
	#install dependencies
	pip3 install  --upgrade pip &&\
	pip3 install -r requirements.txt
lint:
	#make lint
	pylint --disable=R,C *.py src/*.py
format:
	#format code
	black *.py src/*.py
test:
	#test code
	python3 -m pytest -vv --cov=src --cov=main test_*.py
build:
	#run docker-compose
	#docker compose up --build
deploy:
	#deploy
all:
	make install lint format test build deploy