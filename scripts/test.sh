#!/bin/bash

echo Hello!

c=$(( RANDOM % 2 ))
if [ "$c" -eq "0" ];
then
    echo Is 3=5?
else
    echo Is 2+2=4?
fi

read response

echo Your response = $response
