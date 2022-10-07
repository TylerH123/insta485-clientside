#!/bin/bash
set -Eeuo pipefail
set -x
# Log in
# http \
#   --session=./session.json \
#   --form POST \
#   "http://localhost:8000/accounts/" \
#   username=awdeorio \
#   password=password \
#   operation=login
# # REST API request
http \
  --session=./session.json \
  "http://localhost:8000/api/v1/posts/1/"

# http -a awdeorio:password \
#   POST \
#   "http://localhost:8000/api/v1/likes/?postid=3"

# http -a awdeorio:password "http://localhost:8000/api/v1/posts/?postid_lte=2"

# http "http://localhost:8000/api/v1/posts/?size=1"
# http -a awdeorio:password "http://localhost:8000/api/v1/posts/?page=1"
# http -a awdeorio:password "http://localhost:8000/api/v1/posts/?postid_lte=2&size=1&page=1"
# http -a awdeorio:password "http://localhost:8000/api/v1/posts/3/"
# http -a awdeorio:password \
#   DELETE \
#   "http://localhost:8000/api/v1/likes/6/"

# http -a awdeorio:password \
#   POST \
#   "http://localhost:8000/api/v1/comments/?postid=3" \
#   text='Comment sent from httpie'

# http -a awdeorio:password \
#   DELETE \
#   "http://localhost:8000/api/v1/comments/8/"