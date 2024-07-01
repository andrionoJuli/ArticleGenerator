FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

RUN apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip

# Set the working directory in the container
WORKDIR /app

COPY . /app

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 3000

# Run app.py when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3030"]