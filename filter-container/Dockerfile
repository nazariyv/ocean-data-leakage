FROM nickgryg/alpine-pandas:3.8.3

WORKDIR /app

COPY ./filter /app/filter

RUN pip install -r filter/requirements.txt --no-cache-dir --no-color

ENTRYPOINT ["python", "-m", "filter.main"]
