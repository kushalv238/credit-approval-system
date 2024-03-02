FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y python3-venv
RUN python -m venv venv
ENV PATH="/code/venv/bin:$PATH"

COPY . /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["bash"]