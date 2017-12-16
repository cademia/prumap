#!/usr/bin/env python

activate_this = "env/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

from app import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
