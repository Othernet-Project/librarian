SRCDIR=/opt/librarian

cd $SRCDIR
PYTHONPATH=$SRCDIR py.test tests librarian/utils/*.py --doctest-mod "$@" 
