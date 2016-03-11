import io
import os
import yaml

class Config(object):
    def __init__(self, config_file=''.join([os.path.abspath(os.path.dirname(__file__)), '/default.yml'])):
        self._data = dict()

        with io.open(config_file) as fh:
            self._data = yaml.load(fh)

    def __getitem__(self, key):
        return self._data[key]
