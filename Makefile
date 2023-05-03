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

# lint-mypy:
# 	@mypy ./src --exclude ./src/frontend --check

# lint-mypy-report:
# 	@mypy ./src --html-report ./mypy_html

format: format-black format-isort # format-docformatter

lint: lint-black lint-isort lint-flake8 
# lint-mypy
