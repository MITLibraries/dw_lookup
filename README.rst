=============
Author Lookup
=============

This is the author lookup API used by DSpace for managing people authorties.

Developing
----------

Because of the Oracle client library requirement, the recommended way to do local development is to use the provided docker-compose file. You must be connected to the VPN for this to work. You'll need to create a ``.env`` file in the project directory with the following environment variables (ask in the #engineering slack channel for the values)::

  AUTHOR_DB_USER
  AUTHOR_DB_PASSWORD
  AUTHOR_DB_HOST
  AUTHOR_DB_PORT
  AUTHOR_DB_SID

Additionally, if you are using Linux you will need to set ``AUTHOR_NETWORK_MODE=host``. The default password for the dev app is ``authortoken``. You can change this by setting ``DW_LOOKUP_TOKEN``.

You should use make to build the docker image as opposed to running ``docker build`` yourself::

  $ make dist
  $ docker-compose up

Dependencies are managed with ``pipenv``.

Deploying
---------

Deployment is handled through Terraform/Ansible. To deploy changes you will need to first create a Github release. Then, update the ``author_version`` variable in the python role of the Ansible config. See `the Terraform repo <https://github.com/MITLibraries/mitlib-terraform>`_ for more details.

Configuration
~~~~~~~~~~~~~

The app needs a few environment variables to work. In staging and production these are pulled from an AWS Secret so it only needs the ``AWS_SECRET_ID`` set to the ARN for a secret containing the following keys:

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
| ``SENTRY_DSN``         | Sentry DSN (production only)      |
+------------------------+-----------------------------------+
