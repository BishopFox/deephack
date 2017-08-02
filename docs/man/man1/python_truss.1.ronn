DeepHack
====

## SYNOPSIS

`make virtualenv-develop`

`~/.virtualenvs/vulnserver/bin/vulnserver`

`curl 127.0.0.1:5000/v0/sqli/select?user_id=1`

## Dependencies

sudo apt install virtualenv libpq-dev
sudo pip3 install keras tensorflow

## DESCRIPTION

DeepHack

## COMMAND LINE OPTIONS

* `--example` <action>:
    This is an example action, replace it with a real argument!

## EXAMPLES

    Setup a python virtualenv to do development work

        $ make virtualenv-develop

    Create an LXC and install the module into it for development

        $ make lxc-develop

    Create an LXC and install the project into it for production

        $ make lxc
