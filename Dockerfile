FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean

COPY requirements/main.txt .

RUN pip install -r main.txt

COPY . .
# COPY ./realflight_gym ./realflight_gym

# RUN git clone https://github.com/liamf555/realflight_gym.git

RUN pip install -e ./realflight_gym/gym-realflight

CMD ["python", "-m", "mbrl.examples.main", "algorithm=mbpo", "overrides=mbpo_realflight"] 