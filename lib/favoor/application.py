# coding=utf-8
# web application


import os
from web import Favoor

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# wsgi app
wsgi_app = Favoor(root_path)

# register views
from handler import view
wsgi_app.register_view(view)


# local service
wsgi_app.run()
