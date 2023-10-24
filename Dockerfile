FROM python:3.10.13
ENV PYTHONUNBUFFERED = 1
RUN "mkdir -c app"
WORKDIR /app/
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY . main.py /app/
EXPOSE 8080
CMD [ "python3","main.py"]
