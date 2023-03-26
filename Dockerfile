FROM python:3.8-slim-bullseye
# Create app directory
WORKDIR /

# Install app dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt
# Bundle app source
COPY . .
RUN mkdir -p /db
EXPOSE 5000:5000
CMD [ "python", "-m", "app"]