FROM dgdo-python-base

WORKDIR /app
COPY services/python/ml_feedback_server.py .

EXPOSE 50055
CMD ["python", "ml_feedback_server.py"]
