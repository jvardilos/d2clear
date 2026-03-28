FROM python

COPY d2clear.py /
COPY requirements.txt /
RUN pip install -r requirements.txt

CMD ["python", "d2clear.py"]
