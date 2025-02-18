import streamlit as st
import pandas as pd
import numbers
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from cryptocmd import CmcScraper
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
from hyperopt import tpe, fmin

import os, sys
lib_path = os.path.abspath(os.path.join('.','deribit_service/python'))
sys.path.append(lib_path)
from deribit_service import lib_options
from lib import lib_strategy, lib_tuning



### Plot functions
def plot_raw_data():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close'))
	fig.layout.update(width=1100, height=500, title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)

def plot_raw_data_log():
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close'))
	fig.update_yaxes(type='log')
	fig.layout.update(width=1100, height=500, title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
	st.plotly_chart(fig)


# Config layout
st.set_page_config(layout='wide')
col1, col2 = st.beta_columns([7, 2])

with col1:
	st.title('Parameter Optimization')

	st.markdown('This application enables you to optimize the parameters in list of trading strategies.')

	### Change sidebar color
	st.markdown(
	    """
	<style>
	.sidebar .sidebar-content {
	    background-image: linear-gradient(#D6EAF8,#D6EAF8);
	    color: black;
	}
	</style>
	""",
	    unsafe_allow_html=True,
	)

	### Set bigger font style
	st.markdown(
		"""
	<style>
	.big-font {
		fontWeight: bold;
	    font-size:22px !important;
	}
	</style>
	""", unsafe_allow_html=True)

	st.sidebar.markdown("<p class='big-font'><font color='black'>Data Settings</font></p>", unsafe_allow_html=True)

	### Initialise scraper without time interval
	asset = st.selectbox('Select asset', ('Currency', 'Options'), 1)

	if asset == 'Currency':
	   selected_ticker = st.sidebar.text_input('Select a ticker for prediction (i.e. BTC, ETH, LINK, etc.)', 'BTC')

	   @st.cache
	   def load_data(selected_ticker):
	   	init_scraper = CmcScraper(selected_ticker)
	   	data = init_scraper.get_dataframe()
	   	min_date = pd.to_datetime(min(data['Date']))
	   	max_date = pd.to_datetime(max(data['Date']))
	   	return min_date, max_date

	   data_load_state = st.sidebar.text('Loading data...')
	   min_date, max_date = load_data(selected_ticker)
	   data_load_state.text('Loading data... done!')

	   ### Select date range
	   date_range = st.sidebar.selectbox('Select the timeframe to train the model on:', options=['All available data', 'Specific date range'])

	   if date_range == 'All available data':

	   	### Initialise scraper without time interval
	   	scraper = CmcScraper(selected_ticker)

	   elif date_range == 'Specific date range':

	   	### Initialise scraper with time interval
	   	start_date = st.sidebar.date_input('Select start date:', min_value=min_date, max_value=max_date, value=min_date)
	   	end_date = st.sidebar.date_input('Select end date:', min_value=min_date, max_value=max_date, value=max_date)
	   	scraper = CmcScraper(selected_ticker, str(start_date.strftime('%d-%m-%Y')), str(end_date.strftime('%d-%m-%Y')))

	   ### Pandas dataFrame for the same data
	   data = scraper.get_dataframe()
	   data = data.sort_values('Date', ignore_index=True)

	if asset == 'Options':
	    input_data = {}
	    max_date = datetime.now()
	    min_date = datetime(2019, 4, 1)
	    instrument_name = st.sidebar.text_input('Select an instrument for prediction (i.e. BTC-PERPETUAL)', 'BTC-PERPETUAL')
	    input_data['instrument_name'] = instrument_name
	    input_data['resolution'] = '1D' #frequency 1 min

	    date_range = st.sidebar.selectbox('Select the timeframe to train the model on:', options=['All available data', 'Specific date range'])

	    if date_range == 'All available data':
	       input_data['start_timestamp'] = int(min_date.strftime('%s')) * 1000
	       input_data['end_timestamp'] = int(max_date.strftime('%s')) * 1000

	    elif date_range == 'Specific date range':
	        start_time = st.sidebar.date_input('Select start time:', min_value=min_date, max_value=max_date, value=min_date)
	        end_time = st.sidebar.date_input('Select end time:', min_value=min_date, max_value=max_date, value=max_date)
	        input_data['start_timestamp'] = int(start_time.strftime('%s')) * 1000
	        input_data['end_timestamp'] = int(end_time.strftime('%s')) * 1000

	    json_resp = lib_options.load_data(input_data)
	    data = lib_options.transform_data(json_resp)
	    data = data.rename(columns={'timestamp': 'date'})
	    data.columns = [col.title() for col in data.columns]

	### Select number of days to predict on
	# period = int(st.sidebar.number_input('Number of days to predict:', min_value=0, max_value=1000000, value=365, step=1))
	# training_size = int(st.sidebar.number_input('Training set (%) size:', min_value=10, max_value=100, value=100, step=5)) / 100

	st.subheader('Raw data')
	st.write(data.head())

	### Plot (log) data
	plot_log = st.checkbox('Plot log scale')
	if plot_log:
		plot_raw_data_log()
	else:
		plot_raw_data()

	strategy = st.selectbox('Select trading strategy', ('EMA', 'MACD'), 0)

	tune_algo = st.selectbox('Select tuning algorithm', ('Genetic Algorithm', 'Bayesian Optimization'), 1)
	if tune_algo == 'Genetic Algorithm':
		max_gen = int(st.text_input('Maximum number of generations', 10))
	if tune_algo == 'Bayesian Optimization':
		max_evals = int(st.text_input('Maximum number of evaluations', 10))

	# Init
	backtest_data = {}
	paras_dict = {}
	cash = float(st.text_input('Init cash', 1000000))
	commission = float(st.text_input('Commission', 0.001))

	is_run = st.button(label='Run strategy')

	if is_run:
		if strategy == 'EMA':
		    paras_default = {'short_window': 50, 'long_window': 200}
		    ema_position = lib_strategy.find_position(data, paras=paras_default, strat='EMA')
		    data['position'] = ema_position
		    backtest_data['EMA'] = data.copy()
		    paras_dict['EMA'] = paras_default

		if strategy == 'MACD':
			paras_default = {'window_slow': 26, 'window_fast': 12, 'window_sign': 9}
			macd_position = lib_strategy.find_position(data, paras=paras_default, strat='MACD')
			data['position'] = macd_position
			backtest_data['MACD'] = data.copy()
			paras_dict['MACD'] = paras_default

		# Tuning
		if tune_algo == 'Genetic Algorithm':
			paras_best = lib_tuning.ga_config(data, cash, commission, max_gen, strat=strategy)

		if tune_algo == 'Bayesian Optimization':
			score, fspace = lib_tuning.bo_config(data, cash, commission, strat=strategy)
			paras_best = fmin(fn=score, space=fspace, algo=tpe.suggest, max_evals=max_evals)

		paras_best = pd.Series(paras_best)

		# Backtest
		st.subheader('Performance')
		position = lib_strategy.find_position(data, paras_best, strategy)
		data['position'] = position
		bt, stats = lib_tuning.backtest(data, cash, commission)

		per_df = stats.loc[[
			'Start', 'End', 'Duration', 'Equity Final [$]', 'Return [%]', 'Return (Ann.) [%]',
			'Sharpe Ratio', 'Max. Drawdown [%]', 'Max. Drawdown Duration',
			'# Trades'
		]].applymap(lambda x: x if not isinstance(x, numbers.Number) else round(x, 2)).astype(str)
		per_df = pd.concat([per_df, paras_best])
		per_df.columns = [strategy]

		st.dataframe(per_df, height=1000)

		fig = bt.plot(plot_volume=False, superimpose=False, open_browser=False)
		import streamlit.components.v1 as components
		HtmlFile = open('GeneralStrategy.html', 'r', encoding='utf-8')
		source_code = HtmlFile.read()
		components.html(source_code, width=1100, height=700)
