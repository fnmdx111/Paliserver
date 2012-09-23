Paliserver
==========

Pa(per)li(st)server = Paliserver

How to deploy
-------------

1. Make sure you have Python 2.7 and pip installed and PATH configured,
   if you don't, see this [article](http://www.pip-installer.org/en/latest/installing.html), and then
   install all the dependencies listed in section Dependencies by using `pip install dependency`

2. Download the source as zip file and extract it into the desired location,
   or if you have git installed you can `git clone https://github.com/mad4alcohol/Paliserver.git`

3. `cd` into the directory in which you have put the source, run `python db_init_bootstrap.py`
   to initialize a database with user `admin` and user `test_user` created,
   both with the password `123456`

4. Run `python server.py`

5. Visit `your.i.p.address:5000` and see if `Hello world.` is displayed

Dependencies
------------

* flask

* flask-sqlalchemy

* flask-bootstrap

* flask-wtf

* flask-uploads

* tornado

Log
---

*   2012/9/23T2109 - 0.0.c

    this project now can easily be deployed

*   2012/9/23T1403 - 0.0.b

    paper dispatching detail is now available in `view_papers`

*   2012/9/22T1713 - 0.0.a (almost done, few tweaks remaining)

    merged `paliserver-admin` and `paliserver-reusable-modal` into `master` branch

*   2012/9/22T1709 - under dev

    refactored forward modal into a reusable one

*   2012/9/22T1526 - under dev

    introduced admin view

*   2012/9/22T0054 - under dev

    introduced paper list viewing

*   2012/9/20T0252 - under dev

    introduced download

*   2012/9/20T0215 - under dev

    introduced basic and working upload, no progressbar is intended because i think LAN is fast enough,
    to transfer files smaller than 50M

*   2012/9/17T0203 - under dev

    introduced forward-to, `.btn-group` integration, redispatch and so on

*   2012/9/15T1622 - under dev

    introduces paper-list, read buttons and dispatch-withdrawal

*   2012/9/14T0110 - under dev

    imported flask-wtf

*   2012/9/13T1008 - under dev

    imported flask-bootstrap

*   2012/9/12T0045 - under dev

    first push


TODO
----

There is no TODOs currently.


licensed under lgpl

author: <mailto:chsc4698@gmail.com>
