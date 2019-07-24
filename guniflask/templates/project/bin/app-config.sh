#!/usr/bin/env bash

bin=$(dirname ${BASH_SOURCE[0]})
bin=$(cd "$bin"; pwd)

export GUNIFLASK_HOME=${GUNIFLASK_HOME:-$(cd "$bin"/../; pwd)}
export GUNIFLASK_CONF_DIR=${GUNIFLASK_CONF_DIR:-"$GUNIFLASK_HOME"/conf}

if [ -f "$GUNIFLASK_CONF_DIR"/app-env.sh ]; then
    . "$GUNIFLASK_CONF_DIR"/app-env.sh
fi

if [ -n "$GUNIFLASK_VIRTUAL_ENV" ]; then
    . "$GUNIFLASK_VIRTUAL_ENV"/bin/activate
fi

export GUNIFLASK_LOG_DIR=${GUNIFLASK_LOG_DIR:-"$GUNIFLASK_HOME"/.log}
export GUNIFLASK_PID_DIR=${GUNIFLASK_PID_DIR:-"$GUNIFLASK_HOME"/.pid}
export GUNIFLASK_ID_STRING=${GUNIFLASK_ID_STRING:-$USER}
