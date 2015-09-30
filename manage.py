#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from author_lookup.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
else:
   app.debug = True
