#!/bin/bash

ACTION=$1
COFFEE_PID=$2
COFFEE_SRC=$3
COFFEE_OUT=$4

case "$ACTION" in
    start)
        if [ -f "$COFFEE_PID" ]
        then
            exit 1
        else
            coffee --bare --watch --output "$COFFEE_OUT" "$COFFEE_SRC" &
            echo -n "$!" > $COFFEE_PID
        fi
        ;;
    stop)
        if [ -f "$COFFEE_PID" ]
        then
            kill -s TERM $(cat "$COFFEE_PID")
            rm "$COFFEE_PID"
        else
            exit 1
        fi
        ;;
esac
