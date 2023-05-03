format-black:
	@black ./src --exclude ./src/frontend

format-docformatter:
	@docformatter ./src --exclude ./src/frontend --in-place --recursive

format-isort:
	@isort ./src --skip ./src/frontend

lint-black:
	@black ./src --exclude ./src/frontend --check

lint-isort:
	@isort ./src --skip ./src/frontend --check

lint-flake8:
	@flake8 ./src --exclude ./src/frontend 

# lint-mypy:
# 	@mypy ./src

# lint-mypy-report:
# 	@mypy ./src --html-report ./mypy_html

format: format-black format-docformatter format-isort

lint: lint-black lint-isort lint-flake8 
# lint-mypy
