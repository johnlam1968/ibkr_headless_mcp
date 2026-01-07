source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/
## Search the security definition by Contract ID
Returns a list of security definitions for the given conids

GET /trsrv/secdef

 

Request Object
Query Prams
conids: int*. Required
A comma separated series of contract IDs.
Value Format: 1234

Python
cURL
request_url = f"{baseUrl}/trsrv/secdef?conids=265598"
requests.get(url=request_url)
 

Response Object
secdef: array.
Returns the contents of the request with the array.

conid: int.
Returns the conID

currency: String.
Returns the traded currency for the contract.

time: int.
Returns amount of time in ms to generate the data.

chineseName: String.
Returns the Chinese characters for the symbol.

allExchanges: String*.
Returns a series of exchanges the given symbol can trade on.

listingExchange: String.
Returns the primary or listing exchange the contract is hosted on.

countryCode: String.
Returns the country code the contract is traded on.

name: String.
Returns the comapny name.

assetClass: String.
Returns the asset class or security type of the contract.

expiry: String.
Returns the expiry of the contract. Returns null for non-expiry instruments.

lastTradingDay: String.
Returns the last trading day of the contract.

group: String.
Returns the group or industry the contract is affilated with.

putOrCall: String.
Returns if the contract is a Put or Call option.

sector: String.
Returns the contract’s sector.

sectorGroup: String.
Returns the sector’s group.

strike: String.
Returns the strike of the contract.

ticker: String.
Returns the ticker symbol of the traded contract.

undConid: int.
Returns the contract’s underlyer.

multiplier: float,
Returns the contract multiplier.

type: String.
Returns stock type.

hasOptions: bool.
Returns if contract has tradable options contracts.

fullName: String.
Returns symbol name for requested contract.

isUS: bool.
Returns if the contract is US based or not.

incrementRules & displayRule: Array.
Returns rules regarding incrementation for order placement. Not functional for all exchanges. Please see /iserver/contract/rules for more accurate rule details.

isEventContract: bool.
Returns if the contract is an event contract or not.

pageSize: int.
Returns the content size of the request.

 

## Contract information by Contract ID
Requests full contract details for the given conid

GET /iserver/contract/{conid}/info

 

Request Object
Path Params:
conid: String.
Contract ID for the desired contract information.

Python
cURL
request_url = f"{baseUrl}/iserver/contract/265598/info"
requests.get(url=request_url)
 

Response Object
conid: int.
Contract ID of the requested contract.

ticker: String.
Ticker symbol of the requested contract.

secType: String.
Security type of the requested contract.

listingExchange: String.
Primary exchange of the requested contract.

exchange: String.
Traded exchange of the requested contract set in the request.

companyName: String.
Company name of the requested contract.

currency: String.
National currency of the requested contract.

validExchanges: String.
All valid exchanges of the requested contract.

priceRendering: String.
Render price of the requested contract.

maturityDate: String.
Maturity, or expiration date, of the requested contract.

right: String.
Right, put or call, of the requested contract.

strike: int.
Strike price of the requested contract.


## Currency Pairs
Obtains available currency pairs corresponding to the given target currency.

GET /iserver/currency/pairs

 

Request Object
Query Params
currency: String. Required
Specify the target currency you would like to receive official pairs of.
Valid Structure: “USD”

Python
cURL
request_url = f"{baseUrl}/iserver/currency/pairs?currency=USD"
requests.get(url=request_url)
 

Response Object
{{currency}}: List of Objects.
[{
symbol: String.
The official symbol of the given currency pair.

conid: int.
The official contract identifier of the given currency pair.

ccyPair: String.
Returns the counterpart of
}]

{
  "USD": [
    {
      "symbol": "USD.SGD",
      "conid": 37928772,
      "ccyPair": "SGD"
    },
  {...},
    {
      "symbol": "USD.RUB",
      "conid": 28454968,
      "ccyPair": "RUB"
    }
  ]
}
 

## Currency Exchange Rate
Obtains the exchange rates of the currency pair.

GET /iserver/exchangerate

 

Request Object
Query Params
Source: String. Required
Specify the base currency to request data for.
Valid Structure: “AUD”

Target: String. Required
Specify the quote currency to request data for.
Valid Structure: “USD”

Python
cURL
request_url = f"{baseUrl}/iserver/exchangerate?target=AUD&source=USD"
requests.get(url=request_url)
 

Response Object
rate: float.
Returns the exchange rate for the currency pair.

{
    "rate": 0.67005002
}
 

