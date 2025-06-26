"""
【停机坪】策略
形态特征（技术面）​​
- ​​窄幅横盘震荡​​
股价在相对低位或中期调整后，进入小幅波动区间（如±3%以内），形成类似“停机坪”的横盘走势，时间通常持续5-15个交易日。
均线系统逐渐粘合（如5日、10日、20日均线），表明短期成本趋于一致。
​​成交量萎缩​​
横盘期间成交量明显缩小（地量），说明抛压减轻，市场观望情绪浓厚，为变盘信号。
​​关键支撑位稳固​​
股价不跌破前期重要支撑（如箱体下沿、趋势线或筹码密集区），显示主力资金控盘。
"""

import logging
from strategy import turtle_trade


# “停机坪”策略
def check(code_name, data, end_date=None, threshold=15):
    origin_data = data

    if end_date is not None:
        mask = data["日期"] <= end_date
        data = data.loc[mask]

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return

    data = data.tail(n=threshold)

    flag = False

    # 找出涨停日
    for index, row in data.iterrows():
        try:
            if float(row["p_change"]) > 9.5:
                if turtle_trade.check_enter(
                    code_name, origin_data, row["日期"], threshold
                ):
                    if check_internal(code_name, data, row):
                        flag = True
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    return flag


def check_internal(code_name, data, limitup_row):
    limitup_price = limitup_row["收盘"]
    limitup_end = data.loc[(data["日期"] > limitup_row["日期"])]
    limitup_end = limitup_end.head(n=3)
    if len(limitup_end.index) < 3:
        return False

    consolidation_day1 = limitup_end.iloc[0]
    consolidation_day23 = limitup_end = limitup_end.tail(n=2)

    if not (
        consolidation_day1["收盘"] > limitup_price
        and consolidation_day1["开盘"] > limitup_price
        and 0.97 < consolidation_day1["收盘"] / consolidation_day1["开盘"] < 1.03
    ):
        return False

    threshold_price = limitup_end.iloc[-1]["收盘"]

    for index, row in consolidation_day23.iterrows():
        try:
            if not (
                0.97 < (row["收盘"] / row["开盘"]) < 1.03
                and -5 < row["p_change"] < 5
                and row["收盘"] > limitup_price
                and row["开盘"] > limitup_price
            ):
                return False
        except KeyError as error:
            logging.debug("{}处理异常：{}".format(code_name, error))

    logging.debug("股票{0} 涨停日期：{1}".format(code_name, limitup_row["日期"]))

    return True
