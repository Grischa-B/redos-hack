#!/usr/bin/env bash

function help() {
    echo 'Run'
    echo './streamer.sh RunServer'
    echo 'on server side, to allow connections to streaming system'
    echo
    echo 'Run'
    echo './streamer.sh Enter'
    echo 'to start sharing your screen or connect to streaming'
}

if [[ $# != 1 ]]; then
    help
fi

case $1 in
    "RunServer" )
        python3 streamer/server.py -i 0.0.0.0 -p 8080
        ;;
    "Enter" )
        python3 client.py -i 84.252.140.32 -p 8080
        ;;
    "-h" | "--help" )
        help
        ;;
esac
