#!/bin/bash
cd ~/docker/dev/rss/rss_dashboard_login
git checkout extra-feeds
git pull origin extra-feeds
docker compose down
docker compose up -d --build
