SRCDIR=/vagrant
LIBDIR=$SRCDIR/librarian

cd $LIBDIR

# Application should start with root privileges and bind to port 80
sudo PYTHONPATH=$SRCDIR python app.py "$@"