## Find all Info and Rules for a given contract
Returns both contract info and rules from a single endpoint.
For only contract rules, use the endpoint /iserver/contract/rules.
For only contract info, use the endpoint /iserver/contract/{conid}/info.

GET /iserver/contract/{{ conid }}/info-and-rules

 

Request Object
Path Parameters
coind: String. Required
Contract identifier for the given contract.

Query Parameters
isBuy: bool.
Indicates whether you are searching for Buy or Sell order rules.
Set to true for Buy Orders, set to false for Sell Orders

Python
cURL
request_url = f"{baseUrl}/iserver/contract/265598/info-and-rules?isBuy=true"
requests.get(url=request_url)
 

Response Object
cfi_code: String.
Classification of Financial Instrument codes

symbol: String.
Underlying symbol

cusip: String.
Returns the CUSIP for the given instrument.
Only used in BOND trading.

expiry_full: String.
Returns the expiration month of the contract.
Formatted as “YYYYMM”

con_id: int.
Indicates the contract identifier of the given contract.

maturity_date: String.
Indicates the final maturity date of the given contract.
Formatted as “YYYYMMDD”

industry: String.
Specific group of companies or businesses.

instrument_type: String.
Asset class of the instrument.

trading_class: String.
Designated trading class of the contract.

valid_exchanges: String.
Comma separated list of support exchanges or trading venues.

allow_sell_long: bool.
Allowed to sell shares you own.

is_zero_commission_security: bool.
Indicates if the contract supports zero commission trading.

local_symbol: String.
Contract’s symbol from primary exchange. For options it is the OCC symbol.

contract_clarification_type: null

classifier: null.

currency: String.
Base currency contract is traded in.

text: String.
Indicates the display name of the contract, as shown with Client Portal.

underlying_con_id: int.
Underlying contract identifier for the requested contract.

r_t_h: bool.
Indicates if the contract can be traded outside regular trading hours or not.

multiplier: String.
Indicates the multiplier of the contract.

underlying_issuer: String.
Indicates the issuer of the underlying.

contract_month: String.
Indicates the year and month the contract expires.
Value Format: “YYYYMM”

company_name: String.
Indicates the name of the company or index.

smart_available: bool.
Indicates if the contract can be smart routed or not.

exchange: String.
Indicates the primary exchange for which the contract can be traded.

category: String.
Indicates the industry category of the instrument.

rules: Object.
See the /iserver/contract/rules endpoint.


## Search Bond Filter Information
Request a list of filters relating to a given Bond issuerID. The issuerId is retrieved from /iserver/secdef/search and can be used in /iserver/secdef/info?issuerId={{ issuerId }} for retrieving conIds.

/iserver/secdef/bond-filters

 

Request Object
Query Params
symbol: String. Required
This should always be set to “BOND”

issuerId: String. Required
Specifies the issuerId value used to designate the bond issuer type.

Python
cURL
request_url = f"{baseUrl}/iserver/secdef/bond-filters?symbol=BOND&issuerId=e1400715"
requests.get(url=request_url)
 

bondFilters: Array of Objects.
Contains all filters pertaining to the given issuerId.
[{
displayText: String.
An identifier used to document returned options/values. This can be thought of as a key value.

columnId: int.
Used for user interfaces. Internal use only.

options: Array of objects.
Contains all objects with values corresponding to the parent displayText key.
[{
text: String.
In some instances, a text value will be returned, which indicates the standardized value format such as plaintext dates, rather than solely numerical values.

value: String.
Returns value directly correlating to the displayText key. This may include exchange, maturity date, issue date, coupon, or currency.

}]

}]

{
  "bondFilters": [
    {
      "displayText": "Exchange",
      "columnId": 0,
      "options": [
      {
        "value": "SMART"
      }]
    },
    {
      "displayText": "Maturity Date",
      "columnId": 27,
      "options": [
        {
          "text": "Jan 2025",
          "value": "202501"
      }]
    },
    {
      "displayText": "Issue Date",
      "columnId": 28,
      "options": [{
        "text": "Sep 18 2014",
        "value": "20140918"
      }]
    },
    {
      "displayText": "Coupon",
      "columnId": 25,
      "options": [{
        "value": "1.301"
      }]
    },
    {
      "displayText": "Currency",
      "columnId": 5,
      "options": [{
        "value": "EUR"
      }]
    }
  ]
}
 

## Search Contract by Symbol
Search by underlying symbol or company name. Relays back what derivative contract(s) it has. This endpoint must be called before using /secdef/info.

For bonds, enter the family type in the symbol field to receive the issuerID used in the /iserver/secdef/info endpoint.

