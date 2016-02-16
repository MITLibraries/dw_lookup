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

- fill in oracle name/pw for author_lookup/config/default.yml

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

- restart httpd server eg sudo apachectl restart


Usage:

https://libraries-dev.mit.edu/author_lookup_api/author/?name_string=[2 or more chars]

# for comma delimited strings (ex 'smith, joh')
# the first string is the complete last name (no wildcard)
# the rest is assumed to be beginning of first name (wildcard end)

# for multiple strings broken by spaces (ex 'john smith')
# the last string is assumed to be the last name (wildcard end)
# the rest is assumed to be the first name (wildcard end)

# for very short strings w/o commas or spaces (ex 'su')
# assume it's a complete first or last name (no wildcard, but check complete string against first -or- last name fields)

# all other cases (ex willi)
# assume name partial (wildcard beginning and end)


Testing:

- install tox

- run 

```
$ tox tests
```