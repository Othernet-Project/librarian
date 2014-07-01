SRCDIR=/vagrant

cd $SRCDIR
nosetests -w tests "$@"