GET /iserver/secdef/search

 

Request Object
Query Params
symbol: String. Required
Underlying symbol of interest. May also pass company name if ‘name’ is set to true, or bond issuer type to retrieve bonds.

name: bool.
Determines if symbol reflects company name or ticker symbol. If company name is included will only receive limited response: conid, companyName, companyHeader and symbol. The inclusion of the name field will prohibit the /iserver/secdef/strikes endpoint from returning data. After retrieving your expected contract, customers looking to create option chains should remove the name field from the request.

secType: String.
Valid Values: “STK”, “IND”, “BOND”
Declares underlying security type.

 

Python
cURL
request_url = f"{baseUrl}/iserver/secdef/search?symbol=Interactive Brokers&name=true"
requests.get(url=request_url)
 

Response Object
“conid”: String.
Conid of the given contract.

“companyHeader”: String.
Extended company name and primary exchange.

“companyName”: String.
Name of the company.

“symbol”: String.
Company ticker symbol.

“description”: String.
Primary exchange of the contract.

“restricted”: bool.
Returns if the contract is available for trading.

“sections”: Array of objects

“secType”: String.
Given contracts security type.

“months”: String.
Returns a string of dates, separated by semicolons.
Value Format: “JANYY;FEBYY;MARYY”

“symbol”: String.
Symbol of the instrument.

“exchange”: String.
Returns a string of exchanges, separated by semicolons.
Value Format: “EXCH;EXCH;EXCH”

Unique for Bonds
“issuers”: Array of objects
Array of objects containing the id and name for each bond issuer.

“id”: String.
Issuer Id for the given contract.

“name”: String.
Name of the issuer.

“bondid”: int.
Bond type identifier.

“conid”: String.
Contract ID for the given bond.

“companyHeader”: String.
Name of the bond type
Value Format: “Corporate Fixed Income”

“companyName”: null
Returns ‘null’ for bond contracts.

“symbol”:null
Returns ‘null’ for bond contracts.

“description”:null
Returns ‘null’ for bond contracts.

“restricted”:null
Returns ‘null’ for bond contracts.

“fop”:null
Returns ‘null’ for bond contracts.

“opt”:null
Returns ‘null’ for bond contracts.

“war”:null
Returns ‘null’ for bond contracts.

“sections”: Array of objects
Only relays “secType”:”BOND” in the Bonds section.



## Search SecDef information by conid
Provides Contract Details of Futures, Options, Warrants, Cash and CFDs based on conid.

For all instruments, /iserver/secdef/search must be called first.

For derivatives such as Options, Warrants, and Futures Options, you will need to query /iserver/secdef/strikes as well.

GET /iserver/secdef/info

 

Request Object
Query Parameters
conid: String. Required
Contract identifier of the underlying. May also pass the final derivative conid directly.

sectype: String. Required
Security type of the requested contract of interest.

month: String. Required for Derivatives
Expiration month for the given derivative.

exchange: String. Optional
Designate the exchange you wish to receive information for in relation to the contract.

strike: String. Required for Options and Futures Options
Set the strike price for the requested contract details

right: String. Required for Options
Set the right for the given contract.
Value Format: “C” for Call or “P” for Put.

issuerId: String. Required for Bonds
Set the issuerId for the given bond issuer type.
Example Format: “e1234567”

Python
cURL
request_url = f"{baseUrl}/iserver/secdef/info?conid=265598&secType=OPT&month=JAN24&strike=195&right=P"
requests.get(url=request_url)
 

Response Object
conid: int.
Contract Identifier of the given contract

ticker: String
Ticker symbol for the given contract

secType: String.
Security type for the given contract.

listingExchange: String.
Primary listing exchange for the given contract.

exchange: String.
Exchange requesting data for.

companyName: String.
Name of the company for the given contract.

currency: String
Traded currency allowed for the given contract.

validExchanges: String*
Series of all valid exchanges the contract can be traded on in a single comma-separated string.
priceRendering: null.

maturityDate: String
Date of expiration for the given contract.

right: String.
Right (P or C) for the given contract.

strike: Float.
Returns the given strike value for the given contract.


## Search Strikes by Underlying Contract ID
Query to receive a list of potential strikes supported for a given underlying.

This endpoint will always return empty arrays unless /iserver/secdef/search is called for the same underlying symbol beforehand. The inclusion of the name field with the /iserver/secdef/search endpoint will prohibit the strikes endpoint from returning data. After retrieving your expected contract from the initial search, developers looking to create option chains should remove the name field from the request.

 

