#!/bin/bash

ACTION=$1
COMPASS_PID=$2
COMPASS_CONF=$3

case "$ACTION" in
    start)
        if [ -f "$COMPASS_PID" ]
        then
            exit 1
        else
            compass watch -c "$COMPASS_CONF" &
            echo -n "$!" > $COMPASS_PID
        fi
        ;;
    stop)
        if [ -f "$COMPASS_PID" ]
        then
            kill -s INT $(cat "$COMPASS_PID")
            rm "$COMPASS_PID"
        else
            exit 1
        fi
        ;;
esac
