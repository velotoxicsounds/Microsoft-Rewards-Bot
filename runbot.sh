#!/usr/bin/env bash
git pull
python3 redditScrape.py
python3 ms_rewards.py --headless --mobile --pc --quiz
exit
