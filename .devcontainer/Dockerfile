FROM mcr.microsoft.com/vscode/devcontainers/python:3.10-bullseye

# Add env variables
ENV PATH="${PATH}:/root/.poetry/bin"
ENV SHELL /bin/bash

# Update the base image, upgrade pip, & install poetry. 
RUN sudo apt-get update && pip3 install --upgrade pip \
    && pip3 install poetry \
    && poetry config virtualenvs.create false


# Expose Port 5000, which is used by Quart. 
EXPOSE 5000
