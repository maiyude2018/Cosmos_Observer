# -*- coding: utf-8 -*-
import requests, time
import base64
import hashlib
import json
import traceback

def getAllPools():
    #伪代码，获取pools信息
    pools={"cosmosvaloper156gqf9837u7d4c4678yt3rl4ls9c5vuursrrzf": ['0x1234',"0x5678"],
    "cosmosvaloper1sjllsnramtg3ewxqwwrwjxfgc4n4ef9u2lcnj0": ['0x2134']
           }
    return pools

def accountBindMap(pid,delegator):
    # 伪代码，从合约获取evm地址
    adress = "0x0000000000000000000000000000000000000000"
    adress = "0x3d67A8926F097a1304eAF9Dc985fd00533Fa56C5"
    return adress

def getData_forcontract(pid, delegator_evm):
    #伪代码，从合约获取数据
    #todo 以下全是测试用数据
    info = {"pid": pid,"amount": 300000,"delegator_address": "0x3d67A8926F097a1304eAF9Dc985fd00533Fa56C5"}  # 绑定的evm地址
    if pid == "0x1234":
        info = {"pid": pid,  # 矿池地址
                "amount": 300000,  # staking数量
                "delegator_address": "0x3d67A8926F097a1304eAF9Dc985fd00533Fa56C5"}  # 绑定的evm地址
    elif pid == "0x5678":
        info = {"pid": pid,  # 矿池地址
                "amount": 300000,  # staking数量
                "delegator_address": "0x3d67A8926F097a1304eAF9Dc985fd00533Fa56C5"}  # 绑定的evm地址
    return info

#取消所有挖矿
def cancel_all_staking(validator_address,delegator,pools):
    if validator_address in pools.keys():  # 如果代理对象在walnut中
        # 取消所有挖矿
        for pid in pools[validator_address]:
            delegator_address_evm = accountBindMap(pid,delegator)
            contract_info = getData_forcontract(pid, delegator_address_evm)
            if contract_info["delegator_address"] == "0x0000000000000000000000000000000000000000":  # 没有绑定，不操作
                print("不操作")
                continue
            elif int(contract_info["amount"]) > 0:
                staking_info = {"delegator_address": contract_info["delegator_address"],"validator_address": validator_address, "pid": pid, "amount": 0}
                print("执行代理挖矿归零3", staking_info)


#从hash获得交易详细信息
def get_commos_tx(b):
    url_hash="https://api.cosmos.network/txs/%s"
    hash = hashlib.sha256(b).hexdigest().upper()
    #print("hash",hash)
    r=requests.get(url_hash % hash)
    return r.json()

#获取代理信息
def get_delegations(adress):
    url = 'https://api.cosmos.network/staking/delegators/%s/delegations'
    r = requests.get(url % adress)
    return r.json()["result"]

#从区块高度获得交易信息
def re_tx_height(height):
    error = False
    url_height = 'https://api.cosmos.network/txs?tx.height=%s'
    r = requests.get(url_height % str(height))
    try:
        get_error = r.json()['error']
        #print(get_error)
        error = True
    except:
        pass
    if 'txs' in r.json() and error == False:#检查是否空区块，是否错误
        return r.json()
    else:#遇到错误，换另一个api
        tx_data=[]
        url_height = "https://api.cosmos.network/blocks/%s"
        r = requests.get(url_height % str(height))
        txs = r.json()["block"]["data"]["txs"]
        for w in txs:
            b = base64.b64decode(w)
            if b"MsgUndelegate" in b or b"MsgDelegate" in b or b"MsgBeginRedelegate" in b:#代理相关信息
                get_tx = get_commos_tx(b)
                tx_data.append(get_tx)
        rjson={"txs":tx_data}
        #print(rjson)
        return rjson


