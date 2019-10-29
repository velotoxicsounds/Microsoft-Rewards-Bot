#!/usr/bin/env bash
cd /usr/local/msrwb/Microsoft-Rewards-Bot/
git pull
python3 /usr/local/msrwb/Microsoft-Rewards-Bot/ms_rewards.py --headless --mobile --pc --quiz
exit
