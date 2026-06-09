FROM python:3.13-slim

WORKDIR /app

# install uv
RUN pip install uv

# copy project
COPY . /app

# create isolated environment inside container
RUN uv venv /opt/venv

# activate it for all future steps
ENV PATH="/opt/venv/bin:$PATH"

# install dependencies into that venv
RUN uv pip install -e .

# run as module (clean import model)
CMD ["python", "-m", "cmd.inspectDataset"]