GET /iserver/secdef/strikes

Request Object
Query Parameters
conid: String. Required
Contract Identifier number for the underlying

sectype: String. Required
Security type of the derivatives you are looking for.
Value Format: “OPT” or “WAR”

month: String. Required
Expiration month and year for the given underlying
Value Format: {3 character month}{2 character year}
Example: AUG23

exchange: String. Optional
Exchange from which derivatives should be retrieved from.
Default value is set to SMART

Python
cURL
request_url = f"{baseUrl}/iserver/secdef/strikes?conid=265598&sectype=OPT&month=JAN24&exchange=SMART"
requests.get(url=request_url)
 

Response Object

call: Array of Floats
Array containing a series of comma separated float values representing potential call strikes for the instrument.

put: Array of Floats
Array containing a series of comma separated float values representing potential put strikes for the instrument.

 

## Security Future by Symbol
Returns a list of non-expired future contracts for given symbol(s)

GET /trsrv/futures

 

Request Object
Query Params
symbols: String. Required
Indicate the symbol(s) of the underlier you are trying to retrieve futures on. Accepts comma delimited string of symbols.

Python
cURL
request_url = f"{baseUrl}/trsrv/futures?symbols=ES,MES"
requests.get(url=request_url)
 

Response Body
symbol: Array
Displayed as the string of your symbol
Contains a series of objects for each symbol that matches the requested.

symbol: String.
The requested symbol value.

conid: int.
Contract identifier for the specific symbol

underlyingConid: int.
Contract identifier for the future’s underlying contract.

expirationDate: int.
Expiration date of the specific future contract.

ltd: int.
Last trade date of the future contract.

shortFuturesCutOff: int.
Represents the final day for contract rollover for shorted futures.

longFuturesCutOff: int.
Represents the final day for contract rollover for long futures.

 

## Security Stocks by Symbol
Returns an object contains all stock contracts for given symbol(s)

GET /trsrv/stocks

 

Request Object
Query Params
symbols: String.
Comma-separated list of stock symbols. Symbols must contain only capitalized letters.

Python
cURL
request_url = f"{baseUrl}/trsrv/stocks?symbols=AAPL,IBKR"
requests.get(url=request_url)
 

Response Object
symbol: Array of Json
Contains a series of Json for all contracts that match the symbol.

name: String.
Full company name for the given contract.

chineseName: String.
Chinese name for the given company.

assetClass: String.
Asset class for the given company.

contracts: Array.
A series of arrays pertaining to the same company listed by “name”.
Typically differentiated based on currency of the primary exchange.

conid: int.
Contract ID for the specific contract.

exchange: String.
Primary exchange for the given contract.

isUS: bool.
States whether the contract is hosted in the United States or not.


## Trading Schedule by Symbol
Returns the trading schedule up to a month for the requested contract

GET /trsrv/secdef/schedule

 

Request Object
Query Params
assetClass: String. Required
Specify the security type of the given contract.
Value Formats: Stock: STK, Option: OPT, Future: FUT, Contract For Difference: CFD, Warrant: WAR, Forex: SWP, Mutual Fund: FND, Bond: BND, Inter-Commodity Spreads: ICS

conid: String. Required
Provide the contract identifier to retrieve the trading schedule for.

symbol: String. Required
Specify the symbol for your contract.

exchange: String.
Specify the primary exchange of your contract.

exchangeFilter: String.
Specify exchange you want to retrieve data from.

Python
cURL
request_url = f"{baseUrl}/trsrv/secdef//schedule?assetClass=STK&conid=265598&symbol=AAPL&exchange=ISLAND&exchangeFilter=ISLAND"
requests.get(url=requests_url)
 

Response Object
id: String.
Exchange parameter id

tradeVenueId: String.
Reference on a trade venue of given exchange parameter

schedules: Array of Objets.
Always contains at least one ‘tradingTime’ and zero or more ‘sessionTime’ tags

clearingCycleEndTime: int.
End of clearing cycle.

tradingScheduleDate: int.
Date of the clearing schedule.
20000101 stands for any Sat, 20000102 stands for any Sun, … 20000107 stands for any Fri. Any other date stands for itself.

sessions: Object.
description: String.
If the LIQUID hours differs from the total trading day then a separate ‘session’ tag is returned.

openingTime: int.
Opening date time of the session.

closingTime: int.
Closing date time of the sesion.

prop: String.
If the whole trading day is considered LIQUID then the value ‘LIQUID’ is returned.

tradingTimes: Object.
Object containing trading times.

description: String
Returns tradingTime in exchange time zone.

