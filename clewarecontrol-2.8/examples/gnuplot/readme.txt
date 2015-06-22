run with
	-t
to get timestamps in the file
	-O brief
to get only values
	-f file.dat
to store the values in a file.

Then run:
	plot.sh file.dat file.png

E.g.:
	clewarecontrol -d 10239 -c 10 -t -O brief -f examples/gnuplot/file.dat -ra 0
	examples/gnuplot/plot.sh examples/gnuplot/file.dat test.png
