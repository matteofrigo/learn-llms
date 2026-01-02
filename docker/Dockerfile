FROM python:3.12.12-slim

WORKDIR /home/learn-llms

# create python virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# install required python packages in the virtual environment
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel
RUN /opt/venv/bin/pip install numpy pandas matplotlib mistralai pydantic jsonformatter
# RUN python3 -m pip install --upgrade pip setuptools wheel
# RUN python3 -m pip install numpy pandas matplotlib mistralai pydantic jsonformatter