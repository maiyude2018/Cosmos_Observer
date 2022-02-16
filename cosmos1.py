# -*- coding: utf-8 -*-
import requests, time
import base64
import hashlib

#从hash获得交易详细信息
def get_commos_tx(b):
    url_hash="https://api.cosmos.network/txs/%s"
    hash = hashlib.sha256(b).hexdigest().upper()
    #print("hash",hash)
    r=requests.get(url_hash % hash)
    return r.json()

#从区块高度获得交易信息
def re_tx_height(height):
    error = False
    url_height = 'https://api.cosmos.network/txs?tx.height=%s'
    r = requests.get(url_height % str(height))
    try:
        get_error = r.json()['error']
        print(get_error)
        error = True
    except:
        pass
    if 'txs' in r.json() and error == False:
        return r.json()
    else:
        tx_data=[]
        url_height = "https://api.cosmos.network/blocks/%s"
        r = requests.get(url_height % str(height))
        txs = r.json()["block"]["data"]["txs"]
        for w in txs:
            b = base64.b64decode(w)
            if b"MsgUndelegate" in b or b"MsgDelegate" in b or b"MsgBeginRedelegate" in b:#代理信息
                get_tx = get_commos_tx(b)
                tx_data.append(get_tx)
        rjson={"txs":tx_data}
        #print(rjson)
        return rjson


block_height = 9423375
#block_height = 9423436
#block_height = 9448381

block_count = 0
t0 = time.time()


while True:
    try:
        print(block_height)
        r = re_tx_height(block_height)
        #print(r)
        # 如果区块里有txs信息
        if 'txs' in r:
            txs = r['txs']
            for tx in txs:
                # print(tx)
                status = True
                if "failed" in tx['raw_log']:
                    status = False
                height = tx['height']
                # print("height %s" % height)
                txhash = tx['txhash']
                # print("hash %s" % txhash)
                msgs = tx['tx']['value']['msg']
                for msg in msgs:
                    if msg['type'] == "cosmos-sdk/MsgDelegate" and status == True:
                        print(msg['type'][14:])       # Delegate
                        print("hash %s" % txhash)
                        delegator_address = msg["value"]["delegator_address"]
                        validator_address = msg["value"]["validator_address"]
                        amount = msg["value"]["amount"]["amount"]
                        print(delegator_address, "to", validator_address, amount)
                    elif msg['type'] == "cosmos-sdk/MsgUndelegate" and status == True:
                        print(msg['type'][14:])          # Undelegate
                        print("hash %s" % txhash)
                        delegator_address = msg["value"]["delegator_address"]
                        validator_address = msg["value"]["validator_address"]
                        amount = msg["value"]["amount"]["amount"]
                        print(delegator_address, "to", validator_address, amount)
                    elif msg['type'] == "cosmos-sdk/MsgBeginRedelegate" and status == True:
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
