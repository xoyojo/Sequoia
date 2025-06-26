"""
低回撤稳步上涨策略
"""

import logging


# 低回撤稳步上涨策略
def check(code_name, data, end_date=None, threshold=60):
    """
    检查股票是否符合低回撤稳步上涨策略（期间涨幅超60%且无大幅回撤）
    :param code_name: 股票代码_名称 ('301565', '中仑新材')
    :param data: 股票数据
    :param end_date: 检查日期
    :param threshold: 检查天数
    :return: 是否符合策略 Bool
    """
    # 筛选出 data 中 日期 小于等于 end_date 的数据。
    if end_date is not None:
        mask = data["日期"] <= end_date
        data = data.loc[mask]
    data = data.tail(n=threshold)

    if len(data) < threshold:
        logging.debug("{0}:样本小于{1}天...\n".format(code_name, threshold))
        return False

    # 期间涨幅
    ratio_increase = (data.iloc[-1]["收盘"] - data.iloc[0]["收盘"]) / data.iloc[0][
        "收盘"
    ]
    if ratio_increase < 0.6:
        return False

    # 不允许有吸盘，允许有一次“洗盘”
    for i in range(1, len(data)):
        # 单日跌幅超7%；高开低走7%；两日累计跌幅10%；两日高开低走累计10%
        if (
            data.iloc[i - 1]["p_change"] < -7
            or (data.iloc[i]["收盘"] - data.iloc[i]["开盘"])
            / data.iloc[i]["开盘"]
            * 100
            < -7
            or data.iloc[i - 1]["p_change"] + data.iloc[i]["p_change"] < -10
            or (data.iloc[i]["收盘"] - data.iloc[i - 1]["开盘"])
            / data.iloc[i - 1]["开盘"]
            * 100
            < -10
        ):
            return False

    return True
