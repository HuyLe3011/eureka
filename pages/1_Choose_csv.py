#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import tensorflow as tf
import base64

# Đặt seed cố định cho Python, NumPy, và TensorFlow
seed_value = 20  # Bạn có thể thay đổi seed theo ý muốn

os.environ['PYTHONHASHSEED'] = str(seed_value)
random.seed(seed_value)
np.random.seed(seed_value)
tf.random.set_seed(seed_value)

import warnings
warnings.filterwarnings('ignore')

import backtrader as bt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
import tensorflow as tf
import tensorflow.keras.backend as K
import streamlit as st

from tensorflow.keras.layers import LSTM, Flatten, Dense, Masking
from tensorflow.keras.models import Sequential
from scikeras.wrappers import KerasRegressor
from vnstock import *
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import backtrader as bt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Ứng dụng LSTM cho danh mục đầu tư",page_icon="📊")
custom_css = """
<style>
    html, body, [class*="css"] {
        font-size: 20px;
    }
    .stButton > button {
        font-weight: bold !important;
        font-size: 20px !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 5px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #000000 !important;
        color: white !important;
    }
    }
</style>
"""

# Áp dụng CSS tùy chỉnh
st.markdown(custom_css, unsafe_allow_html=True)

class Basic_MACrossStrategy(bt.Strategy):
    params = dict(ma_short_period=20, ma_long_period=50)

    def __init__(self):
        # Define the short-term (20-period) moving average
        self.ma_short = bt.indicators.MovingAverageSimple(self.data.close, period=self.p.ma_short_period, 
                                                          plotname='MA 20')

        # Define the long-term (50-period) moving average
        self.ma_long = bt.indicators.MovingAverageSimple(self.data.close, period=self.p.ma_long_period, 
                                                         plotname='MA 50')

        # Define the crossover signal (1 for upward cross, -1 for downward cross)
        self.crossover = bt.indicators.CrossOver(self.ma_short, self.ma_long)

    def next(self):
        # Buy when the short MA crosses above the long MA
        if self.crossover > 0 and not self.position:
            self.buy(size=None)
            print(f'BUY CREATE, {self.data.datetime.date(0)}, Price: {self.data.close[0]:.2f}')

        # Sell when the short MA crosses below the long MA
        elif self.crossover < 0 and self.position:
            self.sell(size=None)
            print(f'SELL CREATE, {self.data.datetime.date(0)}, Price: {self.data.close[0]:.2f}')


