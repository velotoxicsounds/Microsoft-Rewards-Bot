FROM python:3.7

RUN mkdir -p /rewards_bot/logs

RUN apt-get update
RUN apt-get install -y cron wget apt-transport-https

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - 
RUN sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get install -y google-chrome-stable

COPY . /rewards_bot
WORKDIR /rewards_bot
RUN pip install --no-cache-dir -r requirements.txt

# Run the command on container startup
CMD python3 /rewards_bot/ms_rewards.py --headless --all
