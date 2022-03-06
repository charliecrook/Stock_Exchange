# Stock Exchange Project
I was tasked to create a stock exchange with a user interface using minimal external libraries.

## Description of classes

### OrderBook class
The OrderBook class contains a dictionary with all the orders. The keys are the reference numbers for the orders. Each value is a list containing the information for the order. The dictionary is of the following format: {reference_no: [stock_name, price, quantity, timestamp]}. The class contains methods to add, cancel, amend and view orders.

### Exchange class
The Exchange class has a dependency on the OrderBook class. It requires a buy OrderBook, sell OrderBook and fee ladder. The fee ladder is a tuple of tuples: the first integer in the tuple is the price bracket, the second is the fee multiplier. The class has a method to calculate fees for all orders on the exchange, and a method to view all orders placed on today's date.