openingTime: int.
Opening time of the trading day.

closingTime: int.
Closing time of the trading day.

cancelDayOrders: string.
Cancel time for day orders.

## Live Market Data Snapshot
Get Market Data for the given conid(s).

A pre-flight request must be made prior to ever receiving data. For some fields, it may take more than a few moments to receive information.

See response fields for a list of available fields that can be request via fields argument.

The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot.

For derivative contracts the endpoint /iserver/secdef/search must be called first.

GET /iserver/marketdata/snapshot
 

Request Object
Query Parameters
conids: String. Required
Contract identifier for the contract of interest. A maximum of 100 conids may be specified.
May provide a comma-separated series of contract identifiers.

fields: String. Required
Specify a series of tick values to be returned. A maximum of 50 fields may be specified.
May provide a comma-separated series of field ids.
See Market Data Fields for more information.

Python
cURL
request_url = f"{baseUrl}/iserver/marketdata/snapshot?conids=265598,8314&fields=31,84,86"
requests.get(url=request_url)
 

Response Object
server_id: String.
Returns the request’s identifier.

conidEx: String.
Returns the passed conid field. May include exchange if specified in request.

conid: int.
Returns the contract id of the request

_updated: int*.
Returns the epoch time of the update in a 13 character integer .

6119: String.
Field value of the server_id. Returns the request’s identifier.

fields*: String.
Returns a response for each request. Some fields not be as readily available as others. See the Market Data section for more details.

6509: String.
Returns a multi-character value representing the Market Data Availability.




## Market Data Availability
The field may contain three chars.

First character defines market data timeline. This includes:  R = RealTime, D = Delayed, Z = Frozen, Y = Frozen Delayed, N = Not Subscribed.

Second character defines the data structure. This includes: P = Snapshot, p = Consolidated.

Third character defines the type of data: This will always return: B = Book

Code	Name	Description
R	RealTime	Data is relayed back in real time without delay, market data subscription(s) are required.
D	Delayed	Data is relayed back 15-20 min delayed.
Z	Frozen	Last recorded data at market close, relayed back in real time.
Y	Frozen Delayed	Last recorded data at market close, relayed back delayed.
N	Not Subscribed	User does not have the required market data subscription(s) to relay back either real time or delayed data.
O	Incomplete Market Data API Acknowledgement	The annual Market Data API Acknowledgement has not been completed for the given user.
P	Snapshot	Snapshot request is available for contract.
p	Consolidated	Market data is aggregated across multiple exchanges or venues.
B	Book	Top of the book data is available for contract.
d	Performance Details Enabled	Additional performance details are available for this contract. Internal use intended.

