import htmlPy
import os
import blockchan_utils
from back_end import BackEnd
import json
     

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = htmlPy.AppGUI(title=u"Sample application")
app.maximized = True
app.static_path = os.path.join(BASE_DIR, "static/")
app.template_path = "."
app.bind(BackEnd(app))


app.template = ("index.html", {})


app.start()
