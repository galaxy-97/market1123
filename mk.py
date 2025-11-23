

import time
import json


def get_trader_state(group):
    """从group的trader_state字段中读取现有的trader_state字典"""
    trader_state = json.loads(group.trader_state)
    if 'bids' not in trader_state:
        trader_state['bids'] = []
    if 'asks' not in trader_state:
        trader_state['asks'] = []
    if 'trades' not in trader_state:
        trader_state['trades'] = []
    trader_state_hisoty = json.loads(group.trader_state_history)
    if 'bids' not in trader_state_hisoty:
        trader_state_hisoty['bids'] = []
    if 'asks' not in trader_state_hisoty:
        trader_state_hisoty['asks'] = []
    if 'trades' not in trader_state_hisoty:
        trader_state_hisoty['trades'] = []

    return trader_state,trader_state_hisoty


def update_trader_state(trader_state,trader_state_hisoty, data):
    """根据is_bid值将数据添加到bids或asks列表中，并排序"""
    if data['payload']['is_bid']:
        trader_state['bids'].append(data['payload'])

        trader_state_hisoty['bids'].append(data['payload'])
    else:
        trader_state['asks'].append(data['payload'])

        trader_state_hisoty['asks'].append(data['payload'])

    # 对bids和asks列表排序
    trader_state['bids'].sort(key=lambda x: (-x['price'], int(x['timestamp'])))
    trader_state['asks'].sort(key=lambda x: (x['price'], int(x['timestamp'])))


    # 对bids和asks列表排序
    trader_state_hisoty['bids'].sort(key=lambda x: (-x['price'], int(x['timestamp'])))
    trader_state_hisoty['asks'].sort(key=lambda x: (x['price'], int(x['timestamp'])))


def match_trades(trader_state,trader_state_hisoty,tis):
    import time
    """进行交易匹配，并将结果写入trades列表"""
    bids = trader_state['bids']
    asks = trader_state['asks']
    trades = trader_state['trades']
    trades_hisoty = trader_state_hisoty['trades']

    messages = ""
    messagess = ""
    # 使用索引遍历 bids 和 asks
    i = 0
    while i < len(bids):
        j = 0
        while j < len(asks):
            bid = bids[i]
            ask = asks[j]

            # 检查价格和资产类型是否匹配
            if bid['price'] >= ask['price'] and bid['asset_name'] == ask['asset_name']:
                trade_price = ask['price']

                # 判断较早的订单并选择交易价格
                if bid['timestamp'] <= ask['timestamp']:
                    trade_price = bid['price']  # 使用较早的买单价格
                    bid_type = bid['type']  # 获取买单类型
                    ask_type = ask['type']  # 获取卖单类型
                else:
                    trade_price = ask['price']  # 使用较早的卖单价格
                    bid_type = bid['type']  # 获取买单类型
                    ask_type = ask['type']  # 获取卖单类型

                # 确定交易类型
                if bid_type == 'taker' or ask_type == 'taker':
                    trade_type = 'taker'  # 如果有一个是taker
                else:
                    trade_type = 'maker'  # 如果两个都是maker

                # 创建交易记录
                trade = {
                    'buyer_id': bid['pcode'],
                    'seller_id': ask['pcode'],
                    'bid_id':bid['order_id'],
                        'ask_id':ask['order_id'],
                'price': trade_price,
                    'volume': 1,
                    'asset_name': ask['asset_name'],
                    'timestamp': time.time()-tis,  # 当前时间戳
                    'type': trade_type  # 设置交易类型为taker或maker
                }

                trades.append(trade)
                trades_hisoty.append(trade)
                # 移除匹配成功的订单
                bids.pop(i)
                asks.pop(j)

                # 重置索引 i 和 j 以继续从头匹配
                i = 0
                j = 0
                return bid, ask
            else:
                j += 1  # 检查下一个 ask

        i += 1  # 检查下一个 bid




    return messages, messagess

