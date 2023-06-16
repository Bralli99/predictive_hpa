# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim-buster

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Copy the service account key file into the container
COPY hpa-masterthesis-190aae237e0d.json /app/hpa-masterthesis-190aae237e0d.json

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/hpa-masterthesis-190aae237e0d.json

# Install production dependencies.
RUN pip install -r requirements.txt

CMD [ "python", "./emitter.py"]