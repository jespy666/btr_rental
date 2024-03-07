![Logo](https://i.ibb.co.com/J2nWymn/bro.png)
## Description  
***  
### Repository for developing a web application for the Broteamracing team, specializing in the rental of enduro motorcycles in Saint-Petersburg (Russia)
[Web Application Link](URL)  
[Site Monitor](https://stats.uptimerobot.com/OPGkoIHLmO)  

![Website](https://img.shields.io/website?url=https%3A%2F%2Fbroteamracing.ru%2F&up_message=available&up_color=green&down_message=down&down_color=red&label=Status)
### CodeClimate & CI
***
[![Maintainability](https://api.codeclimate.com/v1/badges/2eefa3d3a18210f244ae/maintainability)](https://codeclimate.com/github/jespy666/btr_rental/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/2eefa3d3a18210f244ae/test_coverage)](https://codeclimate.com/github/jespy666/btr_rental/test_coverage)
[![lint&tests](https://github.com/jespy666/btr_rental/actions/workflows/tests&style.yml/badge.svg)](https://github.com/jespy666/btr_rental/actions/workflows/tests&style.yml)  

### Technologies  
***
#### Core
![Static Badge](https://img.shields.io/badge/Python-3.11-blue)
![Static Badge](https://img.shields.io/badge/Django-4.2.6-green)  
#### Database
![Static Badge](https://img.shields.io/badge/PostgreSQL-16.2-brown)
#### Frontend
![Static Badge](https://img.shields.io/badge/Django%20Bootstrap-5-purple)
#### Broker & tasks
![Static Badge](https://img.shields.io/badge/Redis-5.0.1-red)
![Static Badge](https://img.shields.io/badge/Celery-5.3.4-green)
#### Other
![Static Badge](https://img.shields.io/badge/Docker-25.0.2-blue)
![Static Badge](https://img.shields.io/badge/Aiogram-3.3.0-cyan)
### Internalization
***
Web application translated into 2 languages:
+ *RU (Russian)*
+ *EN (English)*
### Documentation
***
#### Install
- `git clone https://github.com/jespy666/btr_rental.git`
- `cd btr_rental`
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r req/dev.txt` 
- `make collectstatic`
- `python3 manage.py migrate`
#### Environments
- *create .env file in project root* `touch .env`
- *list of needed variables you can see at:*
    - [.env](https://github.com/jespy666/btr_rental/blob/main/.envexample)
#### Additional services (for full operation)  
 - *redis* `make redis`
 - *celery* `make celery`
 - *celery-beat* `make celery-beat`
 - *tg bot* `make bot`
#### Run Dev server  
- `make dev`
#### Test & Linter
- *linter* `make lint`
- *test* (**redis required**) `make test`
- *test-coverage* (**redis required**) `make test-coverage`
#### Internalization
- *create messages file* `make messages`
- **translate something**
- *compile messages file* `make compile`
#### Developers
[jespy666](https://github.com/jespy666)



