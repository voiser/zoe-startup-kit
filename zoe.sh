#!/bin/bash

export ZOE_HOME=$(pwd)
export ZOE_LOGS=${ZOE_HOME}/logs
export ZOE_VAR=${ZOE_HOME}/var
export ZOE_DOMAIN=private
export PYTHONPATH=${ZOE_HOME}/lib/python-dependencies:${ZOE_HOME}/lib/python:${PYTHONPATH}
export PYTHONUNBUFFERED=1
export PERL5LIB=${ZOE_HOME}/lib/perl:${PERL5LIB}

#
# Starts the server
# Returns its PID
#
function launch_server() {
    cd ${ZOE_HOME}/server
    java -jar gul-zoe-server-assembly-1.0.jar \
      -p ${ZOE_SERVER_PORT} \
      -d ${ZOE_DOMAIN} \
      -g ${ZOE_DOMAIN} \
      -c ${ZOE_HOME}/etc/zoe.conf > ${ZOE_LOGS}/server.log 2>&1 &
    echo $!
}

#
# Starts an agent
#   launch_agent [name]
# Writes the PID into 'var/agent.pid' file
#
function launch_agent() {
    name="$1"

    pushd ${ZOE_HOME}/agents/$name > /dev/null 2>&1
    for script in *
    do
        if [[ -f "$script" ]] && [[ -x "$script" ]]
        then
            echo "Launching agent $name ($script)..."
            ./${script} > ${ZOE_LOGS}/$name.log 2>&1 &
            sleep 1
        fi
    done
    popd > /dev/null 2>&1

    echo "$!" > ${ZOE_VAR}/$name.pid 
}

#
# Restarts an agent
# restart_agent [name]
#
function restart_agent() {
    name="$1"

    stop_agent $name
    launch_agent $name
}

#
# Starts the server
#
function server() {
    echo "Starting server..."
    launch_server > ${ZOE_VAR}/server.pid
    sleep 5
}

#
# Starts your beautiful Zoe agents
#
function start() {
    echo "Starting agents..."
    pushd ${ZOE_HOME}/agents > /dev/null 2>&1
    for f in *
    do
        if [[ -d "$f" ]]
        then
            popd >/dev/null 2>&1
            launch_agent $f
            pushd ${ZOE_HOME}/agents > /dev/null 2>&1
        fi
    done
    popd >/dev/null 2>&1
}

#
# Stops your ZOE instance
#
function stop() {
    for f in ${ZOE_VAR}/*.pid
    do
        if [[ -f "$f" ]]
        then
            pid=$(cat $f)
            echo "Stopping process $pid ($f)"
            kill "$pid"
            rm "$f"
        fi
    done
}

#
# Stops a single Zoe agent
# stop_agent [name]
#
function stop_agent() {
    name="$1"
    f="${ZOE_VAR}/$name.pid"

    if  [[ -f "$f" ]]
    then
        pid=$(cat $f)
        echo "Stopping process $pid ($f)"
        kill "$pid"
        rm "$f"
    fi
}

#
# Shows the zoe running processes
#
function status() {
  for f in ${ZOE_VAR}/*.pid
  do
      if [[ -f "$f" ]]
      then
          name=$(basename $f)
          name=${name%%.pid}
          pid=$(cat $f)
          found=$(ps -p $pid)
          r=$?
          if [[ "$r" == "0" ]]
          then
            echo "ALIVE $name (pid $pid)"
          else
            echo "DEAD! $name"
          fi
      fi
  done
}

#
# Magic starts here
#   ./zoe.sh [start | stop]
#
case "$1" in
  "server" )
    server
    ;;
  "start" ) 
    server
    start
    ;;
  "stop" ) 
    stop
    ;;
  "status" )
    status
    ;;
  "restart" ) 
    stop
    start
    ;;
  "launch-agent" )
    launch_agent "$2"
    ;;
  "stop-agent" )
    stop_agent "$2"
    ;;
  "restart-agent" )
    restart_agent "$2"
    ;;
  * )
    echo "usage: ./zoe.sh server|start|stop|status|restart|launch-agent <name>|stop-agent <name>|restart-agent <name>"
    ;;
esac