## Market Data Fields
Field	Return Type	Value	Description
31	string	Last Price	The last price at which the contract traded. May contain one of the following prefixes: C – Previous day’s closing price. H – Trading has halted.
55	string	Symbol	
58	string	Text	
70	string	High	Current day high price
71	string	Low	Current day low price
73	string	Market Value	The current market value of your position in the security. Market Value is calculated with real time market data (even when not subscribed to market data).
74	string	Avg Price	The average price of the position.
75	string	Unrealized PnL	Unrealized profit or loss. Unrealized PnL is calculated with real time market data (even when not subscribed to market data).
76	string	Formatted position	
77	string	Formatted Unrealized PnL	
78	string	Daily PnL	Your profit or loss of the day since prior close. Daily PnL is calculated with real time market data (even when not subscribed to market data).
79	string	Realized PnL	Realized profit or loss. Realized PnL is calculated with real time market data (even when not subscribed to market data).
80	string	Unrealized PnL %	Unrealized profit or loss expressed in percentage.
82	string	Change	The difference between the last price and the close on the previous trading day
83	string	Change %	The difference between the last price and the close on the previous trading day in percentage.
84	string	Bid Price	The highest-priced bid on the contract.
85	string	Ask Size	The number of contracts or shares offered at the ask price.
86	string	Ask Price	The lowest-priced offer on the contract.
87	string	Volume	Volume for the day, formatted with ‘K’ for thousands or ‘M’ for millions. For higher precision volume refer to field 7762.
88	string	Bid Size	The number of contracts or shares bid for at the bid price.
201	string	Right	Returns the right of the instrument, such as P for Put or C for Call.
6004	string	Exchange	
6008	integer	Conid	Contract identifier from IBKR’s database.
6070	string	SecType	The asset class of the instrument.
6072	string	Months	
6073	string	Regular Expiry	
6119	string	Marker for market data delivery method (similar to request id)	
6457	integer	Underlying Conid. Use /trsrv/secdef to get more information about the security	
6508	string	Service Params.	
6509	string	Market Data Availability. The field may contain three chars. First char defines: R = RealTime, D = Delayed, Z = Frozen, Y = Frozen Delayed, N = Not Subscribed, i – incomplete, v – VDR Exempt (Vendor Display Rule 603c). Second char defines: P = Snapshot, p = Consolidated. Third char defines: B = Book. RealTime	Data is relayed back in real time without delay, market data subscription(s) are required. Delayed – Data is relayed back 15-20 min delayed. Frozen – Last recorded data at market close, relayed back in real time. Frozen Delayed – Last recorded data at market close, relayed back delayed. Not Subscribed – User does not have the required market data subscription(s) to relay back either real time or delayed data. Snapshot – Snapshot request is available for contract. Consolidated – Market data is aggregated across multiple exchanges or venues. Book – Top of the book data is available for contract.
7051	string	Company name	
7057	string	Ask Exch	Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
7058	string	Last Exch	Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
7059	string	Last Size	The number of unites traded at the last price
7068	string	Bid Exch	Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
7084	string	Implied Vol./Hist. Vol %	The ratio of the implied volatility over the historical volatility, expressed as a percentage.
7085	string	Put/Call Interest	Put option open interest/call option open interest for the trading day.
7086	string	Put/Call Volume	Put option volume/call option volume for the trading day.
7087	string	Hist. Vol. %	30-day real-time historical volatility.
7088	string	Hist. Vol. Close %	Shows the historical volatility based on previous close price.
7089	string	Opt. Volume	Option Volume
7094	string	Conid + Exchange	
7184	string	canBeTraded	If contract is a trade-able instrument. Returns 1(true) or 0(false).
7219	string	Contract Description	
7220	string	Contract Description	
7221	string	Listing Exchange	
7280	string	Industry	Displays the type of industry under which the underlying company can be categorized.
7281	string	Category	Displays a more detailed level of description within the industry under which the underlying company can be categorized.
7282	string	Average Volume	The average daily trading volume over 90 days.
7283	string	Option Implied Vol. %	A prediction of how volatile an underlying will be in the future.At the market volatility estimated for a maturity thirty calendar days forward of the current trading day, and based on option prices from two consecutive expiration months. To query the Implied Vol. % of a specific strike refer to field 7633.
7284	string	Historical volatility %	Deprecated, see field 7087
7285	string	Put/Call Ratio	
7286	string	Dividend Amount	Displays the amount of the next dividend.
7287	string	Dividend Yield %	This value is the toal of the expected dividend payments over the next twelve months per share divided by the Current Price and is expressed as a percentage. For derivatives, this displays the total of the expected dividend payments over the expiry date
7288	string	Ex-date of the dividend	
7289	string	Market Cap	
7290	string	P/E	
7291	string	EPS	
7292	string	Cost Basis	Your current position in this security multiplied by the average price and multiplier.
7293	string	52 Week High	The highest price for the past 52 weeks.
7294	string	52 Week Low	The lowest price for the past 52 weeks.
7295	string	Open	Today’s opening price.
7296	string	Close	Today’s closing price.
7308	string	Delta	The ratio of the change in the price of the option to the corresponding change in the price of the underlying.
7309	string	Gamma	The rate of change for the delta with respect to the underlying asset’s price.
7310	string	Theta	A measure of the rate of decline the value of an option due to the passage of time.
7311	string	Vega	The amount that the price of an option changes compared to a 1% change in the volatility.
7607	string	Opt. Volume Change %	Today’s option volume as a percentage of the average option volume.
7633	string	Implied Vol. %	The implied volatility for the specific strike of the option in percentage. To query the Option Implied Vol. % from the underlying refer to field 7283.
7635	string	Mark	The mark price is, the ask price if ask is less than last price, the bid price if bid is more than the last price, otherwise it’s equal to last price.
7636	string	Shortable Shares	Number of shares available for shorting.
7637	string	Fee Rate	Interest rate charged on borrowed shares.
7638	string	Option Open Interest	
7639	string	% of Mark Value	Displays the market value of the contract as a percentage of the total market value of the account. Mark Value is calculated with real time market data (even when not subscribed to market data).
7644	string	Shortable	Describes the level of difficulty with which the security can be sold short.
7655	string	Morningstar Rating	Displays Morningstar Rating provided value. Requires Morningstar subscription.
7671	string	Dividends	This value is the total of the expected dividend payments over the next twelve months per share.
7672	string	Dividends TTM	This value is the total of the expected dividend payments over the last twelve months per share.
7674	string	EMA(200)	Exponential moving average (N=200).
7675	string	EMA(100)	Exponential moving average (N=100).
7676	string	EMA(50)	Exponential moving average (N=50).
7677	string	EMA(20)	Exponential moving average (N=20).
7678	string	Price/EMA(200)	Price to Exponential moving average (N=200) ratio -1, displayed in percents.
7679	string	Price/EMA(100)	Price to Exponential moving average (N=100) ratio -1, displayed in percents.
7724	string	Price/EMA(50)	Price to Exponential moving average (N=50) ratio -1, displayed in percents.
7681	string	Price/EMA(20)	Price to Exponential moving average (N=20) ratio -1, displayed in percents.
7682	string	Change Since Open	The difference between the last price and the open price.
7683	string	Upcoming Event	Shows the next major company event. Requires Wall Street Horizon subscription.
7684	string	Upcoming Event Date	The date of the next major company event. Requires Wall Street Horizon subscription.
7685	string	Upcoming Analyst Meeting	The date and time of the next scheduled analyst meeting. Requires Wall Street Horizon subscription.
7686	string	Upcoming Earnings	The date and time of the next scheduled earnings/earnings call event. Requires Wall Street Horizon subscription.
7687	string	Upcoming Misc Event	The date and time of the next shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription.
7688	string	Recent Analyst Meeting	The date and time of the most recent analyst meeting. Requires Wall Street Horizon subscription.
7689	string	Recent Earnings	The date and time of the most recent earnings/earning call event. Requires Wall Street Horizon subscription.
7690	string	Recent Misc Event	The date and time of the most recent shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription.
7694	string	Probability of Max Return	Customer implied probability of maximum potential gain.
7695	string	Break Even	Break even points
7696	string	SPX Delta	Beta Weighted Delta is calculated using the formula; Delta x dollar adjusted beta, where adjusted beta is adjusted by the ratio of the close price.
7697	string	Futures Open Interest	Total number of outstanding futures contracts
7698	string	Last Yield	Implied yield of the bond if it is purchased at the current last price. Last yield is calculated using the Last price on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
7699	string	Bid Yield	Implied yield of the bond if it is purchased at the current bid price. Bid yield is calculated using the Ask on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
7700	string	Probability of Max Return	Customer implied probability of maximum potential gain.
7702	string	Probability of Max Loss	Customer implied probability of maximum potential loss.
7703	string	Profit Probability	Customer implied probability of any gain.
7704	string	Organization Type	
7705	string	Debt Class	
7706	string	Ratings	Ratings issued for bond contract.
7707	string	Bond State Code	
7708	string	Bond Type	
7714	string	Last Trading Date	
7715	string	Issue Date	
7718	string	Beta	Beta is against standard index.
7720	string	Ask Yield	Implied yield of the bond if it is purchased at the current offer. Ask yield is calculated using the Bid on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
7741	string	Prior Close	Yesterday’s closing price
7762	string	Volume Long	High precision volume for the day. For formatted volume refer to field 87.
7768	string	hasTradingPermissions	if user has trading permissions for specified contract. Returns 1(true) or 0(false).
7920	string	Daily PnL Raw	Your profit or loss of the day since prior close. Daily PnL is calculated with real-time market data (even when not subscribed to market data).
7921	string	Cost Basis Raw	Your current position in this security multiplied by the average price and and multiplier.
Unavailable Historical Data
Bars whose size is 30 seconds or less older than six months
Expired futures data older than two years counting from the future’s expiration date.
Expired options, FOPs, warrants and structured products.
End of Day (EOD) data for options, FOPs, warrants and structured products.
Data for expired future spreads
Data for securities which are no longer trading.
Native historical data for combos. Historical data is not stored in the IB database separately for combos.; combo historical data in TWS or the API is the sum of data from the legs.
Historical data for securities which move to a new exchange will often not be available prior to the time of the move.
Studies and indicators such as Weighted Moving Averages or Bollinger Bands are not available from the API.

