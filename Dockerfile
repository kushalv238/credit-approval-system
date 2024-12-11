FROM python:3 AS compiler

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y python3-pip && apt-get install -y python3-venv

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

FROM python:3 AS runner

WORKDIR /code

COPY --from=compiler /venv /venv

ENV PATH="/venv/bin:$PATH"

COPY . /code/