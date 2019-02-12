=============
Author Lookup
=============

This is the author lookup API used by DSpace for managing people authorties.

.. contents:: Table of Contents
.. section-numbering::

Developing
----------

Use ``pipenv`` to install and manage dependencies::

  $ git clone git@github.com:MITLibraries/dw_lookup.git
  $ cd dw_lookup
  $ pipenv install --dev

In order to connect to the Data Warehouse, you will need to install the `Oracle client library <https://www.oracle.com/technetwork/database/database-technologies/instant-client/overview/index.html>`_. It seems that just installing the basic light package should be fine. In general, all you should need to do is extract the package and add the extracted directory to your ``LD_LIBRARY_PATH`` environment variable. If there is no ``lbclntsh.so`` (``libclntsh.dylib`` for Mac) symlink in the extracted directory, you will need to create one. The process will look something like this (changing for paths/filenames as necessary)::

    $ unzip instantclient-basiclite-linux.x64-18.3.0.0.0dbru.zip -d /usr/local/opt

    # Add the following line to your .bash_profile or whatever to make it permanent
    $ export LD_LIBRARY_PATH=/usr/local/opt/instantclient_18_3:$LD_LIBRARY_PATH

    # If the symlink doesn't already exist:
    $ ln -rs /usr/local/opt/instantclient_18_3/libclntsh.so.18.1 \
        /usr/local/opt/instantclient_18_3/libclntsh.so

On Linux, you will also need to make sure you have libaio installed. You can probably just use your system's package manager to install this easily. The package may be called ``libaio1``.

Deploying
---------

.. IMPORTANT::
  The deploy process copies *everything* from project root into the Lambda deploy package. Your project root *must* be clean before deploying! In other words, ``git status`` should show no untracked files.

Dependencies
~~~~~~~~~~~~

The Lambda deploy package needs the Oracle client library and libaio added to it. The make commands for creating a deploy will do this for you. Copies of these two libraries are stored in an S3 bucket. If you need to update the version of either library make sure you are using a version compiled for Linux x86_64 architecture.

Configuration
~~~~~~~~~~~~~

The app needs a few environment variables to work. The Lambda deploy gets these from an AWS Secret so it only needs the ``AWS_SECRET_ID`` set to the ARN for a secret containing the following keys:

+------------------------+-----------------------------------+
| Key                    | Description                       |
+========================+===================================+
| ``AUTHOR_DB_HOST``     | Hostname of Data Warehouse server |
+------------------------+-----------------------------------+
| ``AUTHOR_DB_PORT``     | Port for db connection            |
+------------------------+-----------------------------------+
| ``AUTHOR_DB_SID``      | Oracle SID                        |
+------------------------+-----------------------------------+
| ``AUTHOR_DB_USER``     | DB username                       |
+------------------------+-----------------------------------+
| ``AUTHOR_DB_PASSWORD`` | DB password                       |
+------------------------+-----------------------------------+
| ``DW_LOOKUP_TOKEN``    | API key needed to authenticate    |
+------------------------+-----------------------------------+

Deploy
~~~~~~

This application is deployed as a serverless API Gateway app using `Zappa <https://github.com/Miserlou/Zappa>`_. In general, the process for deploying should be as simple as::

  $ make stage

to deploy a staging build and::

  $ make prod

to deploy a production build.

Zappa `has problems <https://github.com/Miserlou/Zappa/issues/795>`_ sometimes with certain deployments. Setting ``slim_handler`` to ``false`` in the Zappa config seems to prevent this issue from happening. Using this option, however, creates a deploy package that's ~65MB. This is technically over the 50MB limit for Lambda deploy packages, but in practice 65MB seems to be fine. It also wouldn't hurt to run ``make clean`` before deploying.

