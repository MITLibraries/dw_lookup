# author-lookup
REST API to look up basic information on MIT authors

Deploy:

- clone to directory desired (ex /var/www/libraries-dev.mit.edu/, full path will be /var/www/libraries-dev.mit.edu/author_lookup_api/)

- oracle or oracle instantclient needs to be installed and set up correctly. This can be a trial.

NOTES ON ORACLE:

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

you should have the following symlinks in the oracle directory:

```
ln -s libclntsh.dylib.11.1 libclntsh.dylib
ln -s libocci.dylib.11.1 libocci.dylib
```

- create virtual env (I do it right in the cloned directory), activate it, and pip install requirements.txt

- name/pw for oracle db must be set in env eg export ORACLE_USER=xyz, script will pick those up from env

- update conf file. Ex:
    to file /etc/httpd/conf.d/ssl.conf add:

```
WSGIDaemonProcess author_lookup_api user=szendeh group=szendeh threads=5 python-path=/var/www/libraries-dev.mit.edu/author_lookup_api/
WSGIScriptAlias /author_lookup_api "/var/www/libraries-dev.mit.edu/author_lookup_api/author_lookup.wsgi"
<Directory "/var/www/libraries-dev.mit.edu/author_lookup_api">
   WSGIProcessGroup author_lookup_api
   WSGIApplicationGroup %{GLOBAL}
   Order deny,allow
   Allow from all
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