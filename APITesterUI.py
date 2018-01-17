from flask import Flask,render_template, request
from APItesterDB import DB
# from pandas import pd
import pandas as pd

app = Flask(__name__)
db = DB()


last_search = {
    'host': None
}

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/graph71')
def graph71():
    return render_template('graph71.html')


@app.route('/tableview`/', methods=['GET', 'POST'])
def tableview():
    df_html = ""
    df2_html = ""
    hostlist = db.dbhostlist()
    print('hostlist:', hostlist)

    if request.method == 'POST':
        last_search['host'] = request.form['host_option']
        rs = db.dbhosttimestamp(last_search['host'])
        if len(rs) > 0:
            df = pd.DataFrame(rs, columns=['datetime', 'api', 'avg_duration'])
            # print(df)

            pt = df.pivot_table(index='api', columns='datetime', values='avg_duration')
            print(pt)

            # df_html = pt.to_html()
            df_html = pt

        rs = db.dbhosttimestampthreads(last_search['host'])
        if len(rs) > 0:
            df = pd.DataFrame(rs, columns=['datetime', 'threads'])
            # print(df)

            pt = df.pivot_table(columns='datetime', values='threads')
            print(pt)

            # df2_html = pt.to_html()
            df2_html = pt


    return render_template('tableview.html', hostlist=hostlist, rs=df_html, rs2=df2_html, last_search=last_search)




if __name__ == '__main__':
    app.run(debug=True, port=5004)