# if ask['pcode'] == payload['pcode'] and
import json
def is_valid_bid_ask(trader_state, payload,settled_cash=0,settled_assets={}):

    # 解析 settled_assets 字符串为字典
    if isinstance(settled_assets, str):
        try:
            settled_assets = json.loads(settled_assets)  # 将字符串解析为字典
        except json.JSONDecodeError:
            print("Error decoding settled_assets")
            return 999

    # 统计payload['pcode'] 的所有bids的总金额
    def calculate_total_bids(pcode):
        total_bids = sum(bid['price'] for bid in trader_state['bids'] if bid['pcode'] == pcode)
        return total_bids

    # 统计payload['pcode'] 的所有asks的类型次数
    # 统计当前用户的所有asks的次数
    def calculate_total_asks_for_user(pcode, asset_name):
        total_asks = sum(1 for ask in trader_state['asks'] if ask['pcode'] == pcode and ask['asset_name'] == asset_name and not ask['is_bid'])
        return total_asks

    # 计算当前用户的成功交易次数
    # def calculate_trade_count_for_user(pcode, trader_state):
    #     trade_count = 0
    #     for trade in trader_state['trades']:
    #         if trade['buyer_id'] == pcode:
    #             trade_count += 1
    #         if trade['seller_id'] == pcode:
    #             trade_count -= 1  # 如果是卖家，减少已成功的交易次数
    #     return trade_count

    def calculate_trade_count_for_user(pcode, trader_state, asset_name):
        trade_count = 0
        for trade in trader_state['trades']:
            # 区分资产类型
            if trade['asset_name'] == asset_name:
                if trade['buyer_id'] == pcode:
                    trade_count += 1  # 买方交易次数加一
                elif trade['seller_id'] == pcode:
                    trade_count -= 1  # 卖方交易次数减一
        return trade_count
    total_temp=0
    for trade in trader_state['trades']:
        # 区分资产类型
        if trade['buyer_id'] == payload['pcode']:
            total_temp+= trade['price']
        elif trade['seller_id'] == payload['pcode']:
            total_temp-= trade['price']
    settled_cash=str(float(settled_cash)-total_temp)

    """检查进价与出价是否合法"""
    if payload['is_bid']:
        for ask in trader_state['asks']:
            # 增加对 asset_name 的检查
            if ask['pcode'] == payload['pcode'] and ask['asset_name'] == payload['asset_name'] and float(
                    payload['price']) >= float(ask['price']):
                return 1
        # 统计bids金额，判断是否超过settled_cash
        total_bids = calculate_total_bids(payload['pcode'])
        if float(total_bids) + float(payload['price']) > float(settled_cash):
            return 3  # 超过总金额限制

    else:
        for bid in trader_state['bids']:
            # 增加对 asset_name 的检查
            if bid['pcode'] == payload['pcode'] and bid['asset_name'] == payload['asset_name'] and float(
                    payload['price']) <= float(bid['price']):
                return 2
            # 调试输出查看payload['asset_name'] 和 settled_assets内容

        # 统计当前用户在该资产类型下的asks次数，判断是否超过settled_assets限制
        total_asks = calculate_total_asks_for_user(payload['pcode'], payload['asset_name'])
        trade_count = calculate_trade_count_for_user(payload['pcode'], trader_state, payload['asset_name'])

        # 调试输出查看 payload['asset_name'] 和 settled_assets 内容
        print(f"Checking asset_name: {payload['asset_name']}, settled_assets: {settled_assets}")

        if payload['asset_name'] in settled_assets:
            adjusted_asks = total_asks - trade_count  # 调整后的 asks 数量
            print(f"Adjusted asks count for {payload['asset_name']}: {adjusted_asks}")

            if adjusted_asks >= settled_assets[payload['asset_name']]:
                return 4  # 超过 asks 类型次数限制
    return 999


def remove_order(trader_state,trader_state_hisoty, payload):
    """从 trader_state 中移除对应的出价或询价"""
    order_id = payload['order_id']

    if payload['is_bid']:
        # 移除对应的出价
        trader_state['bids'] = [
            bid for bid in trader_state['bids'] if bid['order_id'] != order_id

        ]
    else:
        # 移除对应的询价
        trader_state['asks'] = [
            ask for ask in trader_state['asks'] if ask['order_id'] != order_id
        ]


    if payload['is_bid']:
        for bid in trader_state_hisoty['bids']:
            if bid['order_id'] == order_id:
                bid['type'] = 'inactive'
                break
    else:
        for ask in trader_state_hisoty['asks']:
            if ask['order_id'] == order_id:
                ask['type'] = 'inactive'
                break



def process_trade(trader_state,trader_state_hisoty, payload, player):
    """处理用户确认的交易"""
    bids = trader_state['bids']
    trades = trader_state['trades']
    trades_hisoty=trader_state_hisoty['trades']

    # 找到匹配的bid和ask
    matching_bid = None

    # 在bids中找到对应的order
    for bid in bids:
        if bid['order_id'] == payload['order_id']:
            matching_bid = bid
            break

    if matching_bid:
        trade_price = matching_bid['price']

        trade = {
            'buyer_id': player.id_in_group,
            'seller_id': matching_bid['pcode'],
            'price': trade_price,
            'volume': 1,
            'asset_name': matching_bid['asset_name'],
            'timestamp': time.time()-player.time
        }
        trades.append(trade)
        trades_hisoty.append(trade)

        # 移除已完成的bid和ask
        if matching_bid['volume'] == 0:
            bids.remove(matching_bid)
        trades.sort(key=lambda x: (int(x['timestamp'])))
        trades_hisoty.sort(key=lambda x: (int(x['timestamp'])))
        # 通知交易双方
        return {
            int(matching_bid['pcode']): {"chanel": 'messages',
                                         "data": f"你已成功以价格 {trade_price} 购买了"},
            int(player.id_in_group): {"chanel": 'messages',
                                      "data": f"你已成功以价格 {trade_price} 卖出了"}
        }

    # 如果匹配不成功，返回错误信息
    return {
        payload['pcode']: {"chanel": 'messages', "data": "交易匹配失败，可能对方已经取消了订单"}
    }