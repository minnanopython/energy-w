import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import altair as alt
import datetime
from datetime import timedelta, date
from pandas.tseries.offsets import MonthEnd, MonthBegin
# --------------------------------------------------------------------------------------
# タイトルと枠組み
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Comparison",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)
st.markdown("# 📈 Energy Stock")
# --------------------------------------------------------------------------------------
# 銘柄と分析データを統合した設定
# --------------------------------------------------------------------------------------
DEFAULT_SECTOR = "総合商社"
SECTOR_DATA = {
    "総合商社": {
        '8058.T': {'name': '三菱商事', 'valuation': '割安', 'rating': '中立', 'comment': '三菱グループ中核。総合商社大手。エネルギー関連に強み。機械、化学や食品も。'},
        '8031.T': {'name': '三井物産', 'valuation': '割安', 'rating': '買い', 'comment': '総合商社の名門。鉄鉱石、原油の生産権益量、インフラで強力。海外も収益源。'},
        '8001.T': {'name': '伊藤忠商事', 'valuation': '割安', 'rating': '買い', 'comment': '総合商社大手。非資源事業が主力。中国ビジネスに強み。傘下にファミマなど。'},
        '8053.T': {'name': '住友商事', 'valuation': '割安', 'rating': '買い', 'comment': '住友系の総合商社。油井管・鋼管、金属取引等に強み。資源は非鉄が主。'},
        '8002.T': {'name': '丸紅', 'valuation': '割安', 'rating': '買い', 'comment': '芙蓉グループの総合商社。穀物、紙パ、エネルギー、プラント、輸送機、農化学に強み。'},
        '8015.T': {'name': '豊田通商', 'valuation': '割高', 'rating': '買い', 'comment': 'トヨタ系総合商社。金属・自動車に強み。機械・エネルギー・化学品も。アフリカに進出。'},
        '2768.T': {'name': '双日', 'valuation': '割安', 'rating': '買い', 'comment': '総合商社。ニチメン、日商岩井が母体。自動車、資源、肥料主力。航空機に強み。'},
        '8020.T': {'name': '兼松', 'valuation': '割安', 'rating': '買い', 'comment': '総合商社から専門商社にシフト。電子、食糧、鉄鋼・プラント、車両・航空が柱。'},
    },
    "エネルギー資源": {
        '5020.T': {'name': 'ＥＮＥＯＳＨＤ', 'valuation': '割安', 'rating': '買い', 'comment': '石油元売り最大手。東燃ゼネラルと統合。金属、石油・天然ガス開発にも強み。'},
        '5019.T': {'name': '出光興産', 'valuation': '割安', 'rating': '買い', 'comment': '石油精製元売り大手。石油化学に強み。豪州石炭権益も。昭和シェルと統合。'},
        '5021.T': {'name': 'コスモエネルギーＨＤ', 'valuation': '割安', 'rating': '買い', 'comment': '石油元売り大手。石油化学、石油開発、再生エネルギーなど多角。岩谷産業系。'},
        '1605.T': {'name': 'ＩＮＰＥＸ', 'valuation': '割高', 'rating': '買い', 'comment': '資源開発最大手。原油・ガス開発生産。政府が黄金株保有。豪でLNG。'},
        '1662.T': {'name': '石油資源開発', 'valuation': '割安', 'rating': '中立', 'comment': '資源開発大手。原油・天然ガスの探鉱、開発、生産。カナダ・オイルサンド事業終結。'},
        '1515.T': {'name': '日鉄鉱業', 'valuation': '－－', 'rating': '－－', 'comment': '鉄鋼向け石灰石が主柱。銅精鉱、電気銅も。海外採鉱拡大。日本製鉄系。'},
    },
    "主要電力": {
        '9509.T': {'name': '北海道電力', 'valuation': '割高', 'rating': '中立', 'comment': '原子力と石炭火力が主力。需要は冬ピーク。原発3基が停止、再稼働目指す。'},
        '9506.T': {'name': '東北電力', 'valuation': '割安', 'rating': '買い', 'comment': '東北圏7県に供給。震災で原発停止。風力発電に積極。ガス卸売りも。'},
        '9501.T': {'name': '東京電力ＨＤ', 'valuation': '割高', 'rating': '売り', 'comment': '福島原発事故の賠償、廃炉の負担重く。一時公的管理下に。発送電分離。'},
        '9502.T': {'name': '中部電力', 'valuation': '－－', 'rating': '買い', 'comment': '電力大手。中部財界の重鎮。浜岡原発3基停止中。火力発電は東電と統合。'},
        '9503.T': {'name': '関西電力', 'valuation': '－－', 'rating': '売り', 'comment': '東電と並ぶ業界の雄。原発依存度高いが代替電源確保へ。情報通信も。'},
        '9505.T': {'name': '北陸電力', 'valuation': '割安', 'rating': '中立', 'comment': '北陸３県に供給。石炭火力が主体で水力比率も大。志賀原発２基が停止。'},
        '9504.T': {'name': '中国電力', 'valuation': '－－', 'rating': '中立', 'comment': '瀬戸内に電源集中。石炭火力比率大。島根原発3号機建設、上関原発は中断。'},
        '9507.T': {'name': '四国電力', 'valuation': '割安', 'rating': '買い', 'comment': '瀬戸内に電源集中。原子力と石炭火力の比重高い。情報通信など多角化。'},
        '9508.T': {'name': '九州電力', 'valuation': '割安', 'rating': '買い', 'comment': '全国の離島発電が集中。原発3基稼働で玄海2基は廃炉。通信に意欲的。'},
        '9511.T': {'name': '沖縄電力', 'valuation': '－－', 'rating': '中立', 'comment': '沖縄本島と周辺37島に電力供給。石炭と石油火力が主力。LNGを拡大へ。'},
        '9513.T': {'name': '電源開発', 'valuation': '割高', 'rating': '中立', 'comment': '電力各社への電力卸。石炭火力と水力が電源。大間原発の建設停滞。'},
    },
    "電力電設": {
        '1934.T': {'name': 'ユアテック', 'valuation': '割高', 'rating': '強気', 'comment': '東北電力系総合電気工事で依存度4割。情報通信・再エネ発電工事に実績。'},
        '1942.T': {'name': '関電工', 'valuation': '割高', 'rating': '買い', 'comment': '東電系電気工事大手で依存度約3割。太陽光、水力発電事業、防災関連も。'},
        '1946.T': {'name': 'トーエネック', 'valuation': '割高', 'rating': '－－', 'comment': '電気工事大手。中部電系で依存度約4割。配電工事に強み。一般工事を強化。'},
        '1944.T': {'name': 'きんでん', 'valuation': '割高', 'rating': '買い', 'comment': '電設工事でトップ級。関電系で依存度約2割。情報通信工事など全国展開。'},
        '1930.T': {'name': '北陸電気工事', 'valuation': '割安', 'rating': '－－', 'comment': '北陸電力系。全国展開志向で北陸電力向け配電線は低下。公共工事強化。'},
        '1941.T': {'name': '中電工', 'valuation': '割安', 'rating': '－－', 'comment': '中国電力系で依存度約3割。電気工事主体。総資産の投資有価証券が大。'},
        '1959.T': {'name': '九電工', 'valuation': '割高', 'rating': '買い', 'comment': '九電系の電気工事会社で依存度2割弱。電気設備・空調管・通信一体施工。'},
        '1939.T': {'name': '四電工', 'valuation': '割安', 'rating': '売り', 'comment': '四国電力系で連携緊密。配電や計装、空調工事が主力。メガソーラー事業も。'},
    },
    "電設工事": {
        '1417.T': {'name': 'ミライト・ワン', 'valuation': '割安', 'rating': '強気', 'comment': '通信工事大手。NTT向け中心。ゼネコン西武建設を買収。社会インフラ、デジタル化も。'},
        '1721.T': {'name': 'コムシスＨＤ', 'valuation': '割安', 'rating': '中立', 'comment': '電気通信工事で首位。日本コムシス中核、NTT向けが過半。携帯各社の工事も。'},
        '1951.T': {'name': 'エクシオグループ', 'valuation': '割安', 'rating': '中立', 'comment': '電気通信工事大手。NTT向けに強み。グループで情報インフラ、DX支援、ITサービス。'},
        '1945.T': {'name': '東京エネシス', 'valuation': '割高', 'rating': '売り', 'comment': '発電所の関連設備エンジニアリング。東電関連が中心。再生可能エネ機器設備も。'},
        '1950.T': {'name': '日本電設工業', 'valuation': '割安', 'rating': '－－', 'comment': '鉄道電気工事で首位。JR東日本が筆頭株主。電気・通信工事を総合化'},
        '1938.T': {'name': '日本リーテック', 'valuation': '割安', 'rating': '－－', 'comment': '総合電気設備工事会社。鉄道に強くJR東へ依存大。電力・通信向けも展開。'},
    }
}
SECTORS = {sector: {ticker: data['name'] for ticker, data in stocks.items()} for sector, stocks in SECTOR_DATA.items()}
ALL_STOCKS_MAP = {ticker: data['name'] for sector in SECTOR_DATA.values() for ticker, data in sector.items()}
ALL_TICKERS_WITH_N225 = list(set(list(ALL_STOCKS_MAP.keys()) + ['^N225']))
def get_stock_name(ticker_code):
    if ticker_code == '^N225':
        return "日経平均"
    return ALL_STOCKS_MAP.get(ticker_code, ticker_code)
