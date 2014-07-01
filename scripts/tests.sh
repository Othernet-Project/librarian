SRCDIR=/vagrant

cd $SRCDIR
nosetests tests/*.py "$@"
