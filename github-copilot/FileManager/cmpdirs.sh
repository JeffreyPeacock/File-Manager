#!/bin/sh
for d in /home/public/Photography/Gallery/2020/2020/2020*
do
    echo "===== $d"
    bname=`basename $d`;
    if [ ! -d "/home/public/Photography/Gallery/2020/${bname}" ]
    then
        echo "===== SKIPPING: /home/public/Photography/Gallery/2020/${bname}"
        continue;
    fi
    python src/main.py compare-directories \
        --dirA /home/public/Photography/Gallery/2020/${bname} \
        --dirB $d
done
