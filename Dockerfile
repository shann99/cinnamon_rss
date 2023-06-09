FROM python:3.10
RUN pip install poetry
WORKDIR /app    
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi
COPY . /app
CMD python3 cinnamon_rss.py