class MACrossStrategy(bt.Strategy):
    params = dict(ma_short_period=20, ma_long_period=50)

    def __init__(self):
        self.ma_short = bt.indicators.MovingAverageSimple(self.data.close, period=self.p.ma_short_period,
                                                                plotname='MA 20')
        self.ma_long = bt.indicators.MovingAverageSimple(self.data.close, period=self.p.ma_long_period,
                                                                plotname='MA 50')
        self.crossover = bt.indicators.CrossOver(self.ma_short, self.ma_long)
        self.last_order = None
        self.buy_price = None
        self.holding = False  # Trạng thái có nắm giữ cổ phiếu không
        self.current_quarter = None
        self.quarterly_returns = {}  # Lưu return theo từng quý

    def next(self):
        current_month = self.data.datetime.date(0).month
        current_year = self.data.datetime.date(0).year
        # SAAIIAIAIAIAIAIIAIA ###
        current_quarter = (current_year, (current_month - 1) // 3 + 1)  # Chia tháng theo quý

        if current_quarter not in self.quarterly_returns:
            self.quarterly_returns[current_quarter] = 0

                # Mua cổ phiếu khi có tín hiệu
        if self.crossover > 0 and not self.position:
            self.buy_price = self.data.close[0]
            self.buy(size=None)
            self.holding = True
            self.current_quarter = current_quarter
            print(f'BUY CREATE: {self.data.datetime.date(0)} - Buy price: {self.data.close[0]:.2f}')

                # Bán cổ phiếu khi có tín hiệu
        elif self.crossover < 0 and self.position:
            sell_price = self.data.close[0]
            self.sell(size=None)
            profit_pct = (sell_price - self.buy_price) / self.buy_price
            self.holding = False
            self.quarterly_returns[self.current_quarter] += profit_pct
            print(f'SELL CREATE: {self.data.datetime.date(0)} - Sell price: {self.data.close[0]:.2f}, Profit: {profit_pct:.2%}')

    def stop(self):
        if self.holding:
            sell_price = self.data.close[0]
            profit_pct = (sell_price - self.buy_price) / self.buy_price
            self.quarterly_returns[self.current_quarter] += profit_pct
            print(f'SELL ALL at the end: {self.data.datetime.date(0)} - Sell price: {self.data.close[0]:.2f}, Profit: {profit_pct:.2%}')


# Tải giá đóng cửa và thực hiện chiến thuật Trading SMA
st.header(":blue[CHỌN FILE .CSV ĐỂ TẢI LÊN]")
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #D4F6FF;
        color: white;
    }
    div.stButton > button[kind="primary"] {
        background-color: #FBFBFB;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Quay trở lại trang chủ",type="primary",use_container_width=True,icon="🏠"):
    st.switch_page("main_app.py")
    
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover;
        background-color: rgba(255, 255, 255, 0.7); /* Điều chỉnh độ mờ ở đây */
        background-blend-mode: overlay;
    }}
    .custom-title {{
        color: #F05454;
    }}
    .stMarkdown, .stText {{
        color: #30475E !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

add_bg_from_local('background.png')

st.logo("big_logo.png",icon_image="small_logo.png")

prices = st.file_uploader(":red[        ]", type="csv")

# Kiểm tra nếu file đã được tải lên
if prices is not None:
    # Đọc file CSV bằng pandas
    prices = pd.read_csv(prices,index_col=0)

    # Hiển thị dữ liệu trong Streamlit
    st.write("Dữ liệu đã tải lên!")
    st.dataframe(prices,width=1000, height=200,column_order=('ticker','time','open','high','close','volume'),hide_index=True)
    x=st.button("Ấn nút để bắt đầu tính toán")
    if x==True:
        st.success("Đang thực hiện tính toán...")

        mcp=prices.ticker.unique()
        R_ma_check=[]
        ticker_ma_check=[]
        check_num_of_obs=stock_historical_data('REE','2018-01-01','2023-12-31')
        num_of_obs=check_num_of_obs.drop_duplicates(subset='time',keep='first').shape[0]
        for i in mcp:
            try:
                DT=prices[prices['ticker']==i]
                if DT.drop_duplicates(subset='time',keep='first').shape[0]!=num_of_obs:
                    continue
                DT['time'] = pd.to_datetime(DT['time'])
                DT = DT.set_index('time')
                #TẠO DỮ LIỆU
                data=bt.feeds.PandasData(dataname=DT)#DT LÀ DỮ LIÊU CỔ PHIẾU ĐÃ ĐƯỢC LẤY Ở TRÊN

                #thực thi chiến thuật
                cerebro=bt.Cerebro() #tạo cerebro

                cerebro.addstrategy(Basic_MACrossStrategy) #truyền chiến thuật


                cerebro.adddata(data) #truyền dữ liệu


                cerebro.broker.setcash(1000000000) #số tiền đầu tư
                cerebro.broker.setcommission(commission=0.0015) #số tiền hoa hồng/giao dịch
                cerebro.addsizer(bt.sizers.AllInSizerInt,percents = 95)#số cổ phiếu mua mỗi giao dịch


                print(i)
                before=cerebro.broker.getvalue()
                print('Số tiền trước khi thực hiện chiến thuật: %.2f' % before)
                cerebro.run() #thực thi chiến thuật
                after=cerebro.broker.getvalue()
                print('Số tiền sau khi thực hiện chiến thuật: %.2f' % after)
                r=(after-before)/before
                ticker_ma_check.append(i)
                R_ma_check.append(r)
            except Exception:
                continue
        return_ma_check=pd.DataFrame({'Ticker':ticker_ma_check,'Return':R_ma_check})

        return_ma_check=return_ma_check.sort_values('Return',ascending=False).head(50)

        mcp=return_ma_check.Ticker.to_list()

        list_allo=pd.DataFrame({'Asset':mcp})

        st.title('50 cổ phiếu cho lợi nhuận cao nhất trên chiến thuật SMA theo file dữ liệu')
        return_ma_check_sorted = return_ma_check.sort_values('Return', ascending=False)

        # Tùy chỉnh biểu đồ
        fig = go.Figure(data=[
            go.Bar(x=return_ma_check_sorted['Ticker'], y=return_ma_check_sorted['Return'] * 100)
        ])
        
        # Tùy chỉnh biểu đồ
        fig.update_layout(
            xaxis=dict(
                title='<b>Mã cổ phiếu</b>',  # In đậm tiêu đề trục x
                tickangle=-45,  # Góc xoay cho nhãn trục x
                tickfont=dict(size=12, color='black', family='Arial', bold=True)  # In đậm nhãn trục x
            ),
            yaxis=dict(
                title='<b>Tỷ suất lợi nhuận (%)</b>',  # In đậm tiêu đề trục y
                tickformat="%.2f%%",  # Định dạng số liệu
                tickfont=dict(size=12, color='black', family='Arial', bold=True)  # In đậm nhãn trục y
            ),
            plot_bgcolor='rgba(0,0,0,0)',  # Nền biểu đồ trong suốt
            paper_bgcolor='rgba(0,0,0,0)',  # Nền toàn bộ khung trong suốt
            height=800,
            width=1200
        )


        
        # Hiển thị biểu đồ trong Streamlit
        st.plotly_chart(fig)

        mcp=list_allo.Asset.to_list()


        # # Khai báo chiến thuật SMA

        # ### Ý tưởng chính là chia dữ liệu theo từng quý và chỉ tính lợi nhuận trong những khoảng thời gian mà có nắm giữ cổ phiếu (tức là chỉ khi đã mua cổ phiếu và trước khi bán).
        # Khai báo biến lưu kết quả
        quarterly_returns_MA = {}

        for i in mcp:
            try:
                print(f"\nĐang xử lý mã: {i}")

                DT=prices[prices['ticker']==i]
                DT['time'] = pd.to_datetime(DT['time'])
                DT = DT.set_index('time')

                data = bt.feeds.PandasData(dataname=DT)

                cerebro = bt.Cerebro()
                cerebro.addstrategy(MACrossStrategy)
                cerebro.adddata(data, name=i)
                cerebro.broker.setcash(1000000000)
                cerebro.broker.setcommission(commission=0.0015)
                cerebro.addsizer(bt.sizers.AllInSizerInt, percents=95)

                before = cerebro.broker.getvalue()
                print(f'Số tiền ban đầu: {before:.2f}')

                # Chạy chiến lược
                strategy_instances = cerebro.run()

                after = cerebro.broker.getvalue()
                print(f'Số tiền sau khi thực hiện chiến lược: {after:.2f}')

                # Tính tỷ lệ lợi nhuận
                r = (after - before) / before
                print(f'Lợi nhuận từ mã {i}: {r:.2%}')

                # Lưu lợi nhuận theo quý cho mã này
                quarterly_returns_MA[i] = strategy_instances[0].quarterly_returns

            except Exception as e:
                print(f"Error processing {i}: {e}")
                continue
                
        # Chuyển kết quả quarterly_returns_MA thành DataFrame
        quarterly_returns_df = pd.DataFrame.from_dict(quarterly_returns_MA, orient='index').T


        # Tạo tệp train 
        train_data = quarterly_returns_df
        # Reset index để đưa 'year' và 'quarter' về thành cột
        train_data = train_data.reset_index()


        # Xóa cột 'year' và 'quarter' sau khi reset index
        train_data = train_data.drop(columns=['level_0','level_1'])


        # Lớp CustomModel với hàm sharpe_loss
        class CustomModel:
            def __init__(self, data):
                self.data = data

            def sharpe_loss(self, _, y_pred):
                # Chia giá trị từng cột cho giá trị đầu tiên của cột đó
                data_normalized = tf.divide(self.data, self.data[0] + K.epsilon())
                # Tính giá trị danh mục đầu tư (portfolio)
                portfolio_values = tf.reduce_sum(tf.multiply(data_normalized, y_pred), axis=1)
                # Tránh chia cho 0 hoặc các giá trị bất thường
                portfolio_values = tf.where(tf.equal(portfolio_values, 0), K.epsilon(), portfolio_values)
                # Tính toán lợi nhuận danh mục đầu tư
                portfolio_returns = (portfolio_values[1:] - portfolio_values[:-1]) / (portfolio_values[:-1] + K.epsilon())
                # Tính Sharpe ratio
                sharpe = K.mean(portfolio_returns) / (K.std(portfolio_returns) + K.epsilon())
                return -sharpe

        X_train = train_data.values[np.newaxis, :, :]
        y_train = np.zeros((1, len(train_data.columns)))


        # Khởi tạo mô hình tùy chỉnh
        data_tensor = tf.cast(tf.constant(train_data), float)
        custom_model = CustomModel(data_tensor)


        # Tạo mô hình LSTM
        model = Sequential([
            LSTM(512, input_shape=train_data.shape),
            Flatten(),
            Dense(train_data.shape[1], activation='softmax')
        ])

        # Biên dịch mô hình
        model.compile(
            optimizer= 'Adam',
            loss=custom_model.sharpe_loss
        )


        model_LSTM = model.fit(X_train, y_train, epochs=100, shuffle=False)


        optimal_weights = model.predict(X_train)
        coeff_1 = optimal_weights[0]


        results_LSTM = pd.DataFrame({'Asset':mcp,"Weight":coeff_1})


        st.title('Biểu đồ phân bổ tài sản của danh mục đầu tư')

        square_plot_test = pd.DataFrame({
            'Cổ phiếu': results_LSTM.sort_values('Weight', ascending=False).Asset,
            'Tỷ trọng': results_LSTM.sort_values('Weight', ascending=False).Weight
        })

        # Sắp xếp DataFrame theo tỷ trọng
        square_plot_test = square_plot_test.sort_values('Tỷ trọng', ascending=True)

        # Tạo nhãn mới bao gồm cả tên cổ phiếu và tỷ trọng
        square_plot_test['Nhãn'] = square_plot_test['Cổ phiếu'] + '<br>' + square_plot_test['Tỷ trọng'].apply(lambda x: f"{x*100:.2f}").astype(str) + '%'

        # Định nghĩa màu sắc cho các khối
        colors = [
            '#AB63FA',  # Tím nhạt
            '#636EFA',  # Xanh dương nhạt
            '#A1CAF1',  # Xanh nhạt
            '#19D3F3',  # Xanh cyan
            '#00CC96',  # Xanh lá cây
            '#B6E880',  # Xanh lá cây nhạt
            '#FECB52',  # Vàng
            '#FFA15A',  # Cam sáng
            '#EF553B',  # Đỏ cam
            '#D62728'   # Đỏ đậm (nóng nhất)
        ]


        # Tạo biểu đồ treemap
        fig = px.treemap(
            square_plot_test,
            path=['Cổ phiếu'],
            values='Tỷ trọng',
            color='Tỷ trọng',
            color_continuous_scale=colors,
            custom_data=['Nhãn'],
            hover_data=['Tỷ trọng']
        )

        # Tùy chỉnh hiển thị
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>Tỷ trọng: %{value:.2%}<extra></extra>',
            texttemplate='<b>%{label}<br>%{value:.2%}</b>',  # Thêm thẻ <b> để in đậm
            textposition="middle center",  # Đặt vị trí text ở giữa
            textfont=dict(size=10, family="Arial Black")  # Tăng độ đậm của font
        )
                # Tùy chỉnh kích thước biểu đồ
        fig.update_layout(
            width=1000,  # Tăng chiều rộng
            height=800,  # Tăng chiều cao
        )
        # Hiển thị biểu đồ trong Streamlit
        st.plotly_chart(fig)


