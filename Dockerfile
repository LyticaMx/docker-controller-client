FROM python:3.6

# build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev

# Web app source code
COPY . /app
WORKDIR /app

# POETRY SETUP
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN wget -O - https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && poetry --version \
    && poetry config virtualenvs.create false

RUN poetry install --no-dev --no-interaction --no-ansi -vvv

CMD ["python", "docker-controller-client.py", "-f", "/app/json_example/config.json", "-d"]