# --------------------------------------------------------------------------------------
# データ取得、キャッシュ、騰落率の計算を行う関数
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=True, ttl=timedelta(minutes=30))
def load_daily_data_cached(tickers_list, yf_period_str):
    """OHLCVデータを取得しキャッシュする関数 (日次、6y) """
    if not tickers_list:
        return pd.DataFrame()
    unique_tickers = list(set(tickers_list))
    try:
        tickers_obj = yf.Tickers(unique_tickers)
        data = tickers_obj.history(period="6y", interval="1d", auto_adjust=True)
        if len(unique_tickers) == 1 and 'Close' in data.columns:
            data.columns.name = 'Variable'
            data.columns = pd.MultiIndex.from_product([data.columns, unique_tickers], names=['Variable', 'Ticker'])
        return data.dropna(axis=0, how='all')
    except yf.exceptions.YFRateLimitError as e:
        raise e
    except Exception as e:
        st.error(f"yfinanceデータ取得エラー (日次): {e}")
        return pd.DataFrame()
@st.cache_data(show_spinner=True, ttl=timedelta(hours=6))
def load_all_data_cached(tickers_list):
    """週次終値データを取得しキャッシュする関数 (週次、6y) """
    if not tickers_list:
        return pd.DataFrame()
    unique_tickers = list(set(tickers_list))
    try:
        tickers_obj = yf.Tickers(unique_tickers)
        data = tickers_obj.history(period="6y", interval="1wk", auto_adjust=True)
        if 'Close' in data.columns.get_level_values(0):
            data_close = data["Close"]
        elif len(unique_tickers) == 1 and 'Close' in data.columns:
            data_close = data["Close"].to_frame(name=unique_tickers[0])
        else:
            return pd.DataFrame(index=pd.to_datetime([]), columns=unique_tickers)
    except yf.exceptions.YFRateLimitError as e:
        raise e
    except Exception as e:
        st.error(f"yfinanceデータ取得エラー (週次): {e}")
        return pd.DataFrame()
    return data_close.dropna(axis=0, how='all').sort_index()
@st.cache_data(show_spinner=False, ttl=timedelta(hours=6))
def load_ticker_financials_cached(ticker_list):
    """財務指標を取得しキャッシュする関数"""
    financials = {}
    if not ticker_list:
        return {}
    stock_tickers = [t for t in ticker_list if t != '^N225']
    for ticker in stock_tickers:
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            per = info.get('forwardPE')
            pbr = info.get('priceToBook')
            eps = info.get('trailingEps')
            roe = info.get('returnOnEquity')
            if roe is not None:
                roe *= 100
            roa = info.get('returnOnAssets')
            if roa is not None:
                roa *= 100
            market_cap = info.get('marketCap')
            beta = info.get('beta')
            dividend_yield = info.get('dividendYield')
            financials[ticker] = {
                "PER": per,
                "PBR": pbr,
                "EPS": eps,
                "ROE": roe,
                "ROA": roa,
                "配当": dividend_yield,
            }
        except Exception:
            financials[ticker] = {
                "PER": None,
                "PBR": None,
                "EPS": None,
                "ROE": None,
                "ROA": None,
                "配当": None, 
            }
    return financials
# --------------------------------------------------------------------------------------
# データ取得、キャッシュの実行
# --------------------------------------------------------------------------------------
data_raw_5y = pd.DataFrame()
daily_data_ohlcv = pd.DataFrame()
ALL_FINANCIALS = {}
try:
    with st.spinner(f"週次データをロード中..."):
        data_raw_5y = load_all_data_cached(ALL_TICKERS_WITH_N225)
    with st.spinner(f"日次データをロード中..."):
        daily_data_ohlcv = load_daily_data_cached(ALL_TICKERS_WITH_N225, "5y") 
    with st.spinner("財務指標 (予想PER, PBR, EPS, ROE, ROA) をロード中..."):
        ALL_FINANCIALS = load_ticker_financials_cached(list(ALL_STOCKS_MAP.keys())) 
    if data_raw_5y.empty:
        pass
    if daily_data_ohlcv.empty:
        st.warning("日次データがロードできませんでした。騰落率の計算ができません。")
except yf.exceptions.YFRateLimitError:
    st.warning("YFinanceの接続制限が発生しています。しばらくしてから再試行してください。")
    load_all_data_cached.clear()
    load_daily_data_cached.clear()
    load_ticker_financials_cached.clear()
    st.stop()
except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
    st.stop()
if not daily_data_ohlcv.empty and isinstance(daily_data_ohlcv.columns, pd.MultiIndex):
    daily_data_for_table = daily_data_ohlcv['Close'].ffill()
else:
    daily_data_for_table = daily_data_ohlcv.copy() 
# --------------------------------------------------------------------------------------
# 騰落率の計算を行う関数
# --------------------------------------------------------------------------------------
def calculate_gains(daily_data: pd.DataFrame, days: int) -> pd.Series:
    """
    騰落率を計算する関数 (n営業日前からの騰落率)
    """
    if daily_data.empty:
        return pd.Series(dtype=float)
    daily_price_data = daily_data.copy()
    latest_prices = daily_price_data.iloc[-1].ffill()
    if len(daily_price_data) > days:
        previous_prices = daily_price_data.iloc[-(days + 1)].ffill()
    elif len(daily_price_data) > 0 and days >= 1:
        previous_prices = daily_price_data.iloc[0].ffill()
    else:
        return pd.Series(0, index=daily_price_data.columns) 
    gains = ((latest_prices - previous_prices) / previous_prices) * 100
    return gains.dropna()
def calculate_period_gain(daily_data: pd.DataFrame, start_date_str: str, end_date_str: str) -> pd.Series:
    """
    指定された開始日と終了日の間の騰落率を計算する関数 (期間内の最初と最後の営業日の終値を使用)
    """
    if daily_data.empty:
        return pd.Series(dtype=float)
    daily_price_data = daily_data.copy()
    try:
        start_price_series = daily_price_data.loc[:start_date_str].iloc[-1]
        end_price_series = daily_price_data.loc[:end_date_str].iloc[-1] 
        valid_tickers = start_price_series.index.intersection(end_price_series.index)
        start_price = start_price_series[valid_tickers]
        end_price = end_price_series[valid_tickers] 
        valid_for_calc = (start_price.notna()) & (end_price.notna()) & (start_price != 0)
        start_price_calc = start_price[valid_for_calc]
        end_price_calc = end_price[valid_for_calc] 
        gains = ((end_price_calc - start_price_calc) / start_price_calc) * 100
        full_gains = pd.Series(np.nan, index=daily_price_data.columns)
        full_gains.update(gains)
        return full_gains
    except IndexError:
        return pd.Series(np.nan, index=daily_price_data.columns)
    except Exception:
        return pd.Series(np.nan, index=daily_price_data.columns)
