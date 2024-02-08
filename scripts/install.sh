#!/bin/bash
cd ~
if ! [ -d sistemas_distribuidos ]
then
    mkdir sistemas_distribuidos
fi
cd sistemas_distribuidos

if ! [ -d MyYoutube-Entrega5 ]
then
    git clone https://github.com/gustavomoura628/MyYoutube-Entrega5
    cd MyYoutube-Entrega5
else
    cd MyYoutube-Entrega5
    git pull
fi

pip install rpyc

previous_process=$(netstat -nlp | grep 8090 | awk '{print $7}' | perl -pe "s/\/.*//")
echo previous process = $previous_process
if [ -n "$previous_process" ]; then kill $previous_process; fi
echo Starting datanode.py
python3 datanode.py &
disown
