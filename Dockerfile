FROM franky1/tesseract

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN chmod +x /app/install_debian.sh
RUN /app/install_debian.sh

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt


# Run the web service on container startup. Here we use the gunicorn
# webserver, with 4 worker processes and 32 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 4 --threads 32 --timeout 0 app:app