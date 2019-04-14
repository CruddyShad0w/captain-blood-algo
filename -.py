from pylivetrader.api import (
                             order_target_percent,
                             symbol,
                             schedule_function,
                             date_rules,
                             time_rules
                             )

#Test with 'handle data' then try 'rebalance'
def initialize(context):
    EveryThisManyMinutes = 1
    TradingDayHours = 6.5
    TradingDayMinutes = int(TradingDayHours * 60)
    for minutez in range(1, TradingDayMinutes, EveryThisManyMinutes):
	schedule_function(
		grab_data,
		date_rules.every_day(),
		time_rules.market_open(minutes=minutez))
	schedule_function(
		handle_trade,
		date_rules.every_day(),
		time_rules.market_open(minutes=minutez))

def grab_data(context, data):
    dgaz_two_week_price = data.history(
        context.dgaz,
        fields='price',
        bar_count=10,
        frequency='1d'
        )
    ugaz_two_week_price = data.history(
        context.ugaz,
        fields='price',
        bar_count=10,
        frequency='1d'
        )
    dgaz_week_price = data.history(
        context.dgaz,
        fields='price',
        bar_count=5,
        frequency='1d'
        )

def handle_trade(context, data):

    context.dgaz = [ symbol('DGAZ') ]
    context.ugaz = [ symbol('UGAZ') ]
    
    current_dgaz_price = data.current(context.dgaz, 'price')
    
    current_ugaz_price = data.current(context.ugaz, 'price')
    
    average_dgaz_two_week_price = dgaz_two_week_price.mean()
    
    average_ugaz_two_week_price = ugaz_two_week_price.mean()
    
    average_dgaz_week_price = dgaz_week_price.mean()
    
    
    if current_dgaz_price > average_dgaz_two_week_price:
        order_target_percent(symbol('DGAZ'), 0)
            
    if current_ugaz_price > average_ugaz_two_week_price:
        order_target_percent(symbol('UGAZ'), 0)
            
    if current_dgaz_price <= (0.8 * average_dgaz_two_week_price):
        order_target_percent(symbol('DGAZ'), 0)
            
    if current_ugaz_price <= (0.8 * average_ugaz_two_week_price):
        order_target_percent(symbol('UGAZ'), 0)
            
    if current_dgaz_price <= (0.8 * average_dgaz_two_week_price):
        order_target_percent(symbol('UGAZ'), 1)
                
    if current_ugaz_price <= (0.8 * average_ugaz_two_week_price):
        order_target_percent(symbol('DGAZ'), 1)
            
    if current_dgaz_price < (0.95 * average_dgaz_week_price):
        order_target_percent(symbol('DGAZ'), 1)
        
    if current_dgaz_price >= (1.1 * average_dgaz_two_week_price):
        order_target_percent(symbol('DGAZ'), 1)
