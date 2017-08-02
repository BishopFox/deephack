#!/usr/bin/env bash

PROGRAM_NAME="python_truss"
DEV_DEPS="python-virtualenv python3 python3-dev postgresql-server-dev-all"
SYSTEM_DEPS="postgresql python-psychopg2 postgresql-server-dev-all"
ALL_DEPS=$(echo $DEV_DEPS $SYSTEM_DEPS | tr ' ' ',' | tr '\n' ',')

# get current directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# strip current dir to get to the root of the project directory
SRC_DIR=${SCRIPTS_DIR%$(basename $SCRIPTS_DIR)}

CONTAINER_NAME='deephack.lxc'

lxc_config="/var/lib/lxc/$CONTAINER_NAME/config"
lxc_rootfs="/var/lib/lxc/$CONTAINER_NAME/rootfs/"

Lxc_create() {
    name=$1
    if [[ -z $name ]]; then
    cat <<EOF
Lxc_create container_name
default is to use ubuntu template
EOF
    else
        container_template=ubuntu
        auth_keys=".ssh/authorized_keys"
        sudo -E lxc-create -t $container_template -n $name -- -u $USER -S $HOME/$auth_keys --packages ${ALL_DEPS%?}
        sudo -E lxc-start -d -n $name
    fi
}

install_deps() {
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        if [[ $(cat /etc/os-release  | grep ID_LIKE | tr '=' ' ' | awk '{ print $2 }') == "debian" ]]; then
            if [[ ! -f '/var/lib/apt/periodic/update-success-stamp' || \
                "$[$(date +%s) - $(stat -c %Z /var/lib/apt/periodic/update-success-stamp)]" -ge 600000 ]]; then

                sudo apt-get update
            fi
            sudo apt-get install -y lxc liblxc1 python3-lxc
        else
            echo 'install_deps not implemented on this distro'
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo 'sorry lxc does not work on OSX, use a vagrant VM'
        exit 1
    fi
}

bootstrap() {
    Lxc_create $CONTAINER_NAME

    repo_mount="lxc.mount.entry = $SRC_DIR home/$USER/$PROGRAM_NAME none bind,create=dir 0 0"
    if ! sudo grep -q "$repo_mount" "$lxc_config"; then
        echo "$repo_mount" | sudo tee -a $lxc_config
    fi
    sudo lxc-stop -n "$CONTAINER_NAME"
    sudo lxc-start -d -n "$CONTAINER_NAME"
    #TODO
    # install postgres
    # create database users
    # ensure listening on 0.0.0.0
    # pg_hba.conf to allow access
}

usage() {
    msgs=(
        'build.sh option [arg]'
        '-b | --bootstrap - create minimal dev lxc container'
    )

    for msg in "${msgs[@]}"; do
        echo $msg
    done

    exit 1
}

main() {
    options=$@
    args=($options)
    i=0

    for arg in $options; do
        i=$(( $i + 1 ))

        case $arg in
            -b|--bootstrap|bootstrap)
                bootstrap
                break
                ;;
            -d|--depends|depends)
                install_deps
                break
                ;;
            *)
                usage
                break
                ;;
        esac
    done
}

main $@
