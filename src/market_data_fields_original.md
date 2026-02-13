# IBKR Market Data Fields (Original Reference)

Market data fields available from the `/iserver/marketdata/snapshot` endpoint. Fields are sorted by Field ID.

## Field Reference
| Field ID | Return Type | Name | Description |
|----------|-------------|------|-------------|
| 31 | string | Last Price | The last price at which the contract traded. May contain one of the following prefixes: C – Previous day's closing price. H – Trading has halted. |
| 55 | string | Symbol | Symbol |
| 58 | string | Text | Text |
| 70 | string | High | Current day high price |
| 71 | string | Low | Current day low price |
| 73 | string | Market Value | The current market value of your position in the security. Market Value is calculated with real time market data (even when not subscribed to market data). |
| 74 | string | Avg Price | The average price of the position. |
| 75 | string | Unrealized PnL | Unrealized profit or loss. Unrealized PnL is calculated with real time market data (even when not subscribed to market data). |
| 76 | string | Formatted position | Formatted position |
| 77 | string | Formatted Unrealized PnL | Formatted Unrealized PnL |
| 78 | string | Daily PnL | Your profit or loss of the day since prior close. Daily PnL is calculated with real time market data (even when not subscribed to market data). |
| 79 | string | Realized PnL | Realized profit or loss. Realized PnL is calculated with real time market data (even when not subscribed to market data). |
| 80 | string | Unrealized PnL % | Unrealized profit or loss expressed in percentage. |
| 82 | string | Change | The difference between the last price and the close on the previous trading day |
| 83 | string | Change % | The difference between the last price and the close on the previous trading day in percentage. |
| 84 | string | Bid Price | The highest-priced bid on the contract. |
| 85 | string | Ask Size | The number of contracts or shares offered at the ask price. |
| 86 | string | Ask Price | The lowest-priced offer on the contract. |
| 87 | string | Volume | Volume for the day, formatted with 'K' for thousands or 'M' for millions. For higher precision volume refer to field 7762. |
| 88 | string | Bid Size | The number of contracts or shares bid for at the bid price. |
| 201 | string | Right | Returns the right of the instrument, such as P for Put or C for Call. |
| 6004 | string | Exchange | Exchange |
| 6008 | integer | Conid | Contract identifier from IBKR's database. |
| 6070 | string | SecType | The asset class of the instrument. |
| 6072 | string | Months | Months |
| 6073 | string | Regular Expiry | Regular Expiry |
| 6119 | string | Marker for market data delivery method | Marker for market data delivery method (similar to request id) |
| 6457 | integer | Underlying Conid | Underlying Conid. Use /trsrv/secdef to get more information about the security |
| 6508 | string | Service Params | Service Params. |
| 6509 | string | Market Data Availability | Market Data Availability. See Market Data Availability section for details. |
| 7051 | string | Company name | Company name |
| 7057 | string | Ask Exch | Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY |
| 7058 | string | Last Exch | Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY |
| 7059 | string | Last Size | The number of unites traded at the last price |
| 7068 | string | Bid Exch | Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY |
| 7084 | string | Implied Vol./Hist. Vol % | The ratio of the implied volatility over the historical volatility, expressed as a percentage. |
| 7085 | string | Put/Call Interest | Put option open interest/call option open interest for the trading day. |
| 7086 | string | Put/Call Volume | Put option volume/call option volume for the trading day. |
| 7087 | string | Hist. Vol. % | 30-day real-time historical volatility. |
| 7088 | string | Hist. Vol. Close % | Shows the historical volatility based on previous close price. |
| 7089 | string | Opt. Volume | Option Volume |
| 7094 | string | Conid + Exchange | Conid + Exchange |
| 7184 | string | canBeTraded | If contract is a trade-able instrument. Returns 1(true) or 0(false). |
| 7219 | string | Contract Description | Contract Description |
| 7220 | string | Contract Description | Contract Description |
| 7221 | string | Listing Exchange | Listing Exchange |
| 7280 | string | Industry | Displays the type of industry under which the underlying company can be categorized. |
| 7281 | string | Category | Displays a more detailed level of description within the industry under which the underlying company can be categorized. |
| 7282 | string | Average Volume | The average daily trading volume over 90 days. |
| 7283 | string | Option Implied Vol. % | A prediction of how volatile an underlying will be in the future. At the market volatility estimated for a maturity thirty calendar days forward of the current trading day, and based on option prices from two consecutive expiration months. |
| 7284 | string | Historical volatility % | Deprecated, see field 7087 |
| 7285 | string | Put/Call Ratio | Put/Call Ratio |
| 7286 | string | Dividend Amount | Displays the amount of the next dividend. |
| 7287 | string | Dividend Yield % | This value is the total of the expected dividend payments over the next twelve months per share divided by the Current Price and is expressed as a percentage. |
| 7288 | string | Ex-date of the dividend | Ex-date of the dividend |
| 7289 | string | Market Cap | Market Cap |
| 7290 | string | P/E | P/E |
| 7291 | string | EPS | EPS |
| 7292 | string | Cost Basis | Your current position in this security multiplied by the average price and multiplier. |
| 7293 | string | 52 Week High | The highest price for the past 52 weeks. |
| 7294 | string | 52 Week Low | The lowest price for the past 52 weeks. |
| 7295 | string | Open | Today's opening price. |
| 7296 | string | Close | Today's closing price. |
| 7308 | string | Delta | The ratio of the change in the price of the option to the corresponding change in the price of the underlying. |
| 7309 | string | Gamma | The rate of change for the delta with respect to the underlying asset's price. |
| 7310 | string | Theta | A measure of the rate of decline the value of an option due to the passage of time. |
| 7311 | string | Vega | The amount that the price of an option changes compared to a 1% change in the volatility. |
| 7607 | string | Opt. Volume Change % | Today's option volume as a percentage of the average option volume. |
| 7633 | string | Implied Vol. % | The implied volatility for the specific strike of the option in percentage. |
| 7635 | string | Mark | The mark price is, the ask price if ask is less than last price, the bid price if bid is more than the last price, otherwise it's equal to last price. |
| 7636 | string | Shortable Shares | Number of shares available for shorting. |
| 7637 | string | Fee Rate | Interest rate charged on borrowed shares. |
| 7638 | string | Option Open Interest | Option Open Interest |
| 7639 | string | % of Mark Value | Displays the market value of the contract as a percentage of the total market value of the account. |
| 7644 | string | Shortable | Describes the level of difficulty with which the security can be sold short. |
| 7655 | string | Morningstar Rating | Displays Morningstar Rating provided value. Requires Morningstar subscription. |
| 7671 | string | Dividends | This value is the total of the expected dividend payments over the next twelve months per share. |
| 7672 | string | Dividends TTM | This value is the total of the expected dividend payments over the last twelve months per share. |
| 7674 | string | EMA(200) | Exponential moving average (N=200). |
| 7675 | string | EMA(100) | Exponential moving average (N=100). |
| 7676 | string | EMA(50) | Exponential moving average (N=50). |
| 7677 | string | EMA(20) | Exponential moving average (N=20). |
| 7678 | string | Price/EMA(200) | Price to Exponential moving average (N=200) ratio -1, displayed in percents. |
| 7679 | string | Price/EMA(100) | Price to Exponential moving average (N=100) ratio -1, displayed in percents. |
| 7724 | string | Price/EMA(50) | Price to Exponential moving average (N=50) ratio -1, displayed in percents. |
| 7681 | string | Price/EMA(20) | Price to Exponential moving average (N=20) ratio -1, displayed in percents. |
| 7682 | string | Change Since Open | The difference between the last price and the open price. |
| 7683 | string | Upcoming Event | Shows the next major company event. Requires Wall Street Horizon subscription. |
| 7684 | string | Upcoming Event Date | The date of the next major company event. Requires Wall Street Horizon subscription. |
| 7685 | string | Upcoming Analyst Meeting | The date and time of the next scheduled analyst meeting. Requires Wall Street Horizon subscription. |
| 7686 | string | Upcoming Earnings | The date and time of the next scheduled earnings/earnings call event. Requires Wall Street Horizon subscription. |
| 7687 | string | Upcoming Misc Event | The date and time of the next shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription. |
| 7688 | string | Recent Analyst Meeting | The date and time of the most recent analyst meeting. Requires Wall Street Horizon subscription. |
| 7689 | string | Recent Earnings | The date and time of the most recent earnings/earning call event. Requires Wall Street Horizon subscription. |
| 7690 | string | Recent Misc Event | The date and time of the most recent shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription. |
| 7694 | string | Probability of Max Return | Customer implied probability of maximum potential gain. |
| 7695 | string | Break Even | Break even points |
| 7696 | string | SPX Delta | Beta Weighted Delta is calculated using the formula; Delta x dollar adjusted beta. |
| 7697 | string | Futures Open Interest | Total number of outstanding futures contracts |
| 7698 | string | Last Yield | Implied yield of the bond if it is purchased at the current last price. |
| 7699 | string | Bid Yield | Implied yield of the bond if it is purchased at the current bid price. |
| 7700 | string | Probability of Max Return | Customer implied probability of maximum potential gain. |
| 7702 | string | Probability of Max Loss | Customer implied probability of maximum potential loss. |
| 7703 | string | Profit Probability | Customer implied probability of any gain. |
| 7704 | string | Organization Type | Organization Type |
| 7705 | string | Debt Class | Debt Class |
| 7706 | string | Ratings | Ratings issued for bond contract. |
| 7707 | string | Bond State Code | Bond State Code |
| 7708 | string | Bond Type | Bond Type |
| 7714 | string | Last Trading Date | Last Trading Date |
| 7715 | string | Issue Date | Issue Date |
| 7718 | string | Beta | Beta is against standard index. |
| 7720 | string | Ask Yield | Implied yield of the bond if it is purchased at the current offer. |
| 7741 | string | Prior Close | Yesterday's closing price |
| 7762 | string | Volume Long | High precision volume for the day. For formatted volume refer to field 87. |
| 7768 | string | hasTradingPermissions | if user has trading permissions for specified contract. Returns 1(true) or 0(false). |
| 7920 | string | Daily PnL Raw | Your profit or loss of the day since prior close. Daily PnL is calculated with real-time market data. |
| 7921 | string | Cost Basis Raw | Your current position in this security multiplied by the average price and multiplier. |

## Unavailable Historical Data
- Bars whose size is 30 seconds or less older than six months
- Expired futures data older than two years counting from the future's expiration date.
- Expired options, FOPs, warrants and structured products.
- End of Day (EOD) data for options, FOPs, warrants and structured products.
- Data for expired future spreads
- Data for securities which are no longer trading.
- Native historical data for combos. Historical data is not stored in the IB database separately for combos.
- Historical data for securities which move to a new exchange will often not be available prior to the time of the move.
- Studies and indicators such as Weighted Moving Averages or Bollinger Bands are not available from the API.
