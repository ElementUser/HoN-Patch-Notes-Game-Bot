# Dependencies

- PRAW API: https://www.storybench.org/how-to-scrape-reddit-with-python/

  - Used to communicate with the Reddit API

- TinyDB: https://tinydb.readthedocs.io/en/stable/

  - Used to implement and communicate with a simple, document-oriented database contained in 1 local file

- Poetry: https://python-poetry.org/docs/
  - Used for dependency management & run the bot script in a virtualenv
  - Ensures that the bot script will run in a consistent environment regardless of its host system

# Dev Dependencies

- black: https://black.readthedocs.io/en/stable/

  - Strict code formatter for Python

- flake8: https://flake8.pycqa.org/en/latest/

  - Python code linter

- mypy: http://mypy-lang.org/

  - Optional static type checker for Python code

- pytest: https://docs.pytest.org/en/stable/

  - Unit testing library

- pytest-cov: https://pytest-cov.readthedocs.io/en/latest/

  - Outputs testing coverage reports in the terminal

# Unit Testing

- https://semaphoreci.com/community/tutorials/testing-python-applications-with-pytest
- CI/CD & Unit Testing: https://realpython.com/python-continuous-integration/#single-source-repository

# Continuous Integration (CI) Pipeline

- The CI pipeline for this project can be found [here](https://github.com/ElementUser/HoN-Patch-Notes-Game-Bot/actions)
- Reference for the .yml config file: https://github.com/python-poetry/poetry/blob/master/.github/workflows/main.yml
- Custom Status Badges: [shields.io](https://shields.io/)
