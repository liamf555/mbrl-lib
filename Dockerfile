FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

COPY requirements/main.txt .

RUN pip install -r main.txt

COPY . .

CMD ["python", "-m", "mbrl.examples.main", "algorithm=mbpo", "overrides=mbpo_cartpole"] 