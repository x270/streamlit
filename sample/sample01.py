import streamlit as st
import pandas as pd
from streamlit.proto.MultiSelect_pb2 import MultiSelect
import yfinance as yf
import altair as alt

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T # 行列入れ替え
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.title('米国株チェック')
    st.sidebar.write("""
    # 表示オプション
    ## 表示日数
    """)
    days = st.sidebar.slider('日数',1,1000,365)

    st.write(f"""
    ### 過去{days}日間の株価変動
    """)

    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    condition = st.sidebar.slider('表示範囲',0,2000,500)

    tickers = {
        'QQQ' : 'QQQ',
        'VGT' : 'VGT',
        'VEEV': 'VEEV',
        'SBLK': 'SBLK',
        'MRNA': 'MRNA' ,
        'PLUG': 'PLUG' ,
        'UPWK': 'UPWK' ,
        'QS'  : 'QS'
    }

    data = get_data(days,tickers)

    companys = st.multiselect(
        '銘柄を選択',
        list(data.index),
        list(data.index)
    )

    if not companys:
        st.error('1つ以上選択してください。')
    else:
        data = data.loc[companys]
        st.write("### 株価チャート")
        data = data.T.reset_index() # Indexを日付でなく0,1,2,にする
        data = pd.melt(data, id_vars=['Date']) # 日付を基準に表を組み替える
        data = data.rename(columns={'value':'Stock Prices(USD)'}) # 項目名の変更

        minX = 0
        maxX = condition

        chart= (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x='Date:T',
                y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[minX,maxX])),
                color=('Name:N')
            )
        )

        st.write(chart)
        # st.write(data)
except:
    st.error("予期せぬエラーが発生しました。")
