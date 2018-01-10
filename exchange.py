#encoding:utf-8
import requests
from HttpMD5Util import buildMySign
from okex_error_code import error_codes_map
import sys
from config import APP_CONFIG



class ExchangeBase(object):
    def __init__(self,name,coin_type):
        self.name=name
        self.coin_type=coin_type

    def GetName(self):
        return self.name

    def GetCoinType(self):
        return self.coin_type

    def GetDepth(self):
        pass

    def GetTicker(self):
        pass
    def GetAccount(self):
        pass

    def Buy(self,price,amount):
        pass

    def Sell(self,price,amount):
        pass

    def CancelOrder(self,order_id):
        pass

    def GetOrder(self,order_id):
        pass
    def GetOrders(self,*orders_id):
        pass
class ExchangeOkex(ExchangeBase):

    def __init__(self,name,coin_type,api_key,secret_key):
        self.name=name
        self.coin_type=coin_type
        self.api_key=api_key
        self.secret_key=secret_key
        ExchangeBase.__init__(self,name,coin_type)

    def __build_data(self,data):
        sign=buildMySign(data,self.secret_key)
        data["sign"]=sign

    def __http_get(self,*args,**kvargs):
        response=requests.get(*args,**kvargs)
        if response.status_code==403:
            raise Exception(u"用户请求过快，IP被屏蔽")
        res_json=response.json()
        if "error_code" in res_json:
            raise Exception(error_codes_map[res_json["error_code"]].encode(sys.stdout.encoding))
        return res_json

    def __http_post(self,*args,**kvargs):
        data=kvargs["data"]
        if data:
            self.__build_data(data)
        response=requests.post(*args,**kvargs)
        if response.status_code==403:
            raise Exception(u"用户请求过快，IP被屏蔽")
        res_json=response.json()
        if "error_code" in res_json:
            raise Exception(error_codes_map[res_json["error_code"]])
        return res_json

    def GetDepth(self):
        url="https://www.okex.com/api/v1/depth.do?symbol=%s"%self.coin_type
        return self.__http_get(url)

    def GetTicker(self):
        url="https://www.okex.com/api/v1/ticker.do?symbol=%s"%self.coin_type
        return self.__http_get(url)

    def GetAccount(self):
        url="https://www.okex.com/api/v1/userinfo.do"
        data={
        "api_key":self.api_key,
        }
        return self.__http_post(url,data=data)

    def __transaction(self,price,amount,trans_type=None):
        url="https://www.okex.com/api/v1/trade.do"
        data={
        "api_key":self.api_key,
        "symbol":self.coin_type,
        "type":trans_type,
        "price":price,
        "amount":amount,
        }
        return  self.__http_post(url,data=data)

    def Buy(self,price,amount):
        return self.__transaction(price,amount,"buy")

    def Sell(self,price,amount):
        return self.__transaction(price,amount,"sell")

    def CancelOrder(self,order_id):
        url="https://www.okex.com/api/v1/cancel_order.do"
        data={
        "api_key":self.api_key,
        "symbol":self.coin_type,
        "order_id":order_id,
        }
        return self.__http_post(url,data=data)

    def GetOrder(self,order_id):
        url="https://www.okex.com/api/v1/order_info.do"
        data={
        "api_key":self.api_key,
        "symbol":self.coin_type,
        "order_id":order_id,
        }
        return self.__http_post(url,data=data)
        
    def GetOrders(self,*orders_id):
        url="https://www.okex.com/api/v1/orders_info.do"
        order_id=",".join(orders_id)
        data={
        "api_key":self.api_key,
        "symbol":self.coin_type,
        "order_id":order_id,
        }
        return self.__http_post(url,data=data)
def Exchange(name,coin_type):
    if name=="okex":
        return ExchangeOkex(name,coin_type,APP_CONFIG[name]["api_key"],APP_CONFIG[name]["secret_key"])


