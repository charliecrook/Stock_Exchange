# Stock Exchange Project
I was tasked to create a stock exchange with a user interface using minimal external libraries.

## Description of classes

### OrderBook class
The OrderBook class contains a dictionary with all the orders. The keys are the reference numbers for the orders. Each value is a list containing the information for the order. The dictionary is of the following format: {reference_no: [stock_name, price, quantity, timestamp]}. The class contains methods to add, cancel, amend and view orders.

### Exchange class
The Exchange class has a dependency on the OrderBook class. It requires a buy OrderBook, sell OrderBook and fee ladder. The fee ladder is a tuple of tuples: the first integer in the tuple is the price bracket, the second is the fee multiplier. The class has a method to calculate fees for all orders on the exchange, and a method to view all orders placed on today's date.

### SORT class
The SORT class takes in a list of different exchanges and a list of all stocks traded on these exchanges. The primary function of this class (the __run__ method) is to match all buy and sell orders across all the given input exchanges (i.e. an order on exchange 1 can trade with an order on exchange 2). Each order is checked against all other orders and a trade is exectued if the following conditions are met:
- The stock name matches
- The requested prices of the two orders is within a spread of 5
In this case, the sell order satisfies as much of the buy order as possible, and the two orders are updated to reflect this.
