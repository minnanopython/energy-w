import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta, date, datetime
import altair as alt
import numpy as np

# --------------------------------------------------------------------------------------
# 銘柄と分析データを統合した設定
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="energy-w",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
DEFAULT_SECTOR = "総合商社"
SECTORS_RAW = {
    "総合商社": {
        '8058.T': '三菱商事', '8031.T': '三井物産', '8001.T': '伊藤忠商事',
        '8053.T': '住友商事', '8002.T': '丸紅', '8015.T': '豊田通商',
        '2768.T': '双日', '8020.T': '兼松',
    },
    "エネルギー資源": {
        '5020.T': 'ＥＮＥＯＳＨＤ', '5019.T': '出光興産', '5021.T': 'コスモエネルギーＨＤ',
        '1605.T': 'ＩＮＰＥＸ', '1662.T': '石油資源開発', '1515.T': '日鉄鉱業',
    },
    "主要電力": {
        '9509.T': '北海道電力', '9506.T': '東北電力', '9501.T': '東京電力ＨＤ',
        '9502.T': '中部電力', '9503.T': '関西電力', '9505.T': '北陸電力',
        '9504.T': '中国電力', '9507.T': '四国電力', '9508.T': '九州電力',
        '9511.T': '沖縄電力', '9513.T': '電源開発',
    },
    "電力電設": {
        '1934.T': 'ユアテック', '1942.T': '関電工', '1946.T': 'トーエネック',
        '1944.T': 'きんでん', '1930.T': '北陸電気工事', '1941.T': '中電工',
        '1959.T': '九電工', '1939.T': '四電工',
    },
    "電設工事": {
        '1417.T': 'ミライト・ワン', '1721.T': 'コムシスＨＤ', '1951.T': 'エクシオグループ',
        '1945.T': '東京エネシス', '1950.T': '日本電設工業', '1938.T': '日本リーテック',
    },
}

SECTORS = SECTORS_RAW
ALL_STOCKS_MAP = {ticker: name for stocks in SECTORS_RAW.values() for ticker, name in stocks.items()}
ALL_TICKERS_WITH_N225 = list(set(list(ALL_STOCKS_MAP.keys()) + ['^N225']))
CURRENT_DATE = datetime.now().date()
CURRENT_YEAR = CURRENT_DATE.year
YEARS_TO_CALCULATE_STR = [str(y) for y in sorted(list(set([CURRENT_YEAR, 2023])), reverse=True) if y <= CURRENT_YEAR]
NEW_PERIODS = ["1mo", "2mo", "3mo", "4mo", "5mo", "6mo", "9mo", "1y", "2y"]

# --------------------------------------------------------------------------------------
# データ取得とキャッシュを行う関数
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=True, ttl=timedelta(minutes=30))
def load_weekly_stock_data_cached(tickers_list):
    """週次終値データを取得しキャッシュする関数"""
    if not tickers_list:
        return pd.DataFrame()
    tickers_for_history = list(set(tickers_list))
    weekly_close_data = pd.DataFrame()
    try:
        tickers_obj = yf.Tickers(tickers_for_history)
        data_ohlcv = tickers_obj.history(period="3y", interval="1wk", auto_adjust=True)        
        if 'Close' in data_ohlcv.columns.get_level_values(0):
            weekly_close_data = data_ohlcv['Close']
            if isinstance(weekly_close_data, pd.Series):
                weekly_close_data = weekly_close_data.to_frame(name=tickers_for_history[0])
            weekly_close_data.columns.name = 'Ticker'
            weekly_close_data = weekly_close_data.dropna(axis=0, how='all')
            weekly_close_data.index = weekly_close_data.index.tz_localize(None)
        elif 'Close' in data_ohlcv.columns: # for single ticker case
            weekly_close_data = data_ohlcv['Close'].to_frame(name=tickers_for_history[0])
            weekly_close_data.columns.name = 'Ticker'
            weekly_close_data = weekly_close_data.dropna(axis=0, how='all')
            weekly_close_data.index = weekly_close_data.index.tz_localize(None)
    except yf.exceptions.YFRateLimitError as e:
        raise e
    except Exception as e:
        st.error(f"yfinanceデータ取得エラー: {e}")
        return pd.DataFrame()
    return weekly_close_data

# --------------------------------------------------------------------------------------
# データ取得、キャッシュの実行
# --------------------------------------------------------------------------------------
weekly_data_raw = pd.DataFrame()
try:
    with st.spinner("株価データをロード中..."):
        weekly_data_raw = load_weekly_stock_data_cached(ALL_TICKERS_WITH_N225)
