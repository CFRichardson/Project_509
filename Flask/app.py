import numpy as np
import os
import pandas as pd

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# !!!!! may be not needed for strings will be piped into Python Function
# from sqlalchemy import create_engine
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session

app = Flask(__name__)


@app.route('/home', methods=['POST', 'GET'])
def index():
    """Return the homepage."""
    return render_template("base.html")

if __name__ == "__main__":
    app.run(debug=True)
