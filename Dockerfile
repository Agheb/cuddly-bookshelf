FROM tiangolo/uwsgi-nginx:python2.7

MAINTAINER Amanuel Ghebreweldi

RUN pip install --upgrade pip
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --requirement requirements.txt

# Add app configuration to Nginx
COPY nginx.conf /etc/nginx/conf.d/

# Copy sample app
COPY ./app /app