## Historical Market Data
Get historical market Data for given conid, length of data is controlled by ‘period’ and ‘bar’.

Note:

There’s a limit of 5 concurrent requests. Excessive requests will return a ‘Too many requests’ status 429 response.
This endpoint provides a maximum of 1000 data points.
GET /iserver/marketdata/history
 

Request Object
Query Params
conid: String. Required
Contract identifier for the ticker symbol of interest.

exchange: String.
Returns the exchange you want to receive data from.

period: String.
Overall duration for which data should be returned.
Default to 1w
Available time period– {1-30}min, {1-8}h, {1-1000}d, {1-792}w, {1-182}m, {1-15}y

bar: String. Required
Individual bars of data to be returned.
Possible value– 1min, 2min, 3min, 5min, 10min, 15min, 30min, 1h, 2h, 3h, 4h, 8h, 1d, 1w, 1m.
Formatted as: min=minute, h=hour, d=day, w=week, m=month, y=year
See Step Size below to ensure your Bar Size is supported for your chosen Period value.

startTime: String
Starting date of the request duration.

outsideRth: bool.
Determine if you want data after regular trading hours.
 

Python
cURL
request_url = f"{baseUrl}/iserver/marketdata/history?conid=265598&exchange=SMART&period=1d&bar=1d&startTime=20230821-13:30:00&outsideRth=true"
requests.get(url=request_url)
 

