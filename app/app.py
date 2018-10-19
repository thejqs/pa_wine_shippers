from flask import Flask
from flask import render_template, Markup
import ast
from collections import Counter
import json
import os
import pandas as pd

app = Flask(__name__)


@app.route('/')
@app.route('/index/')
def index():
    intro, chart_intro_1, chart_intro_2 = get_intro_text()
    chart_text = get_chart_text()
    footer_text = get_footer_text()
    j = get_all_shippers()
    pj = pd.read_json(json.dumps(j))
    top_states = Counter(pj.state_long).most_common(7)
    top_counties = Counter(pj.county + ', ' + pj.state_long).most_common(14)
    top_addresses = Counter(pj.api_address).most_common(10)
    top_phones = Counter([a for a in pj.phone if a != '']).most_common(12)
    return render_template(
        'index.html',
        json=j,
        intro=intro,
        chart_intro_1=chart_intro_1,
        chart_intro_2=chart_intro_2,
        chart_text=chart_text,
        footer_text=footer_text,
        top_states=top_states,
        top_counties=top_counties,
        top_addresses=top_addresses,
        top_phones=top_phones
    )


def get_intro_text():
    route = 'app/templates/intro_text.py'
    with open(os.path.join(os.getcwd(), route)) as f:
        jt = json.load(f)
        intro = Markup(jt['intro'])
        chart_intro_1 = Markup(jt['chart_intro_1'])
        chart_intro_2 = Markup(jt ['chart_intro_2'])
        return intro, chart_intro_1, chart_intro_2


def get_chart_text():
    route = 'app/templates/chart_text.py'
    with open(os.path.join(os.getcwd(), route)) as f:
        s = f.read()
        return ast.literal_eval(s)


def get_footer_text():
    route = 'app/templates/footer_text.py'
    with open(os.path.join(os.getcwd(), route)) as f:
        jf = json.load(f)
        footer = Markup(jf['author'])
        return footer


def get_all_shippers():
    route = 'data/'
    # data files are all dated, so when sorted
    # will be chronological
    newest_file = sorted(os.listdir(os.path.join(os.getcwd(), route)))[-1]
    with open(f'{os.path.join(os.getcwd(), route)}{newest_file}') as f:
        j = json.load(f)
        data = (j[key] for key in j)
        # print(data)
        return sorted(list(data), key=lambda k: k['name'])


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port=5000)