def calculate_past_year_gain(daily_data: pd.DataFrame, end_date_str: str, years: int) -> pd.Series:
    """
    指定された終了日 (end_date_str) から、years年さかのぼった日を始点とする期間の騰落率を計算する関数。
    """
    if daily_data.empty or years <= 0:
        return pd.Series(dtype=float)
    try:
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        start_date = end_date - timedelta(days=365.25 * years)
        start_date_str = start_date.strftime("%Y-%m-%d")
        return calculate_period_gain(daily_data, start_date_str, end_date_str)
    except Exception:
        return pd.Series(np.nan, index=daily_data.columns)
def calculate_monthly_gain(daily_data: pd.DataFrame, year: int, month: int) -> pd.Series:
    """
    指定された年月の月次騰落率を計算する関数 (月の初めの営業日と、月の終わりの営業日を使用)
    """
    if daily_data.empty:
        return pd.Series(dtype=float)
    daily_price_data = daily_data.copy()
    first_day_of_month = date(year, month, 1)
    last_day_of_month = (first_day_of_month + MonthEnd(0)).date() 
    try:
        start_price_series = daily_price_data.loc[str(first_day_of_month):].iloc[0]
        end_price_series = daily_price_data.loc[:str(last_day_of_month)].iloc[-1] 
        valid_tickers = start_price_series.index.intersection(end_price_series.index)
        start_price = start_price_series[valid_tickers]
        end_price = end_price_series[valid_tickers] 
        valid_for_calc = (start_price.notna()) & (end_price.notna()) & (start_price != 0)
        start_price_calc = start_price[valid_for_calc]
        end_price_calc = end_price[valid_for_calc] 
        gains = ((end_price_calc - start_price_calc) / start_price_calc) * 100
        full_gains = pd.Series(np.nan, index=daily_price_data.columns)
        full_gains.update(gains)
        return full_gains
    except IndexError:
        return pd.Series(np.nan, index=daily_price_data.columns)
    except Exception:
        return pd.Series(np.nan, index=daily_price_data.columns)
def calculate_ytd_gain(daily_data: pd.DataFrame, year: int) -> pd.Series:
    """
    指定された年の年初来騰落率を計算する関数 (その年の1月1日の最初の営業日から現在までの騰落率)
    """
    start_date_str = f"{year}-01-01"
    end_date_str = daily_data.index[-1].strftime("%Y-%m-%d")
    return calculate_period_gain(daily_data, start_date_str, end_date_str)
def calculate_daily_returns_df(daily_price_data: pd.DataFrame) -> pd.DataFrame:
    if daily_price_data.empty:
        return pd.DataFrame()
    df_price = daily_price_data.copy()
    df_returns = df_price.pct_change() * 100
    return df_returns.dropna(how='all').iloc[-750:]
def color_gain(val):
    """騰落率に色を付ける関数"""
    if pd.isna(val) or val == '-':
        return ''
    try:
        val = float(val)
        color = '#008000' if val >= 0 else '#C70025'
        return f'color: {color}'
    except ValueError:
        return ''
# --------------------------------------------------------------------------------------
# 選択ウィジェットの配置
# --------------------------------------------------------------------------------------
def reset_stock_selection():
    st.session_state["_stock_selection_needs_reset"] = True
col_select_sector, col_select_stock = st.columns([1, 4])
with col_select_sector:
    st.markdown("セクター")
    sector_options = list(SECTORS.keys())
    default_sector_key = DEFAULT_SECTOR
    default_sectors = st.session_state.get("multiselect_sectors", [default_sector_key])
    selected_sectors = st.multiselect(
        "セクターを選択",
        options=sector_options,
        default=default_sectors,
        key="multiselect_sectors",
        label_visibility="collapsed",
        on_change=reset_stock_selection
    )
SELECTED_SECTOR_STOCKS_MAP = {}
if selected_sectors:
    for sector in selected_sectors:
        SELECTED_SECTOR_STOCKS_MAP.update(SECTORS.get(sector, {}))
else:
    SELECTED_SECTOR_STOCKS_MAP = ALL_STOCKS_MAP
stock_options = [name for name in SELECTED_SECTOR_STOCKS_MAP.values()]
all_current_stock_names = stock_options
if "multiselect_stocks" not in st.session_state:
    st.session_state["multiselect_stocks"] = all_current_stock_names
elif st.session_state.get("_stock_selection_needs_reset"):
    st.session_state["multiselect_stocks"] = all_current_stock_names
    del st.session_state["_stock_selection_needs_reset"]
else:
    current_selection = st.session_state["multiselect_stocks"]
    st.session_state["multiselect_stocks"] = [name for name in current_selection if name in all_current_stock_names]
with col_select_stock:
    st.markdown("銘柄")
    selected_stock_names = st.multiselect(
        "銘柄を選択",
        options=all_current_stock_names,
        key="multiselect_stocks",
        label_visibility="collapsed"
    )
FINAL_STOCKS_MAP = {}
name_to_ticker = {name: ticker for ticker, name in SELECTED_SECTOR_STOCKS_MAP.items()}
for name in selected_stock_names:
    ticker = name_to_ticker.get(name)
    if ticker:
        FINAL_STOCKS_MAP[ticker] = name
SELECTED_STOCKS_MAP = FINAL_STOCKS_MAP
selected_plot_tickers = list(SELECTED_STOCKS_MAP.keys())
""
# --------------------------------------------------------------------------------------
# Stockテーブルの配置
# --------------------------------------------------------------------------------------
PERIOD_1_START = "2025-10-03"
PERIOD_1_END = "2025-10-06"
PERIOD_2_START = "2025-10-17"
PERIOD_2_END = "2025-10-20"
gain_period1 = calculate_period_gain(daily_data_for_table, PERIOD_1_START, PERIOD_1_END)
gain_period2 = calculate_period_gain(daily_data_for_table, PERIOD_2_START, PERIOD_2_END)
END_DATE_FOR_PAST_GAIN = PERIOD_2_END
gain_1y = calculate_past_year_gain(daily_data_for_table, END_DATE_FOR_PAST_GAIN, 1)
gain_3y = calculate_past_year_gain(daily_data_for_table, END_DATE_FOR_PAST_GAIN, 3)
if not gain_period1.empty:
    gain_period1 = pd.to_numeric(gain_period1, errors='coerce')
if not gain_period2.empty:
    gain_period2 = pd.to_numeric(gain_period2, errors='coerce')
if not gain_1y.empty:
    gain_1y = pd.to_numeric(gain_1y, errors='coerce')
if not gain_3y.empty:
    gain_3y = pd.to_numeric(gain_3y, errors='coerce')
FILTERED_STOCKS = SELECTED_STOCKS_MAP
end_prices = daily_data_for_table.iloc[-1].ffill()
STOCK_DIVIDEND_MAP = {}
for ticker, data in ALL_FINANCIALS.items():
    STOCK_DIVIDEND_MAP[ticker] = data.get("配当")
