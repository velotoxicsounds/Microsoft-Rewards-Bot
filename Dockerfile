FROM python:3.7

RUN mkdir -p /rewards_bot/config
RUN mkdir -p /rewards_bot/logs

COPY . /rewards_bot
WORKDIR /rewards_bot
RUN pip install --no-cache-dir -r requirements.txt

# Run the command on container startup
CMD python3 /rewards_bot/ms_rewards.py --headless --all
