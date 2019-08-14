#!/usr/bin/env bash

python_home=/home/deploy/.virtualenvs/hm_spider/
project_home=/home/deploy/code/hm_spider/

if [ -d $python_home ]
then
source $python_home'bin/activate'
else
echo 'python home not found'
exit 1
fi
if [ -d $project_home ]
then
uwsgi_config=$project_home'deploy/uwsgi.ini'
else
echo 'project home not found'
exit 1
fi

ps -ef| grep $uwsgi_config | awk '{print $2}' | xargs kill -9
uwsgi $uwsgi_config
