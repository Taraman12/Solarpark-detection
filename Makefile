format-black:
	@black ./src --exclude ./src/frontend

format-docformatter:
	@docformatter --config ./pyproject.toml ./src

format-isort:
	@isort ./src --skip ./src/frontend

lint-black:
	@black ./src --exclude ./src/frontend --check

lint-isort:
	@isort ./src --skip ./src/frontend --check

lint-flake8:
	@flake8 ./src --exclude ./src/frontend

# update names of folders
api-requirements:
	@poetry export -f requirements.txt --output ./src/api/requirements.txt --without-hashes --with api

downloader-requirements:
	@poetry export -f requirements.txt --output ./src/downloader/requirements.txt --without-hashes --with downloader

ml-model-requirements:
	@poetry export -f requirements.txt --output ./src/ML_Modell/requirements.txt --without-hashes --with ml-model

preprocessing-requirements:
	@poetry export -f requirements.txt --output ./src/preprocessing/requirements.txt --without-hashes --with preprocessing

ml-serve-requirements:
	@poetry export -f requirements.txt --output ./src/ml-serve/requirements.txt --without-hashes --with ml-serve

dev-requirements:
	@poetry export -f requirements.txt --output ./requirements-dev.txt --without-hashes --with dev

# lint-mypy:
# 	@mypy ./src --exclude ./src/frontend --check

# lint-mypy-report:
# 	@mypy ./src --html-report ./mypy_html

format: format-black format-isort # format-docformatter

lint: lint-black lint-isort lint-flake8
# lint-mypy

requirements: api-requirements downloader-requirements ml-model-requirements preprocessing-requirements ml-serve-requirements dev-requirements

start-api:
	 @cd src/api && uvicorn app.main:app --reload
