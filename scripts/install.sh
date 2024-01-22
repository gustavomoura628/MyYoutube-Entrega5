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

echo Starting datanode.py
python3 datanode.py
