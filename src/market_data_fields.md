# IBKR Market Data Fields

Market data fields available from the `/iserver/marketdata/snapshot` endpoint, organized by category.

## Price Data
| Field ID | Name | Description |
|----------|------|-------------|
| 31 | Last Price | The last price at which the contract traded. May contain prefixes: C (Previous close), H (Trading halted) |
| 70 | High | Current day high price |
| 71 | Low | Current day low price |
| 82 | Change | The difference between the last price and the close on the previous trading day |
| 83 | Change % | The difference between the last price and the previous close in percentage |
| 84 | Bid Price | The highest-priced bid on the contract |
| 86 | Ask Price | The lowest-priced offer on the contract |
| 7635 | Mark | The mark price (ask if ask < last, bid if bid > last, otherwise last) |
| 7295 | Open | Today's opening price |
| 7296 | Close | Today's closing price |
| 7741 | Prior Close | Yesterday's closing price |
| 7682 | Change Since Open | The difference between the last price and the open price |

## Volume & Size
| Field ID | Name | Description |
|----------|------|-------------|
| 87 | Volume | Volume for the day (formatted with 'K' or 'M') |
| 7762 | Volume Long | High precision volume for the day |
| 88 | Bid Size | Number of contracts/shares bid for at the bid price |
| 85 | Ask Size | Number of contracts/shares offered at the ask price |
| 7059 | Last Size | Number of units traded at the last price |
| 7282 | Average Volume | Average daily trading volume over 90 days |

## Position & PnL
| Field ID | Name | Description |
|----------|------|-------------|
| 73 | Market Value | Current market value of your position (real-time) |
| 74 | Avg Price | Average price of the position |
| 75 | Unrealized PnL | Unrealized profit or loss (real-time) |
| 79 | Realized PnL | Realized profit or loss |
| 78 | Daily PnL | Profit or loss of the day since prior close (real-time) |
| 7920 | Daily PnL Raw | Daily PnL with high precision |
| 80 | Unrealized PnL % | Unrealized profit or loss expressed in percentage |
| 7292 | Cost Basis | Position value (average price × quantity × multiplier) |
| 7921 | Cost Basis Raw | Cost basis with high precision |
| 7639 | % of Mark Value | Market value as percentage of total account value |

## Options Greeks & Volatility
| Field ID | Name | Description |
|----------|------|-------------|
| 7308 | Delta | Ratio of change in option price to change in underlying price |
| 7309 | Gamma | Rate of change for delta with respect to underlying price |
| 7310 | Theta | Rate of decline in option value due to passage of time |
| 7311 | Vega | Option price change per 1% change in volatility |
| 7633 | Implied Vol. % | Implied volatility for the specific option strike |
| 7283 | Option Implied Vol. % | Implied volatility for the underlying (30 days forward) |
| 7087 | Hist. Vol. % | 30-day real-time historical volatility |
| 7284 | Hist. Vol. % | Historical volatility (deprecated, see 7087) |
| 7084 | Implied Vol./Hist. Vol % | Ratio of implied to historical volatility as percentage |
| 7694 | Probability of Max Return | Customer implied probability of maximum potential gain |
| 7700 | Probability of Max Return | Customer implied probability of maximum potential gain |
| 7702 | Probability of Max Loss | Customer implied probability of maximum potential loss |
| 7703 | Profit Probability | Customer implied probability of any gain |
| 7695 | Break Even | Break even points |

## Put/Call Analysis
| Field ID | Name | Description |
|----------|------|-------------|
| 7085 | Put/Call Interest | Put open interest / Call open interest for the trading day |
| 7086 | Put/Call Volume | Put volume / Call volume for the trading day |
| 7285 | Put/Call Ratio | Put/Call ratio |

## Option Volume & Open Interest
| Field ID | Name | Description |
|----------|------|-------------|
| 7089 | Opt. Volume | Option Volume |
| 7607 | Opt. Volume Change % | Today's option volume as percentage of average |
| 7638 | Option Open Interest | Total number of outstanding option contracts |

## Company Fundamentals
| Field ID | Name | Description |
|----------|------|-------------|
| 7051 | Company name | Company name |
| 7280 | Industry | Industry categorization of the underlying company |
| 7281 | Category | More detailed industry description |
| 7289 | Market Cap | Market capitalization |
| 7290 | P/E | Price-to-Earnings ratio |
| 7291 | EPS | Earnings per share |
| 7655 | Morningstar Rating | Morningstar rating (requires subscription) |
| 7704 | Organization Type | Organization type |

## Dividends
| Field ID | Name | Description |
|----------|------|-------------|
| 7286 | Dividend Amount | Amount of the next dividend |
| 7287 | Dividend Yield % | Expected dividend payments / Current Price as percentage |
| 7288 | Ex-date | Ex-dividend date |
| 7671 | Dividends | Expected dividends over next 12 months per share |
| 7672 | Dividends TTM | Dividends over last 12 months per share |

## 52-Week Range
| Field ID | Name | Description |
|----------|------|-------------|
| 7293 | 52 Week High | Highest price for the past 52 weeks |
| 7294 | 52 Week Low | Lowest price for the past 52 weeks |