except yf.exceptions.YFRateLimitError:
    st.warning("YFinanceの接続制限が発生しています。しばらくしてから再試行してください。")
    load_weekly_stock_data_cached.clear()
    st.stop()
except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
    st.stop()

# --------------------------------------------------------------------------------------
# 銘柄選択に関する関数
# --------------------------------------------------------------------------------------
def get_stock_name(ticker_code):
    """ティッカーコードから銘柄名を取得"""
    if ticker_code == '^N225':
        return "日経平均"
    return ALL_STOCKS_MAP.get(ticker_code, ticker_code)

def update_stock_selection(sector_key, stock_key, reset_key):
    """セクター選択に応じて銘柄選択をリセットするためのコールバック"""
    st.session_state[reset_key] = True

def get_filtered_stocks(sector_key, stock_key, reset_key): 
    """選択されたセクターと銘柄に基づいてフィルターされた銘柄マップを取得"""
    selected_sectors = st.session_state[sector_key]
    SELECTED_SECTOR_STOCKS_MAP = {}
    if selected_sectors:
        for sector in selected_sectors:
            SELECTED_SECTOR_STOCKS_MAP.update(SECTORS.get(sector, {}))
    else:
        SELECTED_SECTOR_STOCKS_MAP = ALL_STOCKS_MAP
    all_current_stock_names = [name for name in SELECTED_SECTOR_STOCKS_MAP.values()]
    if st.session_state.get(reset_key):
        st.session_state[stock_key] = all_current_stock_names
        del st.session_state[reset_key]
    elif stock_key not in st.session_state:
        st.session_state[stock_key] = all_current_stock_names
    else:
        current_selection = st.session_state[stock_key]
        st.session_state[stock_key] = [name for name in current_selection if name in all_current_stock_names]
    FINAL_STOCKS_MAP = {}
    name_to_ticker = {name: ticker for ticker, name in SELECTED_SECTOR_STOCKS_MAP.items()}
    for name in st.session_state[stock_key]:
        ticker = name_to_ticker.get(name)
        if ticker:
            FINAL_STOCKS_MAP[ticker] = name            
    return FINAL_STOCKS_MAP, all_current_stock_names

# --------------------------------------------------------------------------------------
# 共通データ処理関数
# --------------------------------------------------------------------------------------
def filter_data_by_period(weekly_data_raw: pd.DataFrame, period_label: str) -> pd.DataFrame:
    """指定された期間（例: 1mo, 3mo, 1y, 2y）で週次データをフィルタリングする"""
    if weekly_data_raw.empty:
        return pd.DataFrame()
    end_date = weekly_data_raw.index.max()
    period_map = {
        "1mo": 4, "2mo": 8, "3mo": 13, "4mo": 17, "5mo": 22,
        "6mo": 26, "9mo": 39, "1y": 52, "2y": 52 * 2,
    }
    weeks_to_subtract = period_map.get(period_label)
    if weeks_to_subtract is None:
        return pd.DataFrame() 
    start_date = end_date - timedelta(weeks=weeks_to_subtract + 1)      
    return weekly_data_raw[weekly_data_raw.index >= start_date].copy()

def calculate_gain_data(plot_data_raw: pd.DataFrame) -> pd.DataFrame:
    """株価データから基準日を1.0とした騰落率データに変換する"""
    if plot_data_raw.empty or plot_data_raw.shape[0] < 2:
        return pd.DataFrame()
    first_valid_index = plot_data_raw.first_valid_index()
    if first_valid_index is None:
        return pd.DataFrame()        
    plot_data_raw = plot_data_raw.loc[:, plot_data_raw.loc[first_valid_index].notna()]
    valid_first_prices = plot_data_raw.loc[first_valid_index]
    if not valid_first_prices.empty and (valid_first_prices != 0).all():
        extracted_normalized = plot_data_raw / valid_first_prices
        return extracted_normalized
    else:
        return pd.DataFrame()

