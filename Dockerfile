FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean

COPY . /app
WORKDIR /app

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         build-essential \
#         libxml2-dev \
#         libxslt-dev \
#         python3-dev \
#     && apt-get clean

RUN pip install .

CMD python -m mbrl.examples.main algorithm=mbpo overrides=mbpo_cartpole 