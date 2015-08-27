# author-lookup
REST API to look up basic information on MIT authors

Deploy:

- clone to directory desired (ex /var/www/libraries-dev.mit.edu/, full path will be /var/www/libraries-dev.mit.edu/author_lookup_api/)

- copy static files to static dir (ex /var/www/libraries-dev.mit.edu/static/)

- update conf file. Ex:
    to file /etc/httpd/conf.d/ssl.conf add:
    
    Alias /static/ "/var/www/libraries-dev.mit.edu/static/"

    and 

    WSGIDaemonProcess author_lookup_api user=szendeh group=szendeh threads=5 python-path=/var/www/libraries-dev.mit.edu/author_lookup_api/
    WSGIScriptAlias /author_lookup_api "/var/www/libraries-dev.mit.edu/author_lookup_api/author_lookup.wsgi"
    <Directory "/var/www/libraries-dev.mit.edu/author_lookup_api">
       WSGIProcessGroup author_lookup_api
       WSGIApplicationGroup %{GLOBAL}
       Order deny,allow
       Allow from all
    </Directory>

    (the paths could change depending on where you cloned into)


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