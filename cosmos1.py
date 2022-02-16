# -*- coding: utf-8 -*-
import requests, time


#从区块高度获得交易信息
def re_tx_height(height):
    url_height = 'https://api.cosmos.network/txs?tx.height=%s'
    r = requests.get(url_height % str(height))
    # print(r.json())
    return r.json()


block_height = 9403396
block_count = 0
t0 = time.time()


while True:
    try:
        print(block_height)
        r = re_tx_height(block_height)
        # 如果区块里有txs信息
        if 'txs' in r:
            txs = r['txs']
            for tx in txs:
                # print(tx)
                height = tx['height']
                # print("height %s" % height)
                txhash = tx['txhash']
                # print("hash %s" % txhash)
                msgs = tx['tx']['value']['msg']
                for msg in msgs:
                    if msg['type'] == "cosmos-sdk/MsgDelegate":
                        print(msg['type'][14:])       # Delegate
                        print("hash %s" % txhash)
                        delegator_address = msg["value"]["delegator_address"]
                        validator_address = msg["value"]["validator_address"]
                        amount = msg["value"]["amount"]["amount"]
                        print(delegator_address, "to", validator_address, amount)
                    elif msg['type'] == "cosmos-sdk/MsgUndelegate":
                        print(msg['type'][14:])          # Undelegate
                        print("hash %s" % txhash)
                        delegator_address = msg["value"]["delegator_address"]
                        validator_address = msg["value"]["validator_address"]
                        amount = msg["value"]["amount"]["amount"]
                        print(delegator_address, "to", validator_address, amount)
                    elif msg['type'] == "cosmos-sdk/MsgBeginRedelegate":
                        print(msg['type'][14:])          # BeginRedelegate
                        print("hash %s" % txhash)
                        delegator_address = msg["value"]["delegator_address"]
                        validator_src_address = msg["value"]["validator_src_address"]
                        validator_dst_address = msg["value"]["validator_dst_address"]
                        amount = msg["value"]["amount"]["amount"]
                        print(delegator_address, validator_src_address,"-to-",validator_dst_address ,amount)

        block_height += 1
        block_count += 1

        # 结束区块高度
        # if block_height > 9403400:
        #     break
    except Exception as e:
        print('[ERROR] Exception occurred when parsing block %s !' % block_height)
        print(e)
        #block_height += 1
        block_count += 1
        time.sleep(2)


# 运行时间
running_time = time.time() - t0
print("Running time: ", time.time() - t0, "seconds")
print("Average time per block:", running_time / block_count, "seconds")
