SRCDIR=/vagrant

cd $SRCDIR
PYTHONPATH=$SRCDIR py.test tests "$@"
