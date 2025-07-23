#
# I need this intermediate script because dot requires two arguments and
# the bash "#!" trick can only pass one.
#
/usr/bin/dot -O -Tpng $1
eog $1.png
