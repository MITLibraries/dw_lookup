import site
from os.path import dirname
site.addsitedir(dirname(__file__) +'/env/lib/python2.6/site-packages')

from manage import app as application

import sys
sys.stdout = sys.stderr