analysis_results = []
if FILTERED_STOCKS:
    ALL_ANALYSIS_DATA = {t: d for sector in SECTOR_DATA.values() for t, d in sector.items()}
    for ticker, name in FILTERED_STOCKS.items():
        analysis_data = ALL_ANALYSIS_DATA.get(ticker, {})
        financial_data = ALL_FINANCIALS.get(ticker, {})
        current_price = end_prices.get(ticker)
        gain_p1 = gain_period1.get(ticker) if ticker in gain_period1.index else np.nan
        gain_p2 = gain_period2.get(ticker) if ticker in gain_period2.index else np.nan
        gain_y1 = gain_1y.get(ticker) if ticker in gain_1y.index else np.nan
        gain_y3 = gain_3y.get(ticker) if ticker in gain_3y.index else np.nan        
        def get_numeric_value_for_sort(data, default=np.nan):
            value = financial_data.get(data)
            if value is None or (isinstance(value, str) and value in ('-', 'N/A', '情報なし', 'nan')):
                 return np.nan
            try:
                return pd.to_numeric(value, errors='coerce')
            except:
                return np.nan        
        row = {
            "コード": ticker.replace(".T", ""),
            "銘柄名": name,
            "株価": current_price,
            "配当": get_numeric_value_for_sort("配当"),
            "10/6": gain_p1,
            "10/20": gain_p2,
            "1y": gain_y1,
            "3y": gain_y3,
            "valuation": analysis_data.get('valuation', 'N/A'),
            "rating": analysis_data.get('rating', 'N/A'),
            "予想PER": get_numeric_value_for_sort("PER"),
            "PBR": get_numeric_value_for_sort("PBR"),
            "EPS": get_numeric_value_for_sort("EPS"),
            "ROE": get_numeric_value_for_sort("ROE"),
            "ROA": get_numeric_value_for_sort("ROA"),
            "comment": analysis_data.get('comment', '情報なし'),
        }
        analysis_results.append(row)         
    if analysis_results:
        df_analysis = pd.DataFrame(analysis_results)
        numeric_cols_to_fill = [
            "株価", "配当", "10/6", "10/20", "1y", "3y",
            "予想PER", "PBR", "EPS", "ROE", "ROA"
        ]
        df_analysis[numeric_cols_to_fill] = df_analysis[numeric_cols_to_fill].fillna(0)
        num_rows = df_analysis.shape[0]
        ROW_HEIGHT = 35
        HEADER_HEIGHT = 38
        MAX_HEIGHT = 550
        calculated_height = HEADER_HEIGHT + (num_rows * ROW_HEIGHT)
        table_height = min(calculated_height, MAX_HEIGHT)        
        column_config_analysis = {
            "株価": st.column_config.NumberColumn("株価", format="%.2f"),
            "配当": st.column_config.NumberColumn("配当", format="%.2f"),
            "10/6": st.column_config.NumberColumn("10/6", format="%.2f"),
            "10/20": st.column_config.NumberColumn("10/20", format="%.2f"),
            "1y": st.column_config.NumberColumn("1y", format="%.2f"),
            "3y": st.column_config.NumberColumn("3y", format="%.2f"),
            "予想PER": st.column_config.NumberColumn("予想PER", format="%.2f"),
            "PBR": st.column_config.NumberColumn("PBR", format="%.2f"),
            "EPS": st.column_config.NumberColumn("EPS", format="%,.2f"), 
            "ROE": st.column_config.NumberColumn("ROE", format="%.2f"),
            "ROA": st.column_config.NumberColumn("ROA", format="%.2f"),
            "valuation": st.column_config.Column("Valuation"), 
            "rating": st.column_config.Column("Rating"),
            "comment": st.column_config.Column("コメント"),
        }         
        display_columns = [
            "コード", "銘柄名", "株価", "配当", "10/6", "10/20",
            "1y", "3y",
            "valuation", "rating", "予想PER", "PBR", "EPS", "ROE", "ROA", "comment"
        ]         
        st.dataframe(
            data=df_analysis[display_columns],
            height=table_height,
            column_config=column_config_analysis,
            hide_index=True
        )
    else:
        st.info("選択された銘柄の分析データがありませんでした。")
elif not selected_sectors:
    st.info("セクターを選択してください。")
else:
    st.info("表示可能な銘柄がありませんでした。")
# --------------------------------------------------------------------------------------
# 📊 Daily Gain
# --------------------------------------------------------------------------------------
st.markdown(f"## 📊 Daily Gain")   
daily_returns_df = calculate_daily_returns_df(daily_data_for_table)
if 'daily_returns_df' in locals() and not daily_returns_df.empty and FILTERED_STOCKS:
    df_daily_returns_1mo = daily_returns_df.tail(20) 
    current_tickers_t3 = ['^N225'] + list(FILTERED_STOCKS.keys()) 
    plot_daily_returns_1mo = df_daily_returns_1mo[[
        t for t in current_tickers_t3 if t in df_daily_returns_1mo.columns
    ]].copy()    
    if not plot_daily_returns_1mo.empty:
        df_daily_gains_T = plot_daily_returns_1mo.T
        df_daily_gains_T['コード'] = df_daily_gains_T.index.str.replace(".T", "")
        df_daily_gains_T['銘柄名'] = df_daily_gains_T.index.map(get_stock_name)      
        all_date_cols = [col for col in df_daily_gains_T.columns if col not in ['コード', '銘柄名']]
        cols = ['コード', '銘柄名'] + all_date_cols
        df_daily_gains_display = df_daily_gains_T[cols].copy()      
        date_cols = df_daily_gains_display.columns[2:]
        date_format = "%m/%d"
        df_daily_gains_display.columns = ['コード', '銘柄名'] + [d.strftime(date_format) for d in date_cols]
        formatted_date_cols = df_daily_gains_display.columns[2:].tolist()
        format_dict = {col: "{:.2f}" for col in formatted_date_cols}      
        styled_daily_gains = df_daily_gains_display.style.map(color_gain, subset=formatted_date_cols).format(
            format_dict
        ).set_properties(**{'text-align': 'right'}, subset=formatted_date_cols)       
        num_rows = df_daily_gains_display.shape[0]
        ROW_HEIGHT = 35 
        HEADER_HEIGHT = 38 
        MAX_HEIGHT = 550
        calculated_height = HEADER_HEIGHT + (num_rows * ROW_HEIGHT)
        table_height = min(calculated_height, MAX_HEIGHT)        
        st.dataframe(
            data=styled_daily_gains,
            height=table_height,
            width='stretch', 
            hide_index=True,
        )
    else:
        st.info("日ごとの騰落率 (1ヶ月分) を表示するためのデータが不足しています。")
else:
    st.info("日次データまたは選択銘柄が不足しています。")
