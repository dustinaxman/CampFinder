# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file first and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

# Copy the rest of the application files into the container
COPY app.py /app/app.py
COPY camp_finder/ /app/camp_finder/

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application with Gunicorn
# 4 worker processes (-w 4) and bind to all IPs on port 5000 (-b 0.0.0.0:5000)
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]