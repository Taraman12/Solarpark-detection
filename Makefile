format-black:
	@black ./src --exclude ./src/frontend

format-docformatter:
	@docformatter --in-place --recursive ./src

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
	

# lint-mypy:
# 	@mypy ./src --exclude ./src/frontend --check

# lint-mypy-report:
# 	@mypy ./src --html-report ./mypy_html

format: format-black format-isort # format-docformatter

lint: lint-black lint-isort lint-flake8 
# lint-mypy

requirements: api-requirements downloader-requirements ml-model-requirements preprocessing-requirements