# --------------------------------------------------------------------------------------
# 棒グラフの描画
# --------------------------------------------------------------------------------------
def create_and_display_bar_charts(daily_returns_data, filtered_stocks, selected_period_key, y_min_daily_gain=None, y_max_daily_gain=None):
    current_plot_tickers = [t for t in filtered_stocks.keys() if t in daily_returns_data.columns and t != '^N225']
    if daily_returns_data.empty or not current_plot_tickers:
        st.info(f"日ごとの騰落率グラフを表示するためのデータがありません。")
        return
    num_cols = 1
    y_domain = [y_min_daily_gain, y_max_daily_gain] if y_min_daily_gain is not None and y_max_daily_gain is not None else 'unaggregated'     
    for row_i in range((len(current_plot_tickers) + num_cols - 1) // num_cols):
        cols = st.columns(num_cols)
        for col_i in range(num_cols):
            idx = row_i * num_cols + col_i
            if idx < len(current_plot_tickers):
                ticker = current_plot_tickers[idx]
                stock_name = ticker[:4] + " " + get_stock_name(ticker)
                plot_df = daily_returns_data[[ticker]].tail(750).reset_index()
                plot_df.columns = ['Date', 'Daily_Return']
                plot_df['Color'] = plot_df['Daily_Return'].apply(lambda x: 'Positive' if x >= 0 else 'Negative')               
                x_format = "%m/%d"
                chart = alt.Chart(plot_df).mark_bar().encode(
                    alt.X("Date:T", axis=alt.Axis(
                        title=None,
                        format=x_format,
                        labelAngle=0
                    )),
                    alt.Y("Daily_Return:Q", axis=alt.Axis(title=None, format="+.0f"),
                        scale=alt.Scale(domain=y_domain)
                    ),
                    alt.Color('Color:N',
                              scale=alt.Scale(domain=['Positive', 'Negative'], range=['#008000', '#C70025']),
                              legend=None),
                    tooltip=[
                        alt.Tooltip("Date:T", title="日付", format="%m/%d"),
                        alt.Tooltip("Daily_Return:Q", title="騰落率", format="+.2f")
                    ]
                ).properties(
                    title=f"{stock_name}",
                    height=250,
                    width='container'
                )
                cell = cols[col_i].container(border=False)
                cell.altair_chart(chart, width='stretch')
# --------------------------------------------------------------------------------------
# 棒グラフの配置
# --------------------------------------------------------------------------------------
if "show_daily_returns_bar_chart" not in st.session_state:
    st.session_state["show_daily_returns_bar_chart"] = False
def get_radio_index(options_list, session_state_key):
    try:
        current_value = st.session_state.get(session_state_key)
        if current_value is None:
            return 0
        return options_list.index(current_value)
    except ValueError:
        return 0
def update_gain_value(radio_key, target_state_key):
    st.session_state[target_state_key] = st.session_state[radio_key]
MAX_GAINS_DAILY = [+1, +3, +5, +10, +15, +20]
MIN_GAINS_DAILY = [-1, -3, -5, -10, -15, -20]
MAX_OPTIONS_DAILY = [f"{g:+.0f}" for g in MAX_GAINS_DAILY]
MIN_OPTIONS_DAILY = [f"{g:.0f}" for g in MIN_GAINS_DAILY]
def find_closest_option(target_value, options_list_float):
    """目標値に最も近いオプションの値（float）を見つける"""
    if not options_list_float:
        return None
    abs_diff = np.abs(np.array(options_list_float) - target_value)
    closest_index = np.argmin(abs_diff)
    return options_list_float[closest_index]
df_daily_returns = calculate_daily_returns_df(daily_data_for_table)
if not df_daily_returns.empty and FILTERED_STOCKS:
    current_tickers = list(FILTERED_STOCKS.keys())
    plot_daily_returns = df_daily_returns[[t for t in current_tickers if t in df_daily_returns.columns]].copy()
    plot_daily_returns_filtered = plot_daily_returns.drop(columns=['^N225'], errors='ignore')
    if not plot_daily_returns_filtered.empty:
        col_header_toggle, col_header_charts, col_header_spacer = st.columns([2, 32.5, 0.1])
        with col_header_toggle:
            current_chart_state = st.session_state["show_daily_returns_bar_chart"]
            if current_chart_state:
                button_label = "ー"
                new_state = False
            else:
                button_label = "＋"
                new_state = True
            def toggle_chart_visibility():
                st.session_state["show_daily_returns_bar_chart"] = new_state
            st.button(
                button_label,
                key="toggle_daily_chart_button",
                on_click=toggle_chart_visibility,
                help="日次騰落率棒グラフの表示/非表示を切り替えます",
            )       
        if st.session_state["show_daily_returns_bar_chart"]:
            col_charts_daily, col_daily, col_controls_daily = st.columns([32, 0.1, 2.5])
            
            y_min_daily_calc = plot_daily_returns_filtered.min().min()
            y_max_daily_calc = plot_daily_returns_filtered.max().max()
            
            if not pd.isna(y_min_daily_calc) and not pd.isna(y_max_daily_calc):
                y_min_auto = y_min_daily_calc - 0.5
                y_max_auto = y_max_daily_calc + 0.5
            else:
                y_min_auto, y_max_auto = None, None
            
            with col_controls_daily:
                autoscale_daily_enabled = st.checkbox(
                    "目盛",
                    value=st.session_state.get("autoscale_daily_enabled", True),
                    key="autoscale_daily_checkbox"
                )
                st.session_state["autoscale_daily_enabled"] = autoscale_daily_enabled
                
                if not autoscale_daily_enabled:
                    with st.markdown("**最大目盛 (上限)**"):
                        max_default_value_float = MAX_GAINS_DAILY[0]
                        if y_max_auto is not None:
                            closest_max_float = find_closest_option(max(0.1, y_max_auto), MAX_GAINS_DAILY)
                            max_default_value_float = closest_max_float
                        
                        max_default_value = f"{max_default_value_float:+.0f}"
                        if "selected_max_daily_gain_value" not in st.session_state or st.session_state["selected_max_daily_gain_value"].replace('+', '') not in [opt.replace('+', '') for opt in MAX_OPTIONS_DAILY]:
                            st.session_state["selected_max_daily_gain_value"] = max_default_value
                        
                        max_radio_key_daily = "radio_y_max_gain_daily"
                        max_default_index_daily = get_radio_index(MAX_OPTIONS_DAILY, "selected_max_daily_gain_value")
                        
                        st.radio(
                            "最大目盛",
                            options=MAX_OPTIONS_DAILY,
                            index=max_default_index_daily if max_default_index_daily is not None else 0,
                            key=max_radio_key_daily,
                            on_change=lambda: update_gain_value(max_radio_key_daily, "selected_max_daily_gain_value"),
                            label_visibility="collapsed"
                        )
                    
                    selected_max_text_daily = st.session_state["selected_max_daily_gain_value"]
                    y_max_daily_gain_set = float(selected_max_text_daily.replace('+', ''))
                    
                    with st.markdown("**最小目盛 (下限)**"):
                        min_default_value_float = MIN_GAINS_DAILY[0]
                        if y_min_auto is not None:
                            closest_min_float = find_closest_option(min(-0.1, y_min_auto), MIN_GAINS_DAILY)
                            min_default_value_float = closest_min_float
                        
                        min_default_value = f"{min_default_value_float:.0f}"
                        if "selected_min_daily_gain_value" not in st.session_state or st.session_state["selected_min_daily_gain_value"].replace('+', '') not in [opt.replace('+', '') for opt in MIN_OPTIONS_DAILY]:
                            st.session_state["selected_min_daily_gain_value"] = min_default_value
                        
                        min_radio_key_daily = "radio_y_min_gain_daily"
                        min_default_index_daily = get_radio_index(MIN_OPTIONS_DAILY, "selected_min_daily_gain_value")
                        
                        st.radio(
                            "最小目盛",
                            options=MIN_OPTIONS_DAILY,
                            index=min_default_index_daily if min_default_index_daily is not None else 0,
                            key=min_radio_key_daily,
                            on_change=lambda: update_gain_value(min_radio_key_daily, "selected_min_daily_gain_value"),
                            label_visibility="collapsed"
                        )
                    
                    selected_min_text_daily = st.session_state["selected_min_daily_gain_value"]
                    y_min_daily_gain_set = float(selected_min_text_daily)
                else:
                    y_min_daily_gain_set = y_min_auto
                    y_max_daily_gain_set = y_max_auto
                
                if y_min_daily_gain_set is not None and y_max_daily_gain_set is not None and y_min_daily_gain_set >= y_max_daily_gain_set:
                    y_min_daily_gain_set = y_min_auto
                    y_max_daily_gain_set = y_max_auto
                    st.session_state["autoscale_daily_checkbox"] = True
                    st.session_state["autoscale_daily_enabled"] = True
                    st.warning("⚠️ 日次目盛が不正です。オートスケールに切り替えます。")            
            with col_charts_daily:
                filtered_stocks_only = {k: v for k, v in FILTERED_STOCKS.items() if k != '^N225'}
                create_and_display_bar_charts(
                    plot_daily_returns_filtered,
                    filtered_stocks_only,
                    "1ヶ月",
                    y_min_daily_gain_set,
                    y_max_daily_gain_set
                )
    else:
        st.info("日ごとの騰落率棒グラフを表示するためのデータが不足しています。")
elif daily_data_for_table.empty:
    pass
else:
    pass
""
# --------------------------------------------------------------------------------------
# 📈 Monthly Gain
# --------------------------------------------------------------------------------------
st.markdown("## 📈 Monthly Gain")
CURRENT_DATE = datetime.date.today()
CURRENT_YEAR = CURRENT_DATE.year
CURRENT_MONTH = CURRENT_DATE.month
MONTH_GAINS = {}
ALL_GAIN_KEYS = {}
monthly_gain_keys = []
for i in range(12):
    target_month = CURRENT_MONTH - (11 - i)
    target_year = CURRENT_YEAR     
    while target_month <= 0:
        target_month += 12
        target_year -= 1
    while target_month > 12:
        target_month -= 12
        target_year += 1
    year = target_year
    month = target_month     
    month_key = f"{year}{month:02}"     
    if month_key not in MONTH_GAINS:
        MONTH_GAINS[month_key] = calculate_monthly_gain(daily_data_for_table, year, month)
        ALL_GAIN_KEYS[month_key] = MONTH_GAINS[month_key]         
    monthly_gain_keys.append(month_key)
YEAR_2025 = 2025
YEAR_2023 = 2023
YEAR_2021 = 2021
YEARS_TO_CALCULATE_STR = [str(y) for y in sorted(list(set([YEAR_2025, YEAR_2023, YEAR_2021])), reverse=True)]
YEAR_GAINS = {}
for year_str in YEARS_TO_CALCULATE_STR:
    year = int(year_str)
    YEAR_GAINS[year_str] = calculate_ytd_gain(daily_data_for_table, year)
    ALL_GAIN_KEYS[year_str] = YEAR_GAINS[year_str]
FINAL_GAIN_KEYS_ORDER = monthly_gain_keys + YEARS_TO_CALCULATE_STR
display_tickers_t2 = ['^N225'] + list(FILTERED_STOCKS.keys())
results_t2 = []
if daily_data_for_table.empty:
    st.info(f"有効な日次データが取得できませんでした。")
elif display_tickers_t2:
    for ticker in display_tickers_t2:
        name = get_stock_name(ticker)
        stock_code = ticker.replace(".T", "")
        row = {
            "コード": stock_code,
            "銘柄名": name,
        }
        for key in FINAL_GAIN_KEYS_ORDER:
            gain_series = ALL_GAIN_KEYS.get(key)
            if gain_series is not None:
                row[key] = gain_series.get(ticker)
            else:
                row[key] = None
        results_t2.append(row)
    if results_t2:
        df_table2 = pd.DataFrame(results_t2)
        gain_cols_t2 = FINAL_GAIN_KEYS_ORDER
        df_table2_final = df_table2.copy()
        for col in gain_cols_t2:
            df_table2_final[col] = pd.to_numeric(df_table2_final[col], errors='coerce')
        dynamic_column_config = {
            "コード": st.column_config.TextColumn(width="small"),
            "銘柄名": st.column_config.TextColumn(width="small"),
        }
        for col in gain_cols_t2:
            dynamic_column_config[col] = st.column_config.NumberColumn(label=f"{col}", format="%.2f", width="small")
        num_rows = df_table2_final.shape[0]
        ROW_HEIGHT = 35
        HEADER_HEIGHT = 38
        MAX_HEIGHT = 550
        calculated_height = HEADER_HEIGHT + (num_rows * ROW_HEIGHT)
        table_height = min(calculated_height, MAX_HEIGHT)
        st.dataframe(
            data=df_table2_final,
            height=table_height,
            column_config=dynamic_column_config,
            hide_index=True
        )
    else:
        st.info("表示可能な銘柄がありませんでした。")
elif not selected_sectors:
    st.info("セクターを選択してください。")
else:
    st.info("表示可能な銘柄がありませんでした。")
""
# --------------------------------------------------------------------------------------
# 折れ線グラフの描画
# --------------------------------------------------------------------------------------
num_cols = 4
def filter_data_by_period(data_raw_5y: pd.DataFrame, period_label: str) -> pd.DataFrame:
    if data_raw_5y.empty:
        return pd.DataFrame()
    end_date = data_raw_5y.index.max() 
    if period_label == "1ヶ月":
        start_date = end_date - timedelta(days=31)
    elif period_label == "3ヶ月":
        start_date = end_date - timedelta(weeks=13)
    elif period_label == "6ヶ月":
        start_date = end_date - timedelta(weeks=26)
    elif period_label == "9ヶ月":
        start_date = end_date - timedelta(weeks=39)
    elif period_label == "1年":
        start_date = end_date - timedelta(weeks=52)
    elif period_label == "3年":
        start_date = end_date - timedelta(weeks=52 * 3)
    else:
        return pd.DataFrame() 
    return data_raw_5y[data_raw_5y.index >= start_date]
def create_and_display_charts(normalized_data, period_label, y_min_gain, y_max_gain, auto_scale=False):
    current_plot_tickers = [t for t in normalized_data.columns if t != '^N225'] 
    if normalized_data.empty or current_plot_tickers == []:
        st.info(f"{period_label}のグラフを表示するためのデータがありません。") 
        return 
    if auto_scale:
        min_ratio = normalized_data.min().min() 
        max_ratio = normalized_data.max().max() 
        buffer = (max_ratio - min_ratio) * 0.1
        y_domain = [max(0.0, min_ratio - buffer), max_ratio + buffer]
    else:
        y_min_ratio = 1.0 + y_min_gain / 100.0
        y_max_ratio = 1.0 + y_max_gain / 100.0
        if y_min_ratio >= y_max_ratio:
            st.warning("⚠️ 最小目盛が最大目盛以上です。Y軸の範囲を±10%に設定しました。")
            y_domain = [1.0 - 0.10, 1.0 + 0.10] 
        else:
            y_domain = [y_min_ratio, y_max_ratio] 
    has_nikkei = '^N225' in normalized_data.columns
    nikkei_data = pd.DataFrame()
    if has_nikkei:
        nikkei_data = normalized_data[['^N225']].rename(columns={'^N225': 'Price'}).copy()
        nikkei_data['Date'] = nikkei_data.index
        nikkei_data['z_index'] = 0 
    date_range = normalized_data.index.max() - normalized_data.index.min()
    tick_count_val = 'auto'
    if period_label == "1ヶ月":
        x_format = "%m/%d"
        tick_count_val = 15
    elif date_range.days <= 400:
        x_format = "%m/%d"
        tick_count_val = 'month' 
    else:
        x_format = "%Y"
        tick_count_val = 'year' 

    y_axis_config = alt.Axis( 
        title=None,
        labelExpr="datum.value == 1 ? '0.0%' : format((datum.value - 1) * 100, '+.1f') + '%'"
    )
    for row_i in range((len(current_plot_tickers) + num_cols - 1) // num_cols):
        cols = st.columns(num_cols)
        for col_i in range(num_cols):
            idx = row_i * num_cols + col_i
            if idx < len(current_plot_tickers):
                ticker = current_plot_tickers[idx] 
                stock_data = pd.DataFrame({
                    "Date": normalized_data.index,
                    "Price": normalized_data[ticker],
                })
                stock_data['z_index'] = 1 
                combined_data = pd.concat([stock_data, nikkei_data]).dropna(subset=['Price'])          
                title_text = ticker[:4] + " " + get_stock_name(ticker) 
                base_chart = alt.Chart(combined_data).encode(
                    alt.X("Date:T", axis=alt.Axis(
                        format=x_format,
                        title=None,
                        labelAngle=0,
                        tickCount=tick_count_val
                    )),
                    alt.Y("Price:Q", 
                        scale=alt.Scale(zero=False, domain=y_domain),
                        axis=y_axis_config),
                ) 
                nikkei_line = alt.Chart(pd.DataFrame())
                if has_nikkei:
                    nikkei_line = base_chart.transform_filter(
                        alt.datum.z_index == 0
                    ).mark_line(
                        color="#A9A9A9",
                        strokeWidth=1.5
                    ).encode(
                        alt.Order("z_index:Q"),
                        tooltip=[
                            alt.Tooltip("Date:T", title="日付", format="%Y/%m/%d"),
                            alt.Tooltip("Price:Q", title="日経騰落率", 
                                        format='+0.2') 
                        ]
                    ) 
                stock_line = base_chart.transform_filter(
                    alt.datum.z_index == 1
                    ).mark_line(
                    color="#C70025",
                    strokeWidth=2
                    ).encode(
                    alt.Order("z_index:Q"),
                    tooltip=[
                        alt.Tooltip("Date:T", title="日付", format="%Y/%m/%d"),
                        alt.Tooltip("Price:Q", title=f"{title_text}騰落率", 
                                        format='+0.2')
                    ]
                    ) 
                chart = (
                    nikkei_line + stock_line
                ).properties(title=f"{title_text}", height=300, width='container')
                cell = cols[col_i].container(border=False)
                cell.altair_chart(chart, width='stretch')
# --------------------------------------------------------------------------------------
# 折れ線グラフの配置
# --------------------------------------------------------------------------------------
MIN_GAINS_FLAT = [-1, -3, -5, -7, -10, -12, -15, -20]
MAX_GAINS_FLAT = [+1, +3, +5, +7, +10, +12, +15, +20, 
                  +50, +70, +100, +200, +300, +500, +1000, +2000]
MIN_OPTIONS = [f"{g:.0f}" for g in MIN_GAINS_FLAT]
MAX_OPTIONS = [f"{g:+.0f}" for g in MAX_GAINS_FLAT]
def update_gain_value(key_to_check, key_to_update):
    current_value = st.session_state[key_to_check] 
    st.session_state[key_to_update] = current_value
def get_radio_index(options_list, key):
    selected_value = st.session_state.get(key)
    if selected_value is None:
        return 0        
    try:
        selected_numeric_str = selected_value.replace('+', '').replace('-', '') 
        options_numeric_str = [opt.replace('+', '').replace('-', '') for opt in options_list]        
        if selected_value in options_list:
             return options_list.index(selected_value)
        for i, opt_str in enumerate(options_numeric_str):
            if opt_str == selected_numeric_str:
                return i        
        return 0 
    except ValueError:
        return 0 
if "autoscale_enabled" not in st.session_state:
    st.session_state["autoscale_enabled"] = True
if "selected_max_gain_value" not in st.session_state:
    st.session_state["selected_max_gain_value"] = "+10"
if "selected_min_gain_value" not in st.session_state:
    st.session_state["selected_min_gain_value"] = "-10"
col_charts, col, col_controls = st.columns([32, 0.1, 2.5])
with col_controls:
    autoscale_enabled = st.checkbox(
        "目盛",
        value=st.session_state["autoscale_enabled"],
        key="autoscale_checkbox"
    )
    st.session_state["autoscale_enabled"] = autoscale_enabled
    if not autoscale_enabled:
        with st.markdown("**最大目盛 (上限)**"): 
            max_default_value = "+10"
            if st.session_state["selected_max_gain_value"].replace('+', '').replace('-', '') not in [opt.replace('+', '').replace('-', '') for opt in MAX_OPTIONS]:
                 st.session_state["selected_max_gain_value"] = max_default_value
            max_radio_key = "radio_y_max_gain_all"
            max_default_index = get_radio_index(MAX_OPTIONS, "selected_max_gain_value")        
            st.radio(
                "最大目盛",
                options=MAX_OPTIONS,
                index=max_default_index,
                key=max_radio_key,
                on_change=lambda: update_gain_value(max_radio_key, "selected_max_gain_value"),
                label_visibility="collapsed"
            )        
        selected_max_text = st.session_state["selected_max_gain_value"]
        y_max_gain = float(selected_max_text.replace('+', ''))         
        with st.markdown("**最小目盛 (下限)**"): 
            min_default_value = "-10"
            if st.session_state["selected_min_gain_value"].replace('+', '').replace('-', '') not in [opt.replace('+', '').replace('-', '') for opt in MIN_OPTIONS]:
                 st.session_state["selected_min_gain_value"] = min_default_value         
            min_radio_key = "radio_y_min_gain_all"
            min_default_index = get_radio_index(MIN_OPTIONS, "selected_min_gain_value")        
            st.radio(
                "最小目盛",
                options=MIN_OPTIONS,
                index=min_default_index,
                key=min_radio_key,
                on_change=lambda: update_gain_value(min_radio_key, "selected_min_gain_value"),
                label_visibility="collapsed"
            )        
        selected_min_text = st.session_state["selected_min_gain_value"]
        y_min_gain = float(selected_min_text)
    else:
        y_min_gain = -1.0
        y_max_gain = 1.0
CHART_Y_RANGE = {
    "1ヶ月": [y_min_gain, y_max_gain],
    "3ヶ月": [y_min_gain, y_max_gain],
    "6ヶ月": [y_min_gain, y_max_gain],
    "9ヶ月": [y_min_gain, y_max_gain],
    "1年": [y_min_gain, y_max_gain],
    "3年": [y_min_gain, y_max_gain],
    str(YEAR_2025): [y_min_gain, y_max_gain],
    str(YEAR_2023): [y_min_gain, y_max_gain],
    str(YEAR_2021): [y_min_gain, y_max_gain],
}
with col_charts:
    if not selected_plot_tickers:
        st.info("グラフに表示する銘柄を上記マルチセレクトで選択してください。")
    elif data_raw_5y.empty and daily_data_for_table.empty:
        st.info("データがロードされていないため、グラフを表示できません。")
    else:
        plot_tickers = selected_plot_tickers[:]
        if '^N225' in data_raw_5y.columns and '^N225' not in plot_tickers:
            plot_tickers.append('^N225') 
        FIXED_PLOT_PERIODS = {
            "1ヶ月": {"period": "1ヶ月", "y_range": CHART_Y_RANGE["1ヶ月"], "data_source": "weekly"}, 
            "3ヶ月": {"period": "3ヶ月", "y_range": CHART_Y_RANGE["3ヶ月"], "data_source": "weekly"},
            "6ヶ月": {"period": "6ヶ月", "y_range": CHART_Y_RANGE["6ヶ月"], "data_source": "weekly"},
            "9ヶ月": {"period": "9ヶ月", "y_range": CHART_Y_RANGE["9ヶ月"], "data_source": "weekly"},
            "1年": {"period": "1年", "y_range": CHART_Y_RANGE["1年"], "data_source": "weekly"},
            "3年": {"period": "3年", "y_range": CHART_Y_RANGE["3年"], "data_source": "weekly"},
        } 
        YEAR_PLOT_PERIODS = {
            str(YEAR_2025): {"period": str(YEAR_2025), "y_range": CHART_Y_RANGE[str(YEAR_2025)], "data_source": "year"},
            str(YEAR_2023): {"period": str(YEAR_2023), "y_range": CHART_Y_RANGE[str(YEAR_2023)], "data_source": "year"},
            str(YEAR_2021): {"period": str(YEAR_2021), "y_range": CHART_Y_RANGE[str(YEAR_2021)], "data_source": "year"},
        }
        ALL_PLOT_PERIODS_KEYS_ORDER = ["1ヶ月", "3ヶ月", "6ヶ月", "9ヶ月", "1年", "3年"] + YEARS_TO_CALCULATE_STR
        ALL_PLOT_PERIODS = {**FIXED_PLOT_PERIODS, **YEAR_PLOT_PERIODS}        
        tabs = st.tabs(ALL_PLOT_PERIODS_KEYS_ORDER)         
        for i, period_label in enumerate(ALL_PLOT_PERIODS_KEYS_ORDER):
            config = ALL_PLOT_PERIODS.get(period_label)
            if config is None:
                continue
            with tabs[i]:
                plot_data_raw = pd.DataFrame()                 
                if config["data_source"] == "weekly":
                    plot_data_raw = filter_data_by_period(data_raw_5y, config["period"])
                elif config["data_source"] == "year":
                    target_year = int(config["period"])
                    start_date_of_year = datetime.date(target_year, 1, 1)
                    plot_data_raw = data_raw_5y[
                        data_raw_5y.index.date >= start_date_of_year
                    ].copy()
                plot_tickers_in_data = [t for t in plot_tickers if t in plot_data_raw.columns]                 
                if plot_tickers_in_data and not plot_data_raw.empty and plot_data_raw.shape[0] >= 2:
                    plot_data_raw = plot_data_raw[plot_tickers_in_data].copy()                    
                    first_valid_index = plot_data_raw.first_valid_index()
                    if first_valid_index is not None:
                        first_valid_prices = plot_data_raw.loc[first_valid_index].copy()
                        plot_data_raw = plot_data_raw.loc[:, first_valid_prices.notna() & (first_valid_prices != 0)]
                        valid_first_prices = plot_data_raw.loc[first_valid_index]                        
                        if not valid_first_prices.empty and (valid_first_prices != 0).all():
                            extracted_normalized = plot_data_raw / valid_first_prices                            
                            y_min, y_max = config["y_range"] 
                            create_and_display_charts(
                                extracted_normalized, 
                                period_label, 
                                y_min, 
                                y_max,
                                auto_scale=st.session_state["autoscale_checkbox"]
                            )
                        else:
                            st.info(f"選択された銘柄について「{period_label}」の有効なデータがありませんでした。")
                    else:
                        st.info(f"選択された銘柄について「{period_label}」の有効なデータがありませんでした。")
                else:
                    st.info(f"選択された銘柄について「{period_label}」の有効なデータがありませんでした。")
# --------------------------------------------------------------------------------------
# ローソク足チャートの描画
# --------------------------------------------------------------------------------------
def create_and_display_candlestick_charts(ohlcv_data, filtered_stocks, period_label="6ヶ月"):
    """
    指定された期間のローソク足、日中変動幅、出来高チャートを縦に連結して表示する。
    """  
    current_plot_tickers = [t for t in filtered_stocks.keys() if t != '^N225']
    if ohlcv_data.empty or not current_plot_tickers:
        st.info(f"{period_label}のローソク足グラフを表示するためのデータがありません。")
        return
    df_ohlcv = ohlcv_data.tail(126).copy()
    if not isinstance(df_ohlcv.columns, pd.MultiIndex):
         st.info("OHLCVデータがMultiIndex形式ではありません。")
         return
    num_cols = 1 
    for row_i in range((len(current_plot_tickers) + num_cols - 1) // num_cols):
        cols = st.columns(num_cols)
        for col_i in range(num_cols):
            idx = row_i * num_cols + col_i
            if idx < len(current_plot_tickers):
                ticker = current_plot_tickers[idx] 
                stock_name = ticker[:4] + " " + get_stock_name(ticker)                 
                try:
                    df_plot = df_ohlcv.loc[:, (['Open', 'High', 'Low', 'Close', 'Volume'], ticker)].copy()
                    df_plot.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    df_plot.index.name = 'Date'
                    df_plot = df_plot.reset_index().dropna()                    
                except KeyError:
                    try:
                        if ticker in df_ohlcv.columns.get_level_values('Ticker'):
                             cols[col_i].info(f"{stock_name} ({ticker}) のOHLCVデータが不完全です。")
                        else:
                             cols[col_i].info(f"{stock_name} ({ticker}) のOHLCVデータが見つかりません。")
                        continue
                    except:
                        cols[col_i].info(f"{stock_name} ({ticker}) のOHLCVデータが見つかりません。")
                        continue
                if df_plot.empty:
                    cols[col_i].info(f"{stock_name} ({ticker}) のプロット可能なデータがありません。")
                    continue                    
                df_plot['Color'] = np.where(df_plot['Close'] > df_plot['Open'], 'Positive', 'Negative')
                df_plot['Daily_Range'] = df_plot['High'] - df_plot['Low']                
                candlestick_base = alt.Chart(df_plot).encode(
                    alt.X('Date:T', title=None, axis=alt.Axis(format="%m/%d", labelAngle=0))
                ).properties(title=f"{stock_name}", height=250)
                candlestick = candlestick_base.mark_bar().encode(
                    alt.Y('Open:Q', title='株価'),
                    alt.Y2('Close:Q'),
                    alt.Color('Color:N', scale=alt.Scale(domain=['Positive', 'Negative'], range=['#008000', '#C70025']), legend=None),
                    tooltip=[
                        alt.Tooltip('Date:T', title='日付', format="%m/%d"),
                        alt.Tooltip('Open:Q', title='始値', format=',.2f'),
                        alt.Tooltip('High:Q', title='高値', format=',.2f'),
                        alt.Tooltip('Low:Q', title='安値', format=',.2f'),
                        alt.Tooltip('Close:Q', title='終値', format=',.2f'),
                    ]
                )
                wick = candlestick_base.mark_rule().encode(
                    alt.Y('Low:Q'),
                    alt.Y2('High:Q'),
                    alt.Color('Color:N', scale=alt.Scale(domain=['Positive', 'Negative'], range=['#008000', '#C70025']), legend=None),
                )
                range_chart = alt.Chart(df_plot).mark_bar(opacity=0.4).encode(
                    alt.X('Date:T', title=None, axis=None), 
                    alt.Y('Daily_Range:Q', title='変動幅', axis=alt.Axis(titlePadding=5, format=',.1f')),
                    alt.Color('Color:N', scale=alt.Scale(domain=['Positive', 'Negative'], range=['#008000', '#C70025']), legend=None),
                    tooltip=[
                        alt.Tooltip('Date:T', title='日付', format="%m/%d"),
                        alt.Tooltip('Daily_Range:Q', title='日中変動幅', format=',.2f'),
                        alt.Tooltip('Color:N', title='終値-始値', format='')
                    ]
                ).properties(height=80)
                volume_chart = alt.Chart(df_plot).mark_bar(opacity=0.4).encode(
                    alt.X('Date:T', title=None, axis=None), 
                    alt.Y('Volume:Q', title='出来高', axis=alt.Axis(titlePadding=5, format=',d')), 
                    alt.Color('Color:N', scale=alt.Scale(domain=['Positive', 'Negative'], range=['#008000', '#C70025']), legend=None),
                    tooltip=[
                        alt.Tooltip('Date:T', title='日付', format="%m/%d"),
                        alt.Tooltip('Volume:Q', title='出来高', format=',d'),
                    ]
                ).properties(height=100)
                combined_ohlc = (candlestick + wick).encode(
                    alt.Y('Close:Q', scale=alt.Scale(zero=False))
                ).properties(height=250)
                chart = alt.VConcatChart(
                    vconcat=[
                        combined_ohlc,
                        range_chart,
                        volume_chart
                    ],
                ).resolve_scale(
                    x='shared',
                    y='independent'
                )
                cols[col_i].altair_chart(chart, width='stretch')
# --------------------------------------------------------------------------------------
# ローソク足チャートの配置
# --------------------------------------------------------------------------------------
if not daily_data_ohlcv.empty and FILTERED_STOCKS:
    st.markdown(f"## 📊 Daily Candlestick")
    filtered_stocks_only = {k: v for k, v in FILTERED_STOCKS.items() if k != '^N225'}
    create_and_display_candlestick_charts(
        daily_data_ohlcv,
        filtered_stocks_only, 
        period_label="6ヶ月"
    )
# --------------------------------------------------------------------------------------
# データダウンロード機能
# --------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("## 📥 Download Data")
if not daily_data_ohlcv.empty and isinstance(daily_data_ohlcv.columns, pd.MultiIndex):
    download_ohlcv_df = daily_data_ohlcv.stack(level=1, future_stack=True).rename_axis(index=['Date', 'Ticker']).reset_index()
    download_ohlcv_df = download_ohlcv_df[['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    csv_data_ohlcv = download_ohlcv_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="全日次株価データ (OHLCV) をCSVでダウンロード",
        data=csv_data_ohlcv,
        file_name='daily_stock_ohlcv.csv',
        mime='text/csv',
        help="高値(High)と安値(Low)を含む、全期間の始値、終値、出来高データです。"
    )
else:
    st.info("日次株価データ (OHLCV) が存在しないため、ダウンロードできません。")