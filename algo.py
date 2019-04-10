
from pylivetrader.api import (
                             schedule_function,
                             date_rules,
                             time_rules,
                             attach_pipeline,
                             get_datetime,
                             pipeline_output,
                             get_open_orders,
                             order,
                             symbol,
                             cancel_order
                             )

import logbook
log = logbook.Logger('algo')

import numpy as np  # needed for NaN handling

from itertools import cycle

def record(*args, **kwargs):
    log.info('args={}, kwargs={}'.format(args, kwargs))

def initialize(context):
    context.MaxBuyOrdersAtOnce = 50
    context.MyFireSaleAge = 6

    context.MaxInvestment = 150000

    # over simplistic tracking of position age
    if not hasattr(context, 'age') or not context.age:
        context.age = {}

    # Rebalance
    minutes = 10
    trading_hours = 6.5
    trading_minutes = int(trading_hours * 60)
    for minutez in range(1, trading_minutes, minutes):
        schedule_function(
				rebalance,
                date_rules.every_day(),
                time_rules.market_open(
                    minutes=minutez))

    # Prevent excessive logging of canceled orders at market close.
    schedule_function(
        cancel_open_orders,
        date_rules.every_day(),
        time_rules.market_close(
            hours=0,
            minutes=1))

    # Record variables at the end of each day.
    schedule_function(
        my_record_vars,
        date_rules.every_day(),
        time_rules.market_close())





def submit_sell(stock, context, data):
    
    if get_open_orders(stock):
        return

    # We bought a stock but don't know it's age yet
    if stock not in context.age:
        context.age[stock] = 0

    # Don't sell stuff that's less than 1 day old
    if stock in context.age and context.age[stock] < 1:
        return

    shares = context.portfolio.positions[stock].amount
    current_price = float(data.current([stock], 'price'))
    two_week_price_history = data.history([stock], 'price', 10, '1d')
    average_two_week_price = float(two_week_price_history.mean())
    current_price = float(data.current([stock], 'price'))
    context.stocks = [ symbol('UGAZ'), symbol('DGAZ') ]

    if (context.age[stock] >= context.MyFireSaleAge and
            (current_price < float(0.8 * average_two_week_price))):
            log.info("First sell function is working!" % stock.symbol)
        
    if (context.age[stock] >= context.MyFireSaleAge and
            (current_price > average_two_week_price)):
            log.info("Second sell function is working!" % stock.symbol)

    order(context.stock, -shares)

def submit_buy(stock, context, data, weight):
    
    cash = min(investment_limits(context)['remaining_to_invest'], context.portfolio.cash)

    two_week_price_history = data.history([stock], 'price', 10, '1d')
    one_week_price_history = data.history([stock], 'price', 5, '1d')
    average_two_week_price = float(two_week_price_history.mean())
    average_one_week_price = float(one_week_price_history.mean())
    current_price = float(data.current([stock], 'price'))
    
    context.stock = [ symbol('UGAZ'), symbol('DGAZ') ]
    

    if np.isnan(current_price):
            pass  # probably best to wait until nan goes away
            
    if current_price >= float(1.1 * average_two_week_price): # if the price is 10% greater than or equal to the 10d avg
            buy_price = float(current_price)
            
    if current_price >= float(1.15 * average_two_week_price): # if the price is 15% above the 10d avg
            buy_price = float(current_price)
            
    if current_price < float(0.95 * average_one_week_price): # if the price is 5% below the 5d avg
            buy_price = float(current_price)
            

            
    else:
            buy_price = float(current_price * context.buy_factor)
            shares_to_buy = int(weight * cash / buy_price)


            # This cancels open sales that would prevent these buys from being submitted if running
            # up against the PDT rule
            open_orders = get_open_orders()
            if stock in open_orders:
                for open_order in open_orders[stock]:
                    cancel_order(open_order)

    order(context.stock, shares_to_buy)
def rebalance(stock, context, data, weight):
	submit_sell(stock, context, data)
	submit_buy(stock, context, data, weight)

def my_record_vars(context, data):
    """
    Record variables at the end of each day.
    """

    # Record our variables.
    record(leverage=context.account.leverage)

    if 0 < len(context.age):
        MaxAge = context.age[max(
            context.age.keys(), key=(lambda k: context.age[k]))]
        MinAge = context.age[min(
            context.age.keys(), key=(lambda k: context.age[k]))]
        record(MaxAge=MaxAge)
        record(MinAge=MinAge)

    limits = investment_limits(context)
    record(ExcessCash=limits['excess_cash'])
    record(Invested=limits['invested'])
    record(RemainingToInvest=limits['remaining_to_invest'])

def cancel_open_buy_orders(context, data):
    oo = get_open_orders()
    if len(oo) == 0:
        return
    for stock, orders in oo.items():
        for o in orders:
            # message = 'Canceling order of {amount} shares in {stock}'
            # log.info(message.format(amount=o.amount, stock=stock))
            if 0 < o.amount:  # it is a buy order
                cancel_order(o)


def cancel_open_orders(context, data):
    oo = get_open_orders()
    if len(oo) == 0:
        return
    for stock, orders in oo.items():
        for o in orders:
            # message = 'Canceling order of {amount} shares in {stock}'
            # log.info(message.format(amount=o.amount, stock=stock))
            cancel_order(o)

def investment_limits(context):
    cash = context.portfolio.cash
    portfolio_value = context.portfolio.portfolio_value
    invested = portfolio_value - cash
    remaining_to_invest = max(0, context.MaxInvestment - invested)
    excess_cash = max(0, cash - remaining_to_invest)

    return {
        "invested": invested,
        "remaining_to_invest": remaining_to_invest,
        "excess_cash": excess_cash
    }