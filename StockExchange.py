import csv
import time
import datetime
from datetime import timedelta

# The OrderBook class contains an order book and options to edit the order book
class OrderBook:
    
    def __init__(self, orders):
        self.orders = orders
        
    def new_order(self):
        print("________________________\n")
        stock = input("Enter company name: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        self.orders[max(self.orders.keys())+1] = [stock, price, quantity, datetime.datetime.fromtimestamp(time.mktime(time.localtime()))]
        print("________________________\n")
        
    def cancel_order(self):
        print("________________________\n")
        order_id = int(input("Enter order ID: "))
        del self.orders[order_id]
        print("________________________\n")
        
    def amend_order(self):
        print("________________________\n")
        order_id = int(input("Enter order ID: "))
        stock = input("Enter company name: ")
        price = float(input("Enter price: "))
        quantity = int(input("Enter quantity: "))
        self.orders[order_id] = [stock, price, quantity, datetime.datetime.fromtimestamp(time.mktime(time.localtime()))]
        print("________________________\n")
        
    def view_orders(self):
        print("----------\nORDER BOOK\n----------")
        for key in self.orders.keys():
            print("________________________\n")
            print("Order ID: {}".format(key))
            print("Company: {}".format(self.orders[key][0]))
            print("Price: {}".format(self.orders[key][1]))
            print("Quantity: {}".format(self.orders[key][2]))
            print("Order time: {}".format(self.orders[key][3]))
            print("________________________\n")
                       

# Exchange class depends on OrderBook class. It mimics a stock exchange with buy orders, sell orders and a fee ladder.
class Exchange:
    
    def __init__(self, buy_order_book, sell_order_book, fee_ladder):
        self.buy_order_book = buy_order_book
        self.sell_order_book = sell_order_book
        self.fee_ladder = fee_ladder
        self.buy_fees = self.calc_fees(buy_order_book)
        self.sell_fees = self.calc_fees(sell_order_book)
                        
    def calc_fees(self, order_book):
        fees = {}
        for key in order_book.orders:
            if order_book.orders[key][2] < self.fee_ladder[0][0]:
                fees[key] = order_book.orders[key][2] * self.fee_ladder[0][1]
            elif order_book.orders[key][2] >= self.fee_ladder[0][0] and order_book.orders[key][2] < self.fee_ladder[1][0]:
                fees[key] = order_book.orders[key][2] * self.fee_ladder[1][1]
            elif order_book.orders[key][2] >= self.fee_ladder[1][1]:
                fees[key] = order_book.orders[key][2] * self.fee_ladder[2][1]
        return fees
    
    def todays_trade_value(self, order_book):
        total_trade_value = 0
        for key in order_book.orders:
            if order_book.orders[key][3].date() == datetime.datetime.today().date():
                total_trade_value += order_book.orders[key][1] * order_book.orders[key][2]
        return total_trade_value
    

# The SORT class matches buy and sell orders for many different input exchanges
class SORT:
    
    def __init__(self, exchanges, stocks):
        self.exchanges = exchanges
        self.stocks = stocks
        self.trade_log = {}

    # this method runs the order matching algorithm
    def __run__(self):
        self.merged_buy_orders, self.merged_sell_orders = Utilities.merge_order_books(self.exchanges)
        self.matched_buy_orders, self.matched_sell_orders = self.match() # these are concatonated order books after trades
        self.update_exchanges()
        
    def match(self):
        matched_buy_orders = {}
        matched_sell_orders = {}
        for stock in self.stocks:
            dummy_buy = Utilities.create_dummy_orders(self.merged_buy_orders, self.stocks)
            dummy_sell = Utilities.create_dummy_orders(self.merged_sell_orders, self.stocks)
            dummy_buy, dummy_sell = self.execute_trades(dummy_buy, dummy_sell) # start with one pass
            matched_buy_orders.update(dummy_buy)
            matched_sell_orders.update(dummy_sell) 
        return matched_buy_orders, matched_sell_orders
        
    def execute_trades(self, buy_orders, sell_orders):
        for i in buy_orders:
            for j in sell_orders:
                if self.check_spread(buy_orders, i, sell_orders, j) and self.check_quantity(buy_orders, i, sell_orders, j):
                    trade_price = min(buy_orders[i][1], sell_orders[j][1])
                    trade_quantity = min(buy_orders[i][2], sell_orders[j][2])
                    print("________________________\n")
                    print("Buy order reference {} traded with sell order reference {}.".format(i,j))
                    print("Quantity traded: {}\nPrice of trade: {}".format(trade_quantity, trade_price))
                    print("________________________\n")
                    buy_orders[i][2] -= trade_quantity
                    sell_orders[j][2] -= trade_quantity
                    self.trade_log[Utilities.concat(i, j)] = (buy_orders[i][0], trade_price, trade_quantity)          
        return buy_orders, sell_orders
    
    def check_spread(self, buy_orders, buy_ref, sell_orders, sell_ref):
        return buy_orders[buy_ref][1] <= sell_orders[sell_ref][1] + 5 and buy_orders[buy_ref][1] >= sell_orders[sell_ref][1] - 5
    
    def check_quantity(self, buy_orders, buy_ref, sell_orders, sell_ref):
        return buy_orders[buy_ref][2] > 0 and sell_orders[sell_ref][2] > 0
    
    def update_exchanges(self):
        for exchange in self.exchanges:
            exchange.buy_order_book = OrderBook(self.update_order_book(exchange.buy_order_book.orders, self.matched_buy_orders))
            exchange.sell_order_book = OrderBook(self.update_order_book(exchange.sell_order_book.orders, self.matched_sell_orders))
            
    def update_order_book(self, order_book, matched_book):
        for order in order_book:
            if order in matched_book.keys():
                timestamp = order_book[order][3]
                order_book[order] = [matched_book[order][0], matched_book[order][1], matched_book[order][2], timestamp]
        return order_book
    
    def check_order_status(self, order_book):
        print("________________________\n")
        for order in order_book.orders:
            if (order in self.matched_buy_orders.keys() or self.matched_sell_orders.keys()) and order_book.orders[order][2] == 0:
                print("Order reference {} partially filled.".format(order))
            elif order in self.matched_buy_orders.keys() or self.matched_sell_orders.keys():
                print("Order reference {} fully filled.".format(order))
            else:
                print("Order reference {} not yet matched.".format(order))


# The UserMenu class is the interface for the end user
class UserMenu:
    
    def __init__(self, exchange, SORT):
        self.exit_inputs = ("Quit", "quit", "QUIT", "Exit", "exit", "EXIT", "Close", "close", "CLOSE")
        self.exchange = exchange
        self.SORT = SORT
        
    def main_menu(self):
        input_options = (1, 2, 3, 4, 5)
        number_options = len(input_options)
        user_input = 1
        while user_input not in self.exit_inputs:
            print("________________________\n")
            print("\nPlease choose from the following options: \n 1). Buy order book options \n 2). Sell order book options \n 3). View today's total order value \n 4). Execute orders \n 5). Exit")
            try:
                user_input = int(input("Enter a number between 1 and {}.".format(number_options)))
            except:
                print("________________________\n")
                print("You must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
            
            if user_input not in input_options:
                print("________________________\n")
                print("\nYou must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
                
            elif user_input == 1:
                self.order_menu(self.exchange.buy_order_book)
                
            elif user_input == 2:
                self.order_menu(self.exchange.sell_order_book)
                
            elif user_input == 3:
                print("________________________\n")
                print("\nPlease choose from the following options: \n 1). View value of buy orders \n 2). View value of sell orders")
                print(self.exchange.todays_trade_value(self.choose_buy_or_sell()))
            
            elif user_input == 4:
                self.SORT.__run__()
                print("________________________\n")
                print("\nPlease choose from the following options: \n 1). View status of buy orders \n 2). View status of sell orders")
                self.SORT.check_order_status(self.choose_buy_or_sell())
                                      
            elif user_input == 5:
                break
            
            else:
                print("________________________\n")
                print("An unexpected error occurred")
                break
                
    def order_menu(self, order_book):
        input_options = (1, 2, 3, 4, 5, 6)
        number_options = len(input_options)
        user_input = 1
        while user_input not in self.exit_inputs:
            print("________________________\n")
            print("\nPlease choose from the following options: \n 1). New buy order \n 2). Cancel order \n 3). Amend order \n 4). View orders \n 5). Calculate fees \n 6). Return to the previous menu")
            
            try:
                user_input = int(input("Enter a number between 1 and {}.".format(number_options)))
            except:
                print("________________________\n")
                print("You must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
            
            if user_input not in input_options:
                print("________________________\n")
                print("\nYou must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
                
            elif user_input == 1:
                order_book.new_order()
                
            elif user_input == 2:
                order_book.cancel_order()
                
            elif user_input == 3:
                order_book.amend_order()
                
            elif user_input == 4:
                order_book.view_orders()
                
            elif user_input == 5:
                print("________________________\n")
                print("\nPlease choose from the following options: \n 1). Calculate fees of buy orders \n 2). Calculate fees of sell orders")
                print("________________________\n")
                [print("Order reference: {}   Fee: {}".format(k,v)) for k,v in self.exchange.calc_fees(self.choose_buy_or_sell()).items()]
            
            elif user_input == 6:
                break
            
            else:
                print("________________________\n")
                print("An unexpected error occurred.")
                break

    def choose_buy_or_sell(self):
        input_options = (1, 2)
        number_options = len(input_options)
        user_input = 1
        while user_input not in self.exit_inputs:
            
            try:
                user_input = int(input("Enter a number between 1 and {}.".format(number_options)))
            except:
                print("________________________\n")
                print("You must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
            
            if user_input not in input_options:
                print("________________________\n")
                print("\nYou must enter a number between 1 and {}.".format(number_options))
                print("________________________\n")
                continue
                
            elif user_input == 1:
                return self.exchange.buy_order_book
                break
                
            elif user_input == 2:
                return self.exchange.sell_order_book
                break

            else:
                print("________________________\n")
                print("An unexpected error occurred.")
                break
                

# The FileManager class read and writes order books to csv files
class FileManager:
    
    def write_to_csv(dict_data, name, self=None):
        csv_columns = list(dict_data.keys())
        dict_data = [dict_data]
        with open(name, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=',', fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                    writer.writerow(data)

    def read_from_csv(name, self=None):
        with open(name, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')
            line_count = 0
            for data in reader:
                x = data
            y = {}
            for key in x:
                y[int(key)] = eval(x[key])
            return y
                

# This class performs utility operations for the other classes
class Utilities:
    
    def concat(a, b, self=None):
        return int(f"{a}{b}")

    def merge_order_books(exchanges, self=None):
        merged_buy = {}
        merged_sell = {}
        for exchange in exchanges:
            merged_buy.update(exchange.buy_order_book.orders)
            merged_sell.update(exchange.sell_order_book.orders)
        return merged_buy, merged_sell 
    
    def create_dummy_orders(order_book, stocks, self=None):
        dummy_orders = {}
        for key in order_book:
            if order_book[key][0] in stocks:
                dummy_orders[key] = order_book[key]
        return dummy_orders