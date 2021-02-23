import os

from flask import Flask

import base64
from io import BytesIO

from matplotlib.figure import Figure

# basic
import numpy as np
import pandas as pd

# get data
import pandas_datareader as pdr

# visual
import mpl_finance as mpf
import seaborn as sns

#time
import datetime as datetime

#talib
import talib

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello world!'

@app.route("/test")
def test():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

@app.route("/tw/<int:twc>")
def analysis_stock(twc):
    year=2020
    month=1
    day=1
    
    start = datetime.datetime(year, month, day)
    df_2330 = pdr.DataReader('%d.TW' % twc, 'yahoo', start=start)
    df_2330.index = df_2330.index.format(formatter=lambda x: x.strftime('%Y-%m-%d')) 

    sma_10 = talib.SMA(np.array(df_2330['Close']), 10)
    sma_30 = talib.SMA(np.array(df_2330['Close']), 30)
    df_2330['k'], df_2330['d'] = talib.STOCH(df_2330['High'], df_2330['Low'], df_2330['Close'])
    df_2330['k'].fillna(value=0, inplace=True)
    df_2330['d'].fillna(value=0, inplace=True)

    fig = Figure(figsize=(24, 20))
    ax = fig.add_axes([0,0.3,1,0.4])
    ax2 = fig.add_axes([0,0.2,1,0.1])
    ax3 = fig.add_axes([0,0,1,0.2])

    ax.set_xticks(range(0, len(df_2330.index), 10))
    ax.set_xticklabels(df_2330.index[::10])
    mpf.candlestick2_ochl(ax, df_2330['Open'], df_2330['Close'], df_2330['High'],
                          df_2330['Low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
    ax.plot(sma_10, label='10d avg')
    ax.plot(sma_30, label='30d avg')

    ax2.plot(df_2330['k'], label='K value')
    ax2.plot(df_2330['d'], label='D value')
    ax2.set_xticks(range(0, len(df_2330.index), 10))
    ax2.set_xticklabels(df_2330.index[::10])

    mpf.volume_overlay(ax3, df_2330['Open'], df_2330['Close'], df_2330['Volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
    ax3.set_xticks(range(0, len(df_2330.index), 10))
    ax3.set_xticklabels(df_2330.index[::10])

    ax.legend()
    ax2.legend()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
