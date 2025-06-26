# -*- encoding: UTF-8 -*-

import data_fetcher
import settings
import strategy.enter as enter
from strategy import turtle_trade, climax_limitdown
from strategy import backtrace_ma250
from strategy import breakthrough_platform
from strategy import parking_apron
from strategy import low_backtrace_increase
from strategy import keep_increasing
from strategy import high_tight_flag
import akshare as ak
import push
import logging
import time
import datetime
import pickle


def prepare():
    """
    数据准备
    """
    logging.info(
        "************************ process start ***************************************"
    )
    # all_data = ak.stock_zh_a_spot_em()
    # subset = all_data[["代码", "名称"]]
    # stocks = [tuple(x) for x in subset.values][:10]
    stocks = [
        ("301565", "中仑新材"),
        ("833943", "优机股份"),
        ("836871", "派特尔"),
        ("688201", "信安世纪"),
        ("300591", "万里马"),
        ("300635", "中达安"),
        ("301022", "海泰科"),
        ("301319", "唯特偶"),
    ]
    # statistics(all_data, stocks)

    strategies = {
        "放量上涨": enter.check_volume,
        "均线多头": keep_increasing.check,
        "停机坪": parking_apron.check,
        # "回踩年线": backtrace_ma250.check,
        # '突破平台': breakthrough_platform.check,
        "无大幅回撤": low_backtrace_increase.check,
        "海龟交易法则": turtle_trade.check_enter,
        "高而窄的旗形": high_tight_flag.check,
        "放量跌停": climax_limitdown.check,
    }

    if datetime.datetime.now().weekday() == 0:  # 周一
        strategies["均线多头"] = keep_increasing.check

    process(stocks, strategies)

    logging.info(
        "************************ process   end ***************************************"
    )


def process(stocks, strategies):
    """
    执行策略
    """
    # stocks_data = data_fetcher.run(stocks)
    # 将stock_data 存为dump
    with open("stock_data.pkl", "rb") as f:
        stocks_data = pickle.load(f)
    for strategy, strategy_func in strategies.items():
        check(stocks_data, strategy, strategy_func)
        time.sleep(2)


def check(stocks_data, strategy, strategy_func):
    """
    执行策略检查
    """
    end = settings.config["end_date"]
    m_filter = check_enter(end_date=end, strategy_fun=strategy_func)
    results = dict(filter(m_filter, stocks_data.items()))
    print(type(results))
    for i in results.keys():
        print(i)

    if len(results) > 0:
        push.strategy(
            '**************"{0}"**************\n{1}\n**************"{0}"**************\n'.format(
                strategy, list(results.keys())
            )
        )


def check_enter(end_date=None, strategy_fun=enter.check_volume):
    """
    检查策略
    """

    def end_date_filter(stock_data):
        if end_date is not None:
            if end_date < stock_data[1].iloc[0].日期:  # 该股票在end_date时还未上市
                logging.debug("{}在{}时还未上市".format(stock_data[0], end_date))
                return False
        return strategy_fun(stock_data[0], stock_data[1], end_date=end_date)

    return end_date_filter


# 统计数据
def statistics(all_data, stocks):
    limitup = len(all_data.loc[(all_data["涨跌幅"] >= 9.5)])
    limitdown = len(all_data.loc[(all_data["涨跌幅"] <= -9.5)])

    up5 = len(all_data.loc[(all_data["涨跌幅"] >= 5)])
    down5 = len(all_data.loc[(all_data["涨跌幅"] <= -5)])

    msg = "涨停数：{}   跌停数：{}\n涨幅大于5%数：{}  跌幅大于5%数：{}".format(
        limitup, limitdown, up5, down5
    )
    push.statistics(msg)