## Technical Indicators
| Field ID | Name | Description |
|----------|------|-------------|
| 7674 | EMA(200) | Exponential moving average (N=200) |
| 7675 | EMA(100) | Exponential moving average (N=100) |
| 7676 | EMA(50) | Exponential moving average (N=50) |
| 7677 | EMA(20) | Exponential moving average (N=20) |
| 7678 | Price/EMA(200) | Price to EMA(200) ratio minus 1, in percent |
| 7679 | Price/EMA(100) | Price to EMA(100) ratio minus 1, in percent |
| 7724 | Price/EMA(50) | Price to EMA(50) ratio minus 1, in percent |
| 7681 | Price/EMA(20) | Price to EMA(20) ratio minus 1, in percent |

## Short Selling
| Field ID | Name | Description |
|----------|------|-------------|
| 7644 | Shortable | Describes the level of difficulty with which the security can be sold short |
| 7636 | Shortable Shares | Number of shares available for shorting |
| 7637 | Fee Rate | Interest rate charged on borrowed shares |

## Bond Data
| Field ID | Name | Description |
|----------|------|-------------|
| 7698 | Last Yield | Implied yield at current last price |
| 7699 | Bid Yield | Implied yield at current bid price |
| 7720 | Ask Yield | Implied yield at current ask price |
| 7706 | Ratings | Ratings issued for bond contract |
| 7705 | Debt Class | Debt class |
| 7708 | Bond Type | Bond type |
| 7707 | Bond State Code | Bond state code |
| 7715 | Issue Date | Bond issue date |
| 7714 | Last Trading Date | Last trading date |

## Beta & Index
| Field ID | Name | Description |
|----------|------|-------------|
| 7718 | Beta | Beta against standard index |
| 7696 | SPX Delta | Beta Weighted Delta |

## Futures
| Field ID | Name | Description |
|----------|------|-------------|
| 7697 | Futures Open Interest | Total number of outstanding futures contracts |

## Contract Information
| Field ID | Name | Description |
|----------|------|-------------|
| 55 | Symbol | Symbol |
| 58 | Text | Text description |
| 6008 | Conid | Contract identifier from IBKR's database |
| 6070 | SecType | Asset class of the instrument |
| 6072 | Months | Months |
| 6073 | Regular Expiry | Regular expiry |
| 201 | Right | Right of the instrument (P for Put, C for Call) |
| 6457 | Underlying Conid | Underlying contract identifier |
| 7184 | canBeTraded | Returns 1 (true) or 0 (false) |
| 7768 | hasTradingPermissions | Returns 1 (true) or 0 (false) |
| 7219 | Contract Description | Contract description |
| 7220 | Contract Description | Contract description |
| 7221 | Listing Exchange | Listing exchange |
| 6004 | Exchange | Exchange |
| 7094 | Conid + Exchange | Conid combined with exchange |

## Market Data Status
| Field ID | Name | Description |
|----------|------|-------------|
| 6509 | Market Data Availability | See Market Data Availability section |
| 6508 | Service Params | Service parameters |
| 6119 | Marker for market data delivery | Marker for market data delivery method |

## Exchange Information
| Field ID | Name | Description |
|----------|------|-------------|
| 7057 | Ask Exch | Exchange offering the SMART ask price |
| 7058 | Last Exch | Exchange offering the SMART last price |
| 7068 | Bid Exch | Exchange offering the SMART bid price |

## Corporate Events (Required Wall Street Horizon subscription)
| Field ID | Name | Description |
|----------|------|-------------|
| 7683 | Upcoming Event | Next major company event |
| 7684 | Upcoming Event Date | Date of the next major company event |
| 7685 | Upcoming Analyst Meeting | Date/time of next analyst meeting |
| 7686 | Upcoming Earnings | Date/time of next earnings event |
| 7687 | Upcoming Misc Event | Date/time of next shareholder meeting/presentation |
| 7688 | Recent Analyst Meeting | Date/time of most recent analyst meeting |
| 7689 | Recent Earnings | Date/time of most recent earnings event |
| 7690 | Recent Misc Event | Date/time of most recent shareholder meeting/presentation |

## Market Data Availability Codes
| Code | Name | Description |
|------|------|-------------|
| R | RealTime | Data is relayed back in real time without delay, market data subscription(s) are required |
| D | Delayed | Data is relayed back 15-20 min delayed |
| Z | Frozen | Last recorded data at market close, relayed back in real time |
| Y | Frozen Delayed | Last recorded data at market close, relayed back delayed |
| N | Not Subscribed | User does not have the required market data subscription(s) |
| O | Incomplete Acknowledgement | Annual Market Data API Acknowledgement not completed |
| P | Snapshot | Snapshot request is available for contract |
| p | Consolidated | Market data is aggregated across multiple exchanges/venues |
| B | Book | Top of the book data is available for contract |
| d | Performance Details | Additional performance details available (internal use) |

The field may contain three chars:
- First char: Timeline (R=RealTime, D=Delayed, Z=Frozen, Y=Frozen Delayed, N=Not Subscribed)
- Second char: Structure (P=Snapshot, p=Consolidated)
- Third char: Type (B=Book)
