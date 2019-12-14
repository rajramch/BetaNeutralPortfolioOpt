import ffn 
import datetime as dt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from empyrical import alpha_beta   ### Used if we want to calculate the beta values
#import matplotlib as pyplot  /// Used if we want to plot any Diagrams
#import numpy as np
#import pandas as pd
#from pandas_datareader import data



#  Calculate and Print the beta values of the 30 Stocks of Dow Jones
# =============================================================================
# price = list()
# benchmark = ffn.get('spy', start='2016-11-01',end='2018-11-01')
# names = ['mmm','axp','aapl','ba','cat','cvx','csco','ko', 'xom','gs','hd','ibm','intc','jnj','jpm','mcd','mrk','msft','nke','pfe','pg','trv','unh','utx','vz','v','wmt','wba','dis']
# for i in names:
#     temp = ffn.get(i, start='2016-11-01',end='2018-11-01')
#     price.append(temp)
#     alpha, beta = alpha_beta(temp, benchmark)
#     print('name: ',i,'\tbeta value: ',beta)
# =============================================================================



#Stock selection is made! Top five stocks for our portfolio
#Plot of each stock to show price evolution within the given time frame including the benchmark
# =============================================================================
# prices1 = ffn.get('pfe,ibm,wmt,msft,cat,spy', start='2016-11-01', end='2018-11-01')
# prices = ffn.get('pfe,ibm,wmt,msft,cat', start='2016-11-01', end='2018-11-01')
# benchmark = ffn.get('spy', start='2016-11-01')
# ax = prices1.rebase().plot(lw=2, alpha=0.8)
# plt.ylabel('price in $')
# =============================================================================



#Report of some important performance matrix
# =============================================================================
# stats = prices.calc_stats()
# stats.display()
# =============================================================================



#Calculate beta value for each stock choice
# =============================================================================
# price = list()
# benchmark = ffn.get('spy', start='2016-11-01',end='2018-11-01')
# names = ['pfe','ibm','wmt','msft','cat']
# for i in names:
#     
#     temp = ffn.get(i, start='2016-11-01',end='2018-11-01')
#     price.append(temp)
#     alpha, beta = alpha_beta(temp, benchmark)
#     print('name: ',i,'\tbeta value: ',beta)
# =============================================================================


# Expected returns and sample covariance
#Minimum volatility. May be useful if you're trying to get an idea of how low the volatility could be, 
#but in practice it makes a lot more sense to me to use the portfolio that maximises the Sharpe ratio.
# Optimise portfolio for maximum Sharpe Ratio to serve as benchmark
# =============================================================================
# mu = expected_returns.mean_historical_return(prices)
# S = risk_models.sample_cov(prices)
# 
# ef = EfficientFrontier(mu, S)
# raw_weights = ef.max_sharpe()       #  raw_weights = ef.min_volatility()
# cleaned_weights = ef.clean_weights() 
# print(cleaned_weights)
# ef.portfolio_performance(verbose=True)
# =============================================================================


#To achieve beta neutrality
# =============================================================================
# ef = EfficientFrontier(mu, S, weight_bounds=(-1, 1))
# ef.efficient_return(target_return=0.2, market_neutral=True)
# =============================================================================


#The result of market neutral optimisation is essentially a long and short portfolio. 
#We normalize the results as weights as shown below
# =============================================================================
# weights = ef.efficient_return(target_return=0.2, market_neutral=True)
# weight_sum = sum(w for w in weights.values() if w > 0)
# normalised_weights = {k:v/weight_sum for k,v in weights.items()}
# normalised_weights
# =============================================================================

#We then need to convert these weights into an actual allocation, telling you how many shares of each asset you should purchase.
# =============================================================================
# latest_prices = get_latest_prices(prices)
# da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=1000000)
# allocation, leftover = da.lp_portfolio()
# print(allocation)
# print("Funds remaining: ${:.2f}".format(leftover))
# =============================================================================