Step Size
A step size is the permitted minimum and maximum bar size for any given period.

period	1min	1h	1d	1w	1m	3m	6m	1y	2y	3y	15y
bar	1min	1min – 8h	1min – 8h	10min – 1w	1h – 1m	2h – 1m	4h – 1m	8h – 1m	1d – 1m	1d – 1m	1w – 1m
default bar	1min	1min	1min	15min	30min	1d	1d	1d	1d	1w	1w
 

Response Object
serverId: String.
Internal request identifier.

symbol: String.
Returns the ticker symbol of the contract.

text: String.
Returns the long name of the ticker symbol.

priceFactor: String.
Returns the price increment obtained from the display rules.

startTime: String.
Returns the initial time of the historical data request.
Returned in UTC formatted as YYYYMMDD-HH:mm:ss

high: String.
Returns the High values during this time series with format %h/%v/%t.
%h is the high price (scaled by priceFactor),
%v is volume (volume factor will always be 100 (reported volume = actual volume/100))
%t is minutes from start time of the chart

low: String.
Returns the low value during this time series with format %l/%v/%t.
%l is the low price (scaled by priceFactor),
%v is volume (volume factor will always be 100 (reported volume = actual volume/100))
%t is minutes from start time of the chart

timePeriod: String.
Returns the duration for the historical data request

barLength: int.
Returns the number of seconds in a bar.

mdAvailability: String.
Returns the Market Data Availability.
See the Market Data Availability section for more details.

mktDataDelay: int.
Returns the amount of delay, in milliseconds, to process the historical data request.

outsideRth: bool.
Defines if the market data returned was inside regular trading hours or not.

volumeFactor: int.
Returns the factor the volume is multiplied by.

priceDisplayRule: int.
Presents the price display rule used.
For internal use only.

priceDisplayValue: String.
Presents the price display rule used.
For internal use only.

negativeCapable: bool.
Returns whether or not the data can return negative values.

messageVersion: int.
Internal use only.

data: Array of objects.
Returns all historical bars for the requested period.
[{
o: float.
Returns the Open value of the bar.

c: float.
Returns the Close value of the bar.

h: float.
Returns the High value of the bar.

l: float.
Returns the Low value of the bar.

v: float.
Returns the Volume of the bar.

t: int.
Returns the Operator Timezone Epoch Unix Timestamp of the bar.
}],

points: int.
Returns the total number of data points in the bar.

travelTime: int.
Returns the amount of time to return the details.


500 System Error
error: String.

{
  'error': 'description'
}
 

429 Too many requests
error: String.

{
  'error': 'description'
}
 

## HMDS Period & Bar Size
Valid Period Units:
Unit	Description
S	Seconds
d	Day
w	Week
m	Month
y	Year
Note: These units are case sensitive.

Valid Bar Units:
Duration	Bar units allowed	Bar size Interval (Min/Max)
60 S	secs | mins	1 secs -> 1mins
3600 S (1hour)	secs | mins | hrs	5 secs -> 1 hours
14400 S (4hours)	sec | mins | hrs	10 secs -> 4 hrs
28800 S  (8hours)	sec | mins | hrs	30 secs -> 8 hrs
1 d	mins | hrs   | d	1 mins-> 1 day
1 w	mins | hrs | d | w	3 mins -> 1 week
1 m	mins | d | w	30 mins -> 1 month
1 y	d | w | m	1 d -> 1 m
Note: These units are case sensitive.

NOTE: Keep in mind that a step size is defined as the ratio between the historical data request’s duration period and its granularity (i.e. bar size). Historical Data requests need to be assembled in such a way that only a few thousand bars are returned at a time.

## Pacing Limits
https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#pacing-limitations