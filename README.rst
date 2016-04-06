=========
librarian
=========

Librarian is a web server that allows users to view and download files stored
on Outernet receivers. In essence it is similar to a typical static web 
server's directory index with bells and whistles.

Generating documentation
========================

To generate the documentation, you need to have Python and `Sphinx
<www.sphinx-doc.org>`_ installed. Once you have the prerequisites run
``make``::

    $ make docs

The generated documentation will be found in ``docs/build/html``.

Running the test suite
======================

To run the tests first prepare the development environment according to the
documentation::

    $ make prepare

You will need to have `Tox <http://codespeak.net/tox/>`_ installed. Then run
the tests by simply executing the ``tox`` command::

    $ tox

Contributing interface translations
===================================

You can either translate using the .po files in the project directory, or use
the hosted version `on POEditor
<https://poeditor.com/join/project?hash=90911b6fc31f2d68c7debd999aa078c6>`_
(recommended). Note that Librarian is always under active development, so
strings *will* change from time to time, and sometimes the contributed
translations may be completely removed.

If you are contributing, or considering contributing translations, please swing
by our `forums <https://discuss.outernet.is/>`_ and say hello.

List of translation contributors
--------------------------------

Special thanks to all those who have contributed their valuable time and
knowledge:

- Kurei-Z
- Haveson Florvil Alphanet
- Susruthan Seran
- Ignas Sklerius
- Dani Álvarez
- Mogens From
- necklinux
- Stefan Ionita
- Lars Lillo Ulvestad
- Max Boone
- Eric Alexander
- Rafael Leda
- Daniel Antal
- Emanuelis Adomaitis
- Filippo
- zaid
- Manish Rastogi
- cavit
- Surit
- Chengtao Hua
- Josep Manel
- Saman rajaei
- patrik
- Aadarsh
- Kajcha
- André Daniel
- Andrey
- Ismail Al Ahmad
- Morten
- Morteza
- Max Sundström
- Viktoria
- David Marques
- Warodom Phaenthong
- Baris Sekerciler
- Tolga Evcimen
- Will Martin
- Manoel Junior
- Krabbs
- Vibhor Dubey
- Nelson Macchi
- M. Ammar
- Gustaf
- Hammad Tariq
- Romaric FAVE
- Peer Oliver Schmidt
- javad katooli
- dan
- Gerry Galactic
- Varshan BP
- Frédéric Uhrweiller
- Pengan Zhou
- Arthur
- Navina
- Nicky Kouffeld, Dutchwebs
- Sakara
- Bruno Nogueira
- Mohammad Reza Golaghaee
- Luis Fuentes
- Marco Rubio
- Rodrigo
- Kasparas
- Frederik
- zanghel
- Benoît Casanova
- Gonzalo
- Anirban Chatterjee
- Christian Novrup
- Janberk Genç
- Mario Lopez
- Dana Tierney
- Terrence
- Ahmed
- daming_99
- Steffie
- Francesca
- HM
- Julien
- Sebastian Borg
- Ronald Philipsen
- Rebeca Virgo
- Ciprian
- Gabriel
- Salutlolo
- Souhaïl BOUGRINE
- Baris Kilic
- Tori Arbaugh
- Hamza Siddiqui
- Thibaut
- Alireza Keshavarz
- Jannis A. K.
- Miguel Maldonado
- Daem0n
- tommaso
- Moe Ihab
- Massimiliano CARNEMOLLA
- Behzad
- Mehmet Mallı
- Buddha Burman
- Zipper
- Sai Chakradhar Araveti
- Klara Milena Hirscher
- Andrew
- soukayna
- Zakaria Bendali
- Siddharth Nair
- Bruno
- Francis
- Roman
- ix
- Christoph Nebendahl
- Алексей
- behzad
- Chase Burgess
- Slandgkearth
- DURAIRAJAA N

Reporting bugs and feature requests
===================================

Bugs and feature requests can be posted either in our `forums
<https://discuss.outernet.is/>`_ or in the GitHub
`issue tracker <https://github.com/Outernet-Project/librarian/issues>`_.

License
=======

Librarian and supporting code are released under GPLv3 or later. Please see
``COPYING`` file in the source tree.
