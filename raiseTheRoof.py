import os
import ccxt
import json
import time
import sys

class RaiseIt:

    def __init__(self):

        os.chdir(sys.path[0])
        self.symbol = "BUSD/USDT"
        self.bid = None
        self.timeout_var = 10


        if(os.path.exists("config.json") and os.stat("config.json").st_size):
            with open("config.json", "r") as f:
                keys = json.load(f)
            api_key = keys['apikey']
            secret_key = keys['secretkey']
        else:
            api_key = input("Enter API key: ")
            secret_key = input("Enter secret key: ")
            with open("config.json", "w") as f:
                temp = json.dumps({'apikey':api_key,'secretkey':secret_key})
                f.write(temp)

        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'timeout': 30000,
            'enableRateLimit': True,
        })

        print(self.is_open())
        bal = self.get_bal()
        print("USDT",bal[0])
        print("BUSD",bal[1])
        tot = bal[0]+bal[1]
        self.initial_tot_bal = self.total_bank()

        if(os.path.exists("raise_data.json") and os.stat("raise_data.json").st_size):
            with open('raise_data.json','r') as f:
                try:
                    dat = json.load(f)
                except json.decoder.JSONDecodeError as e:
                    print(e)
                    print(f.read())
                    open('raise_data.json', 'w').close()
                    dat = {"last_balance": None, "total_lost": 0, "trading_volume": 0}


            with open('raise_data.json','w') as f:
                f.write(json.dumps(dat))
        else:
            with open('raise_data.json','w') as f:
                f.write(json.dumps({'last_balance':tot,'total_lost':0}))

        self.is_open(display=True)

    #Main functions
    def buy(self, wait=False):
        budg = self.get_bal()[0]-0.001
        if(budg>9):
            tick = self.exchange.fetch_ticker(self.symbol)
            self.bid = tick['bid']
            print(self.bid)
            self.exchange.create_market_buy_order(self.symbol, budg * self.bid)
            count = 0
            while (self.is_open() and wait):
                print("waiting buy")
                time.sleep(1)
                count += 1
                if (count == self.timeout_var):
                    self.timeout()
            self.add_volume(budg)
        else:
            print("Not enough USDT")

    def sell(self, wait=False):
        busd_q = self.get_bal()[1]-0.001
        if(busd_q>9):
            if(self.bid is None):
                tick = self.exchange.fetch_ticker(self.symbol)
                self.bid = tick['bid']
            #createMarketSellOrder(symbol, amount[, params])
            self.exchange.create_limit_sell_order(self.symbol, busd_q, self.bid)
            count=0
            while(self.is_open() and wait):
                print("waiting sell")
                time.sleep(1+count)
                count+=1
                if(count==self.timeout_var):
                    self.timeout()
            self.add_volume(busd_q)
        else:
            print(busd_q, "Not enough BUSD")

    def start(self, i=1):
        for x in range(2):
            b = ra.get_bal()
            while (ra.is_open(display=True)):
                time.sleep(30)
            if (b[0] > (ra.total_bank() / 3)):
                ra.buy(wait=True)
            else:
                ra.sell()

    def main(self):

        if(self.is_open()):
            print("Error order is open")
            return
        elif(self.total_bank()<17):
            print("Lost too much money")
            with open('error.txt', 'w') as f:
                f.write("Lost too much money",time.time())
            quit()

        t = self.total_bank()
        print("totalbank->",t)
        print('totalloss->',t-self.initial_tot_bal)

        bal = self.get_bal()
        if(bal[0]>bal[1]):
            self.buy(wait=True)
        else:
            self.sell(wait=True)


    #management
    def is_open(self, display=False, get_orders=False):
        open_orders = self.exchange.fetch_open_orders(self.symbol)

        if (display):
            print("->",len(open_orders), open_orders)
            if(open_orders):
                print(open_orders[0]['info']['side'])
        if (get_orders):
            return open_orders

        if(open_orders):
            return True
        else:
            return False

    def get_bal(self):
        balances = self.exchange.fetch_balance()
        bal_usdt = balances['USDT']['free']
        bal_busd = balances['BUSD']['free']
        return (bal_usdt, bal_busd)

    def add_volume(self, volume):
        with open("raise_data.json",'r+') as f:
            dat = json.load(f)
            if("trading_volume" in dat):
                dat["trading_volume"] += volume
                print("total volume: ", dat["trading_volume"])
            else:
                dat.update({"trading_volume":volume})
            temp = json.dumps(dat)
            f.write(temp)

    #Helpful
    def timeout(self):
        open_orders = self.exchange.fetch_open_orders(self.symbol)
        print(open_orders[0]['info']['orderId'])
        print('timeout')
        if(len(open_orders)>1):
            print("more than one order")

    def total_bank(self):
        bal = self.get_bal()
        free = bal[0] + bal[1]
        open_orders = self.is_open(get_orders=True)
        if(open_orders):
            for x in range(len(open_orders)):
                if(open_orders[x]['info']['symbol']=="BUSDUSDT"):
                    free+= float(open_orders[x]['info']['origQty'])
        return free

        #self.exchange.cancel_order()



if __name__=="__main__":
    # rad = RaiseIt()
    #
    #
    # rad.is_open(display=True)
    # for x in range(5):
    #     i = 1
    #     while (ra.is_open()):
    #         i += 1
    #         time.sleep(20 + i)
    #     ra.main()
    ra = RaiseIt()
    ra.start()
