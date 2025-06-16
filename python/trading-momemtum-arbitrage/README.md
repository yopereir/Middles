# Trading momentum arbitrage
This script aims to make options trades to profit off near-term options mispricing when news causes a stock price to move heavily in a particularly direction.

## Assumptions:
The news is not subject to change.
A trend reversal will not happen within a week.

## Countermeasures:
To counter these assumptions, a stop loss not exceeding 50% of the invested capital will be present.
Max capital for a trade cannot be more than 5%.

## Implementation:
Naked strategy- If a stock spikes in price, sell PUTS at the stock price prior to the news. If a stock tanks in price, sell CALLS at the stock price prior to the news. Create a stop loss at 50% of option value.
Covered strategy- If a stock spikes in price, sell a put credit spread with strick price of upper leg being stock price prior to the news. If a stock tanks in price, sell a call credit spread with strick price of lower leg being stock price prior to the news. Create a stop loss at EOD at 50% lower value.