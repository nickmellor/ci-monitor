#! /bin/sh

gnuplot << EOF > $2
set term png
set autoscale
set timefmt "%s"
set xdata time
plot "$1" using 1:2 axes x1y1 with lines title 'values'
EOF
