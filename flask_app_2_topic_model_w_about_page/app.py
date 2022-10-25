# flask related modules
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

# DS related modules
import os
import pandas as pd

app = Flask(__name__)

# Pre-computation for tm_lda page!
min_dfs = [0,0.05,0.1]
max_dfs = [0.7,0.8,0.9]
n_comps = [5,6,7,8,9,15]
params = []
for min_ in min_dfs:
    for max_ in max_dfs:
        for n_comp in n_comps:
            params.append([min_,max_,n_comp])
idx_seeker = pd.DataFrame(params, columns=['min','max','comps'])
idx_seeker.reset_index(inplace=True)

lda_renders = os.listdir('templates/renders/')
lda_renders.sort()
@app.route('/tm_lda', methods=["POST","GET"])
def tm_lda():
    '''Topic Model LDA'''
    try:
        min_val = float(request.form.get("chosen_min"))
        max_val = float(request.form.get("chosen_max"))
        n_comp_val = float(request.form.get("chosen_ncomps"))
    except:
        min_val, max_val, n_comp_val = min_dfs[0], max_dfs[0], n_comps[0]

    current_output = f'Min={min_val}, Max={max_val}, Comps={n_comp_val}'

    min_bool = (idx_seeker['min'] == min_val)
    max_bool = (idx_seeker['max'] == max_val)
    n_comp_val = (idx_seeker['comps'] == n_comp_val)
    index = idx_seeker.loc[min_bool & max_bool & n_comp_val,'index']
    render = 'renders/' + lda_renders[int(index.item())]

    return render_template('tm_lda.html',index=int(index.item()),current_output=current_output,render=render, min_dfs=min_dfs,max_dfs=max_dfs,n_comps=n_comps)

@app.route('/home', methods=['POST', 'GET'])
def index():
    """Return the homepage."""
    return render_template("home.html")


@app.route('/about')
def about():
    """Return the about page."""
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