#To Calculate the returns we use the following code
# =============================================================================
# sum1 = 0
# for key,val in allocation.items():
#     sum1 = sum1 - (latest_prices[key]*val)
# print(sum1)
# new = 0
# for key,val in allocation.items():
#     new = new + (latest_prices2[key]*val)
#     sum1 = sum1 + (latest_prices2[key]*val)
# print(new)
# print(sum1)
# =============================================================================



##############################################################################
#Combining the above code into a single function which calculates the returns for the selected time frame

def calc(stockStartTime,stockEndTime):
    #calculating 2 years prior of the start date
    tempdate = dt.datetime.fromisoformat(stockStartTime)
    tempdate = tempdate - dt.timedelta(weeks=104)
    prices = ffn.get('pfe,ibm,wmt,msft,cat', start= tempdate.strftime('%Y-%m-%d'), end=stockStartTime)
    # Expected returns and sample covariance
    mu = expected_returns.mean_historical_return(prices)
    S = risk_models.sample_cov(prices)
    # Calculating raw weights to minimize volatility.
    # This is done because or client's requirements are low risk 
    ef = EfficientFrontier(mu, S)
    raw_weights = ef.min_volatility() #ef.max_sharpe()
    cleaned_weights = ef.clean_weights() 
    print("Cleaned weights:\n",cleaned_weights)
    print("Portfolio Performance:\n",ef.portfolio_performance(verbose=True))
    #To achieve beta neutrality
    ef = EfficientFrontier(mu, S, weight_bounds=(-1, 1))
    print(" Weights: ",ef.efficient_return(target_return=0.15, market_neutral=True))
    weights = ef.efficient_return(target_return=0.2, market_neutral=True)
    weight_sum = sum(w for w in weights.values() if w > 0)
    #normalised_weights = {k:v/weight_sum for k,v in weights.items()}
    #print("Normalized weights: ",normalised_weights)
    
    #We then need to convert these weights into an actual allocation, telling you how many shares of each asset you should purchase.
    latest_prices = get_latest_prices(prices)
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=1000000)
    allocation, leftover = da.lp_portfolio()
    print("")
    for key,val in allocation.items():
        print("Number of positions in ",key," stock: ",val)
    print("")
    print("Funds remaining: ${:.2f}".format(leftover))
    print("")
    prices2 = ffn.get('pfe,ibm,wmt,msft,cat', start=stockStartTime, end=stockEndTime)
    latest_prices2 = get_latest_prices(prices2)
    sum1 = 0
    for key,val in allocation.items():
        sum1 = sum1 - (latest_prices[key]*val)
    print("Value of Portfolio after short sales :\t",abs(sum1))
    new = 0
    for key,val in allocation.items():
        new = new + (latest_prices2[key]*val)
        sum1 = sum1 + (latest_prices2[key]*val)
    print("Value at end of period :\t\t",new)
    print("Profit at end of time period :\t\t",sum1)
    return sum1 
###############################################################################################
# Writing a function which uses the profit calculation function and gets the total 
def totalret(startDate):
    tempdate = dt.datetime.fromisoformat(startDate)
    monthend = tempdate + dt.timedelta(days=30)
    #print("monthend:",monthend)
    total = 0
    monthlyRet = list()
    for i in range(12):
        print("\n\n********************",tempdate.strftime('%d %b %Y'),"***********************\n\n")
        ret = calc( stockStartTime = tempdate.strftime('%Y-%m-%d') , stockEndTime = monthend.strftime('%Y-%m-%d'))
        monthlyRet.append(ret)
        total = total + ret
        tempdate = tempdate + dt.timedelta(days=30)
        #print("temp:",tempdate)
        monthend = monthend + dt.timedelta(days=30)
        #print("monthend:",monthend)
        i = i + 1
    print("\n")
    for i in monthlyRet:
        print("Returns per time period: ${:.2f}".format(i),"\tReturns in percentage:", i/1000000)
    print("\n\n\n*************The total return for 1 year : ", total,"******************")
    
totalret("2018-11-01")