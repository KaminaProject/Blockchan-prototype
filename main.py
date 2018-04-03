import htmlPy
import os
from back_end import BackEnd
import json


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = htmlPy.AppGUI(title=u"Blockchan")
app.maximized = True
app.static_path = os.path.join(BASE_DIR, "static/")
app.template_path = "."
app.bind(BackEnd(app))
app.developer_mode = True


app.template = ("index.html", {'mode':'posts'})

app.start()
