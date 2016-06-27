# author-lookup
REST API to look up basic information on MIT authors

Deploy:

- clone to directory desired (ex /var/www/libraries-dev.mit.edu/htdocs/secure/, full path will be /var/www/libraries-dev.mit.edu/htdocs/secure/dw_lookup/)

- oracle or oracle instantclient needs to be installed and set up correctly. This can be a trial.

NOTES ON ORACLE:

This is a useful link:
https://blogs.oracle.com/opal/entry/configuring_python_cx_oracle_and

if Oracle is not installed, you can:
  - go here: http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html
  - select your deployed env (OSX, Linux, 32/64 bit etc)
  - download *both* the basic package *and* the optional SDK package
  - tar -xzf both and copy the contents into a place you will remember. For this example, it's at /usr/lib/oracle/12.1/

once Oracle is installed, you must make sure your env is pointing at it properly. eg something like:
```
export ORACLE_HOME=/Users/szendeh/work/oracle/11_2
export DYLD_LIBRARY_PATH=$ORACLE_HOME
export LD_LIBRARY_PATH=$ORACLE_HOME
```

you should have the following symlinks in the oracle directory (FOR MAC):

```
ln -s libclntsh.dylib.11.1 libclntsh.dylib
ln -s libocci.dylib.11.1 libocci.dylib
```

- create virtual env (I do it right in the cloned directory), activate it, and pip install requirements.txt

- name/pw for oracle db must be set in env eg export ORACLE_USER=xyz, script will pick those up from env

- update conf file. Ex:
    to file /etc/httpd/conf.d/ssl.conf add:

```
WSGIDaemonProcess dw_lookup user=szendeh group=szendeh processes=5 threads=1 python-path=/var/www/libraries.mit.edu/htdocs/_api/dw_lookup/
WSGIScriptAlias /api/dw_lookup "/var/www/libraries.mit.edu/htdocs/_api/dw_lookup/dw_lookup.wsgi"

<Directory "/var/www/libraries.mit.edu/htdocs/_api/dw_lookup">
    SetEnv ORACLE_HOME=/usr/lib/oracle/12.1/client64
    WSGIProcessGroup dw_lookup
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from 18.
</Directory>
```
    (the paths could change depending on where you cloned into)

- update evn apache runs with using file /etc/sysconfig/httpd Add:
```
export ORACLE_USER=[fill in username]
export ORACLE_PASSWORD=[fill in password]
```

(script looks for these variables in the env when it runs)


- restart httpd server eg sudo service httpd restart


Testing:

- install tox

- run 

```
$ tox tests
```