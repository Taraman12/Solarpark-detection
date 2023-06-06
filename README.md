[![Linting](https://github.com/Taraman12/Solarpark-detection/actions/workflows/lint.yml/badge.svg)](https://github.com/Taraman12/Solarpark-detection/actions/workflows/lint.yml)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)(https://github.com/Taraman12/Solarpark-detection/actions/workflows/docker.yml)
# Solarpark-detection
 Continuous solar park detection from satellite imagery with Deep Learning

# ToDos:
- [ ] Add a description of the project
- [ ] Add pre-commit hooks
- [ ] Add docformatter again
- [ ] Add mypy again
- [ ] Add readTheDocs

 # Create requirements.txt
 check if all groups are correct
 
 poetry export -f requirements.txt --output requirements.txt --without-hashes --with main --with lint --with dev --with ml-model --with api 

# problems with psycopg2:
sudo apt-get install libpq-dev

mypy vscode settings:
"mypy.dmypyExecutable":".//.env//Lib//site-packages//mypy//dmypy_server.py"