block_height = 9448153
#block_height = 9423436
block_height = 9454476
#block_height = 9454482

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
                try:
                    code = tx["code"]
                    if code != 0:
                        status = False
                        continue
                except:
                    pass
                height = tx['height']
                # print("height %s" % height)
                txhash = tx['txhash']
                # print("hash %s" % txhash)
                msgs = tx['tx']['value']['msg']
                memo = tx['tx']['value']['memo']


                # 判断交易数量大于2，且含有转账和代理操作，含有memo
                if len(msgs) == 2 and "cosmos-sdk/MsgDelegate" in str(msgs) and "cosmos-sdk/MsgSend" in str(msgs) and len(memo) > 0:
                    check_send = False
                    check_delegate = False
                    check_memo = False

                    #检查memo格式是否合法
                    try:
                        memo = json.loads(memo)
                        #print(memo)
                        memo_pid=memo["pid"]
                        memo_delegator_address=memo["delegator_address"]
                        check_memo = True
                    except Exception as e:
                        check_memo = False

                    pools = getAllPools()

                    for lists in msgs:
                        #检查转账操作是否合法
                        if lists['type'] == "cosmos-sdk/MsgSend":
                            from_address = lists["value"]["from_address"]
                            to_address = lists["value"]["to_address"]
                            amount_send = lists["value"]["amount"][0]["amount"]
                            #print("send",from_address, to_address, amount_send)
                            if to_address == "cosmos1tg30qk7vwlddcwlr447xlf9dzmgcevslvnfqu4" and amount_send == "100":#检测转账对象以及数量是否正确
                                check_send = True
                        # 检查代理操作是否合法
                        elif lists['type'] == "cosmos-sdk/MsgDelegate":
                            delegator_address = lists["value"]["delegator_address"]
                            validator_address = lists["value"]["validator_address"]
                            amount_Delegate = lists["value"]["amount"]["amount"]
                            #print(delegator_address, "to", validator_address, amount_Delegate)
                            if validator_address in pools.keys()  :#检测代理对象是否在walnut合约列表中
                                check_delegate = True
                    #print(check_delegate, check_send, check_memo)

                    if check_send == True and check_delegate == True and check_memo == True:
                        #读取该用户代理到该节点的总量
                        delegations_data=get_delegations(delegator_address)
                        for data in delegations_data:
                            validator_address_in_data=data["delegation"]["validator_address"]
                            if validator_address_in_data == validator_address:
                                amount_validator = data["balance"]["amount"]
                        #用pid和用户id查询绑定情况
                        contract_info = getData_forcontract(memo_pid, memo_delegator_address)
                        if contract_info["delegator_address"] == "0x0000000000000000000000000000000000000000":#没有绑定，则直接代理挖矿
                            staking_info={"delegator_address":memo_delegator_address,"validator_address":validator_address,"pid":memo_pid,"amount":int(amount_validator)}
                            print("执行代理挖矿",staking_info)
                        elif contract_info["delegator_address"] == memo_delegator_address:#有绑定，且地址一致
                            if int(contract_info["amount"]) == int(amount_validator):#查询数量，一致无需更新
                                print("数量一致，无需更新",)
                            else:#不一致更新数量
                                staking_info = {"delegator_address": memo_delegator_address,"validator_address": validator_address, "pid": memo_pid,"amount": int(amount_validator)}
                                print("执行代理挖矿2", staking_info)
                        elif contract_info["delegator_address"] != memo_delegator_address:#有绑定，地址不一致，更新代理数量为0
                            if int(contract_info["amount"]) == 0:
                                print("数量为0，无需更新")
                            else:
                                staking_info = {"delegator_address": memo_delegator_address,"validator_address": validator_address, "pid": memo_pid,"amount": 0}
                                print("执行代理挖矿归零", staking_info)
                        #取消其他矿池挖矿
                        for pid in pools[validator_address]:
                            if pid == memo_pid:
                                continue
                            else:
                                delegator_address_evm = accountBindMap(pid, delegator_address)
                                contract_info = getData_forcontract(pid, delegator_address_evm)
                                if contract_info["delegator_address"] == memo_delegator_address and int(contract_info["amount"]) >0 :
                                    staking_info = {"delegator_address": memo_delegator_address,"validator_address": validator_address, "pid": pid,"amount": 0}
                                    print("执行代理挖矿归零2", staking_info)
                    elif check_memo == False or check_delegate == False or check_send == False:
                        for lists in msgs:
                            if lists['type'] == "cosmos-sdk/MsgDelegate":
                                delegator_address = lists["value"]["delegator_address"]
                                validator_address = lists["value"]["validator_address"]
                                amount_Delegate = lists["value"]["amount"]["amount"]
                                # 检查代理节点是否在walnut合约中
                                cancel_all_staking(validator_address, delegator_address, pools)

                else:
                    pools = getAllPools()
                    for msg in msgs:
                        if msg['type'] == "cosmos-sdk/MsgDelegate" :
                            #print(msg['type'][14:])       # Delegate
                            #print("hash %s" % txhash)
                            delegator_address = msg["value"]["delegator_address"]
                            validator_address = msg["value"]["validator_address"]
                            amount = msg["value"]["amount"]["amount"]
                            #print(delegator_address, "to", validator_address, amount)
                            # 检查代理节点是否在walnut合约中
                            cancel_all_staking(validator_address,delegator_address,pools)
                        elif msg['type'] == "cosmos-sdk/MsgUndelegate" :
                            #print(msg['type'][14:])          # Undelegate
                            #print("hash %s" % txhash)
                            delegator_address = msg["value"]["delegator_address"]
                            validator_address = msg["value"]["validator_address"]
                            amount = msg["value"]["amount"]["amount"]
                            #print(delegator_address, "to", validator_address, amount)
                            # 检查代理节点是否在walnut合约中
                            cancel_all_staking(validator_address,delegator_address, pools)
                        elif msg['type'] == "cosmos-sdk/MsgBeginRedelegate" :
                            #print(msg['type'][14:])          # BeginRedelegate
                            #print("hash %s" % txhash)
                            delegator_address = msg["value"]["delegator_address"]
                            validator_src_address = msg["value"]["validator_src_address"]
                            validator_dst_address = msg["value"]["validator_dst_address"]
                            amount = msg["value"]["amount"]["amount"]
                            #print(delegator_address, validator_src_address,"-to-",validator_dst_address ,amount)
                            # 检查代理节点是否在walnut合约中
                            cancel_all_staking(validator_address, delegator_address,pools)


        block_height += 1
        block_count += 1

    # 结束区块高度
    # if block_height > 9403400:
    #     break
    except Exception as e:
            print('[ERROR] Exception occurred when parsing block %s !' % block_height)
            print(e)
            print(traceback.format_exc())
            #block_height += 1
            block_count += 1
            time.sleep(2)


# 运行时间
running_time = time.time() - t0
print("Running time: ", time.time() - t0, "seconds")
print("Average time per block:", running_time / block_count, "seconds")
