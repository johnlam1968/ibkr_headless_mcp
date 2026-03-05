# IBKR Market Data Fields (Original Reference) - edited

Market data fields available from the `/iserver/marketdata/snapshot` endpoint. Fields are sorted by Field ID.
Focusing on underlying asset watchlist, irrelevant fields are deleted.

## Field Reference
| Field ID | Return Type | Name | Description |
|----------|-------------|------|-------------|
| 31 | string | Last Price | The last price at which the contract traded. May contain one of the following prefixes: C – Previous day's closing price. H – Trading has halted. |
| 55 | string | Symbol | Symbol |
| 70 | string | High | Current day high price |
| 71 | string | Low | Current day low price |
| 82 | string | Change | The difference between the last price and the close on the previous trading day |
| 83 | string | Change % | The difference between the last price and the close on the previous trading day in percentage. |
| 84 | string | Bid Price | The highest-priced bid on the contract. |
| 86 | string | Ask Price | The lowest-priced offer on the contract. |
| 87 | string | Volume | Volume for the day, formatted with 'K' for thousands or 'M' for millions. For higher precision volume refer to field 7762. |
| 6008 | integer | Conid | Contract identifier from IBKR's database. |
| 6070 | string | SecType | The asset class of the instrument. |
| 6457 | integer | Underlying Conid | Underlying Conid. Use /trsrv/secdef to get more information about the security |
| 7051 | string | Company name | Company name |
| 7084 | string | Implied Vol./Hist. Vol % | The ratio of the implied volatility over the historical volatility, expressed as a percentage. |
| 7085 | string | Put/Call Interest | Put option open interest/call option open interest for the trading day. |
| 7086 | string | Put/Call Volume | Put option volume/call option volume for the trading day. |
| 7087 | string | Hist. Vol. % | 30-day real-time historical volatility. |
| 7088 | string | Hist. Vol. Close % | Shows the historical volatility based on previous close price. |
| 7089 | string | Opt. Volume | Option Volume |
| 7282 | string | Average Volume | The average daily trading volume over 90 days. |
| 7283 | string | Option Implied Vol. % | A prediction of how volatile an underlying will be in the future. At the market volatility estimated for a maturity thirty calendar days forward of the current trading day, and based on option prices from two consecutive expiration months. |
| 7285 | string | Put/Call Ratio | Put/Call Ratio |
| 7289 | string | Market Cap | Market Cap |
| 7290 | string | P/E | P/E |
| 7291 | string | EPS | EPS |
| 7293 | string | 52 Week High | The highest price for the past 52 weeks. |
| 7294 | string | 52 Week Low | The lowest price for the past 52 weeks. |
| 7295 | string | Open | Today's opening price. |
| 7296 | string | Close | Today's closing price. |
| 7607 | string | Opt. Volume Change % | Today's option volume as a percentage of the average option volume. |
| 7633 | string | Implied Vol. % | The implied volatility for the specific strike of the option in percentage. |
| 7638 | string | Option Open Interest | Option Open Interest |
| 7644 | string | Shortable | Describes the level of difficulty with which the security can be sold short. |
| 7655 | string | Morningstar Rating | Displays Morningstar Rating provided value. Requires Morningstar subscription. |
| 7674 | string | EMA(200) | Exponential moving average (N=200). |
| 7675 | string | EMA(100) | Exponential moving average (N=100). |
| 7676 | string | EMA(50) | Exponential moving average (N=50). |
| 7677 | string | EMA(20) | Exponential moving average (N=20). |
| 7682 | string | Change Since Open | The difference between the last price and the open price. |
| 7683 | string | Upcoming Event | Shows the next major company event. Requires Wall Street Horizon subscription. |
| 7684 | string | Upcoming Event Date | The date of the next major company event. Requires Wall Street Horizon subscription. |
| 7685 | string | Upcoming Analyst Meeting | The date and time of the next scheduled analyst meeting. Requires Wall Street Horizon subscription. |
| 7686 | string | Upcoming Earnings | The date and time of the next scheduled earnings/earnings call event. Requires Wall Street Horizon subscription. |
| 7687 | string | Upcoming Misc Event | The date and time of the next shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription. |
| 7688 | string | Recent Analyst Meeting | The date and time of the most recent analyst meeting. Requires Wall Street Horizon subscription. |
| 7689 | string | Recent Earnings | The date and time of the most recent earnings/earning call event. Requires Wall Street Horizon subscription. |
| 7690 | string | Recent Misc Event | The date and time of the most recent shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription. |
| 7718 | string | Beta | Beta is against standard index. |
| 7741 | string | Prior Close | Yesterday's closing price |
| 7762 | string | Volume Long | High precision volume for the day. For formatted volume refer to field 87. |

