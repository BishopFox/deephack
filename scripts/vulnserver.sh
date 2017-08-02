#!/usr/bin/env bash
. ~/.virtualenvs/vulnserver/bin/activate
uwsgi --reuse-port --http 127.0.0.1:5000 --wsgi-file vulnserver/lib/vroutes.py --callable app --processes 2 --logto /tmp/vulnserver.log
