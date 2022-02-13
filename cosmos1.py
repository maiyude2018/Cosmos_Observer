import requests,time
import base64
import hashlib

#从hash获得交易详细信息
def re_tx(b):
    url_hash="https://api.cosmos.network/txs/%s"
    hash = hashlib.sha256(b).hexdigest().upper()
    print("hash",hash)
    r=requests.get(url_hash % hash)
    return r.json()["tx"]


start_block=9403352
while True:
    try:
        url="https://api.cosmos.network/blocks/%s"
        print(start_block)
        r=requests.get(url % start_block)
        txs=r.json()["block"]["data"]["txs"]
        #print(txs)
        for w in txs:
            b = base64.b64decode(w)
            #print(b)
            if b"MsgUndelegate" in b:#取消代理信息
                print("Undelegate")
                tx=re_tx(b)
                msg = tx["value"]["msg"]
                for i in msg:
                    # print(i)
                    type = i["type"]
                    if type == "cosmos-sdk/MsgUndelegate":
                        delegator_address = i["value"]["delegator_address"]
                        validator_address = i["value"]["validator_address"]
                        amount = i["value"]["amount"]["amount"]
                        print(delegator_address, "to", validator_address, amount)
            if b"MsgDelegate" in b:#代理信息
                print("Delegate")
                tx = re_tx(b)
                msg=tx["value"]["msg"]
                for i in msg:
                    #print(i)
                    type=i["type"]
                    if type == "cosmos-sdk/MsgDelegate":
                        delegator_address=i["value"]["delegator_address"]
                        validator_address=i["value"]["validator_address"]
                        amount = i["value"]["amount"]["amount"]
                        print(delegator_address,"to",validator_address,amount)
            if b"MsgBeginRedelegate" in b:#Redelegate信息
                print("Redelegate")
                tx = re_tx(b)
                msg = tx["value"]["msg"]
                for i in msg:
                    #print(i)
                    type = i["type"]
                    if type == "cosmos-sdk/MsgBeginRedelegate":
                        delegator_address = i["value"]["delegator_address"]
                        validator_src_address = i["value"]["validator_src_address"]
                        validator_dst_address = i["value"]["validator_dst_address"]
                        amount = i["value"]["amount"]["amount"]
                        print(delegator_address, validator_src_address,"-to-",validator_dst_address ,amount)
        start_block += 1
    except Exception as e:
        print(e)
        time.sleep(2)