# --------------------------------------------------------------------------------------
# グラフ描画関数
# --------------------------------------------------------------------------------------
num_cols = 8 # ★1行に表示するグラフの数
def create_and_display_charts(data_to_plot, period_label, y_min_param, y_max_param, is_gain_chart, auto_scale=False, chart_container=st):
    """Altairでグラフを作成し表示する (騰落率/株価 兼用)"""    
    stock_tickers = [t for t in data_to_plot.columns if t != '^N225']
    if data_to_plot.empty or stock_tickers == []:
        return 
    y_domain = None
    if is_gain_chart:
        if auto_scale:
            min_ratio = data_to_plot.min().min()
            max_ratio = data_to_plot.max().max()
            if np.isnan(min_ratio) or np.isnan(max_ratio):
                y_domain = [1.0 - 0.10, 1.0 + 0.10]
            else:
                buffer = (max_ratio - min_ratio) * 0.1
                y_domain = [max(0.0, min_ratio - buffer), max_ratio + buffer]
        else:
            y_min_ratio = 1.0 + y_min_param / 100.0
            y_max_ratio = 1.0 + y_max_param / 100.0
            if y_min_ratio >= y_max_ratio:
                y_domain = [1.0 - 0.10, 1.0 + 0.10]
            else:
                y_domain = [y_min_ratio, y_max_ratio]
        y_axis_config = alt.Axis(
            title=None,
            labelExpr="datum.value == 1 ? '0%' : format((datum.value - 1) * 100, '+.0f') + '%'" 
        )
        tooltip_title = "騰落率"
        tooltip_format = '+0.2%'         
    else:
        y_domain = None        
        y_axis_config = alt.Axis(title=None, format="~s")
        tooltip_title = "価格"
        tooltip_format = ',.2f'
    date_range = data_to_plot.index.max() - data_to_plot.index.min()
    tick_count_val = 'auto'
    if period_label in ["1mo", "2mo", "3mo"]:
        x_format = "%m/%d"
        tick_count_val = 10
    elif period_label in ["4mo", "5mo", "6mo", "9mo", "1y"]:
        x_format = "%Y/%m"
        tick_count_val = 'month'
    elif date_range.days <= 400 * 3:
        x_format = "%Y/%m"
        tick_count_val = 'month'
    else:
        x_format = "%Y"
        tick_count_val = 'year'
    for row_i in range((len(stock_tickers) + num_cols - 1) // num_cols):
        cols = chart_container.columns(num_cols)
        for col_i in range(num_cols):
            idx = row_i * num_cols + col_i
            if idx < len(stock_tickers):
                ticker = stock_tickers[idx]
                stock_data = pd.DataFrame({
                    "Date": data_to_plot.index,
                    "Value": data_to_plot[ticker],
                })
                stock_data['z_index'] = 1                 
                combined_data = stock_data.dropna(subset=['Value'])                
                has_nikkei_comparison = is_gain_chart and '^N225' in data_to_plot.columns
                
                if has_nikkei_comparison:
                    nikkei_data = pd.DataFrame({
                        "Date": data_to_plot.index,
                        "Value": data_to_plot['^N225'],
                    })
                    nikkei_data['z_index'] = 0 
                    combined_data = pd.concat([combined_data, nikkei_data]).dropna(subset=['Value'])
                
                valid_values = combined_data['Value'].dropna()
                if combined_data.empty or valid_values.empty: 
                    continue

                title_text = ticker[:4] + " " + get_stock_name(ticker) 
                
                base_chart = alt.Chart(combined_data).encode(
                    alt.X("Date:T", axis=alt.Axis(
                        format=x_format, title=None, labelAngle=0, tickCount=tick_count_val
                    )),
                    alt.Y("Value:Q",
                        scale=alt.Scale(zero=False, domain=y_domain) if y_domain else alt.Scale(zero=False),
                        axis=y_axis_config),
                )
                stock_line = base_chart.transform_filter(
                    alt.datum.z_index == 1
                ).mark_line(
                    strokeWidth=2
                ).encode(
                    color=alt.value("#C70025"), 
                    order=alt.Order("z_index:Q", sort="descending"),
                    tooltip=[
                        alt.Tooltip("Date:T", title="日付", format="%Y/%m/%d"),
                        alt.Tooltip("Value:Q", title=f"{title_text}{tooltip_title}", format=tooltip_format)
                    ]
                )                
                final_chart = stock_line
                if has_nikkei_comparison:
                    nikkei_line = base_chart.transform_filter(
                        alt.datum.z_index == 0
                    ).mark_line(
                        strokeWidth=1.5
                    ).encode(
                        color=alt.value("#A9A9A9"), 
                        order=alt.Order("z_index:Q", sort="descending"),
                        tooltip=[
                            alt.Tooltip("Date:T", title="日付", format="%Y/%m/%d"),
                            alt.Tooltip("Value:Q", title="日経" + tooltip_title, format=tooltip_format)
                        ]
                    )
                    final_chart = nikkei_line + stock_line
                chart = final_chart.properties(
                    title=alt.TitleParams(
                        f"{title_text}",
                        fontSize=12,
                    ),
                    height=160,
                    width='container'
                )
                cell = cols[col_i].container(border=False)
                cell.altair_chart(chart, width='stretch')

# --------------------------------------------------------------------------------------
# 1. Priceチャートのセクター選択・銘柄選択のウィジェット
# --------------------------------------------------------------------------------------
st.markdown("## 📈 Price Chart")
""
col_select_sector_price, col_select_stock_price = st.columns([1, 4])
PRICE_SECTOR_KEY = "multiselect_sectors_price"
PRICE_STOCK_KEY = "multiselect_stocks_price"
PRICE_RESET_KEY = "_reset_price"
with col_select_sector_price:
    sector_options = list(SECTORS.keys())    
    if PRICE_SECTOR_KEY not in st.session_state:
        st.session_state[PRICE_SECTOR_KEY] = [DEFAULT_SECTOR]
    if PRICE_RESET_KEY not in st.session_state:
        st.session_state[PRICE_RESET_KEY] = False
    st.multiselect(
        "セクターを選択 (Price)",
        options=sector_options,
        key=PRICE_SECTOR_KEY,
        label_visibility="collapsed",
        on_change=lambda: update_stock_selection(PRICE_SECTOR_KEY, PRICE_STOCK_KEY, PRICE_RESET_KEY)
    )
FILTERED_STOCKS_PRICE, all_stock_names_price = get_filtered_stocks(
    PRICE_SECTOR_KEY, PRICE_STOCK_KEY, PRICE_RESET_KEY
)
with col_select_stock_price:
    st.multiselect(
        "銘柄を選択 (Price)",
        options=all_stock_names_price,
        key=PRICE_STOCK_KEY,
        label_visibility="collapsed"
    )
selected_plot_tickers_price = list(FILTERED_STOCKS_PRICE.keys())

# --------------------------------------------------------------------------------------
# 2. Priceチャート
# --------------------------------------------------------------------------------------
col_charts_price = st.container()
with col_charts_price:
    if not selected_plot_tickers_price:
        st.info("Priceグラフに表示する銘柄を上記マルチセレクトで選択してください。")
    elif weekly_data_raw.empty:
        st.info("データがロードされていないため、Priceグラフを表示できません。")
    else:
        ALL_PLOT_PERIODS_KEYS_ORDER = NEW_PERIODS + YEARS_TO_CALCULATE_STR
        tabs = st.tabs(ALL_PLOT_PERIODS_KEYS_ORDER)
        
        for i, period_label in enumerate(ALL_PLOT_PERIODS_KEYS_ORDER):
            with tabs[i]:
                plot_data_raw = pd.DataFrame()
                if period_label in NEW_PERIODS:
                    plot_data_raw = filter_data_by_period(weekly_data_raw, period_label)
                else: 
                    target_year = int(period_label)
                    start_date_of_year = datetime(target_year, 1, 1).date()
                    plot_data_raw = weekly_data_raw[
                        weekly_data_raw.index.date >= start_date_of_year
                    ].copy()
                plot_tickers_in_data = [t for t in selected_plot_tickers_price if t in plot_data_raw.columns and t != '^N225']                 
                if plot_tickers_in_data and not plot_data_raw.empty and plot_data_raw.shape[0] >= 1:
                    stock_only_data = plot_data_raw[plot_tickers_in_data].copy()                     
                    if not stock_only_data.empty:
                        create_and_display_charts(
                            stock_only_data,
                            period_label,
                            y_min_param=0, y_max_param=0,
                            is_gain_chart=False,
                            auto_scale=True,
                            chart_container=st
                        )
                    else:
                        st.info("選択された銘柄の株価データがありません。")
                else:
                    st.info(f"選択された銘柄について「{period_label}」の有効な株価データがありませんでした。")

# --------------------------------------------------------------------------------------
# 3. Gainチャートのセクター選択・銘柄選択のウィジェット
# --------------------------------------------------------------------------------------
""
st.markdown("## 📈 Gain Chart")
""
col_select_sector_gain, col_select_stock_gain = st.columns([1, 4])
GAIN_SECTOR_KEY = "multiselect_sectors_gain"
GAIN_STOCK_KEY = "multiselect_stocks_gain"
GAIN_RESET_KEY = "_reset_gain"
with col_select_sector_gain:    
    if GAIN_SECTOR_KEY not in st.session_state:
        st.session_state[GAIN_SECTOR_KEY] = [DEFAULT_SECTOR]
    if GAIN_RESET_KEY not in st.session_state:
        st.session_state[GAIN_RESET_KEY] = False        
    st.multiselect(
        "セクターを選択 (Gain)",
        options=sector_options,
        key=GAIN_SECTOR_KEY,
        label_visibility="collapsed",
        on_change=lambda: update_stock_selection(GAIN_SECTOR_KEY, GAIN_STOCK_KEY, GAIN_RESET_KEY)
    )
FILTERED_STOCKS_GAIN, all_stock_names_gain = get_filtered_stocks(
    GAIN_SECTOR_KEY, GAIN_STOCK_KEY, GAIN_RESET_KEY
)
with col_select_stock_gain:
    st.multiselect(
        "銘柄を選択 (Gain)",
        options=all_stock_names_gain,
        key=GAIN_STOCK_KEY,
        label_visibility="collapsed"
    )
selected_plot_tickers_gain = list(FILTERED_STOCKS_GAIN.keys())
if '^N225' in weekly_data_raw.columns and '^N225' not in selected_plot_tickers_gain:
     selected_plot_tickers_gain.append('^N225')
def update_gain_value(key_to_check, key_to_update):
    current_value = st.session_state[key_to_check]
    st.session_state[key_to_update] = current_value
def get_radio_index(options_list, key):
    selected_value = st.session_state.get(key)
    if selected_value is None:
        return 0
    try:
        if selected_value in options_list:
            return options_list.index(selected_value)
        selected_numeric = float(selected_value)
        options_numeric = [float(opt) for opt in options_list]
        return min(range(len(options_numeric)), key=lambda i: abs(options_numeric[i] - selected_numeric))
    except ValueError:
        return 0
if "autoscale_enabled_gain" not in st.session_state:
    st.session_state["autoscale_enabled_gain"] = True
if "selected_max_gain_value" not in st.session_state:
    st.session_state["selected_max_gain_value"] = "+10"
if "selected_min_gain_value" not in st.session_state:
    st.session_state["selected_min_gain_value"] = "-10"
autoscale_enabled = st.session_state["autoscale_enabled_gain"] = True
y_min_gain = -1.0  
y_max_gain = 1.0
selected_max_text = st.session_state["selected_max_gain_value"]
selected_min_text = st.session_state["selected_min_gain_value"]
col_charts_gain = st.container()

# --------------------------------------------------------------------------------------
# 4. Gainチャート
# --------------------------------------------------------------------------------------
with col_charts_gain:
    if not selected_plot_tickers_gain:
        st.info("Gainグラフに表示する銘柄を上部のマルチセレクトで選択してください。")
    elif weekly_data_raw.empty:
        st.info("データがロードされていないため、Gainグラフを表示できません。")
    else:
        ALL_PLOT_PERIODS_KEYS_ORDER = NEW_PERIODS + YEARS_TO_CALCULATE_STR
        tabs = st.tabs(ALL_PLOT_PERIODS_KEYS_ORDER)

        for i, period_label in enumerate(ALL_PLOT_PERIODS_KEYS_ORDER):
            with tabs[i]:
                plot_data_raw = pd.DataFrame()
                if period_label in NEW_PERIODS:
                    plot_data_raw = filter_data_by_period(weekly_data_raw, period_label)
                else:
                    target_year = int(period_label)
                    start_date_of_year = datetime(target_year, 1, 1).date()
                    plot_data_raw = weekly_data_raw[
                        weekly_data_raw.index.date >= start_date_of_year
                    ].copy()
                plot_tickers_in_data = [t for t in selected_plot_tickers_gain if t in plot_data_raw.columns]
                if plot_tickers_in_data and not plot_data_raw.empty and plot_data_raw.shape[0] >= 2:
                    plot_data_raw = plot_data_raw[plot_tickers_in_data].copy()                    
                    extracted_normalized = calculate_gain_data(plot_data_raw)                    
                    if not extracted_normalized.empty:
                        create_and_display_charts(
                            extracted_normalized,
                            period_label,
                            y_min_gain,
                            y_max_gain,
                            is_gain_chart=True,
                            auto_scale=st.session_state["autoscale_enabled_gain"],
                            chart_container=st
                        )
                    else:
                        st.info(f"選択された銘柄について「{period_label}」の有効な始値データがない、またはデータ期間が短すぎます。")
                else:
                    st.info(f"選択された銘柄について「{period_label}」の有効なデータがありませんでした。")