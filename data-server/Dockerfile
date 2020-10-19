FROM python:3

WORKDIR /usr/src/app

EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD [ "python", "./main.py" ]
