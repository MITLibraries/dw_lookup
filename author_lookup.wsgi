import site
site.addsitedir('/var/www/libraries-dev.mit.edu/author_lookup/env/lib/python2.6/site-packages')

from manage import app as application

import sys
sys.stdout = sys.stderr
