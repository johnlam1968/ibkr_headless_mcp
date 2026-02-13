source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/
## Receive Brokerage Accounts 
Returns a list of accounts the user has trading access to, their respective aliases and the currently selected account. Note this endpoint must be called before modifying an order or querying open orders.

GET /iserver/accounts

Request Object:
No parameters necessary.

Python
cURL
request_url = f"{baseUrl}/iserver/accounts" 
requests.get(url=request_url)
 

Response Object:
accounts: Array of Strings.
Returns an array of all accessible accountIds.

acctProps: Json Object.
Returns an json object for each accessible account’s properties.

hasChildAccounts: bool.
Returns whether or not child accounts exist for the account.

supportsCashQty: bool
Returns whether or not the account can use Cash Quantity for trading.

supportsFractions: bool.
Returns whether or not the account can submit fractional share orders.

allowCustomerTime: bool.
Returns whether or not the account must submit “manualOrderTime” with orders or not.
If true, manualOrderTime must be included.
If false, manualOrderTime cannot be included.

aliases: JSON Object.
Returns any available aliases for the account.

allowFeatures: JSON object
JSON of allowed features for the account.

showGFIS: bool.
Returns if the account can access market data.

showEUCostReport: bool.
Returns if the account can view the EU Cost Report

allowFXConv: bool.
Returns if the account can convert currencies.

allowFinancialLens: bool.
Returns if the account can access the financial lens.

allowMTA: bool.
Returns if the account can use mobile trading alerts.

allowTypeAhead: bool.
Returns if the account can use Type-Ahead support for Client Portal.

allowEventTrading: bool.
Returns if the account can use Event Trader.

snapshotRefreshTimeout: int.
Returns the snapshot refresh timeout window for new data.

liteUser: bool.
Returns if the account is an IBKR Lite user.

showWebNews: bool.
Returns if the account can use News feeds via the web.
research: bool.

debugPnl: bool.
Returns if the account can use the debugPnl endpoint.

showTaxOpt: bool.
Returns if the account can use the Tax Optimizer tool

showImpactDashboard: bool.
Returns if the account can view the Impact Dashboard.

allowDynAccount: bool.
Returns if the account can use dynamic account changes.

allowCrypto: bool.
Returns if the account can trade crypto currencies.

allowedAssetTypes: bool.
Returns a list of asset types the account can trade.

chartPeriods: Json Object.
Returns available trading times for all available security types.

groups: Array.
Returns an array of affiliated groups.

profiles: Array.
Returns an array of affiliated profiles.

selectedAccount: String.
Returns currently selected account. See Switch Account for more details.

serverInfo: JSON Object.
Returns information about the IBKR session. Unrelated to Client Portal Gateway.

sessionId: String.
Returns current session ID.

isFT: bool.
Returns fractional trading access.

isPaper: bool.
Returns account type status.

{
  "accounts": [
    "U1234567"
  ],
  "acctProps": {
    "U1234567": {
      "hasChildAccounts": false,
      "supportsCashQty": true,
      "noFXConv": false,
      "isProp": false,
      "supportsFractions": true,
      "allowCustomerTime": false
    }
  },
  "aliases": {
    "U1234567": "U1234567"
  },
  "allowFeatures": {
    "showGFIS": true,
    "showEUCostReport": false,
    "allowEventContract": true,
    "allowFXConv": true,
    "allowFinancialLens": false,
    "allowMTA": true,
    "allowTypeAhead": true,
    "allowEventTrading": true,
    "snapshotRefreshTimeout": 30,
    "liteUser": false,
    "showWebNews": true,
    "research": true,
    "debugPnl": true,
    "showTaxOpt": true,
    "showImpactDashboard": true,
    "allowDynAccount": false,
    "allowCrypto": false,
    "allowedAssetTypes": "STK,CRYPTO"
  },
  "chartPeriods": {
    "STK": [
      "*"
    ],
    "CRYPTO": [
      "*"
    ]
  },
  "groups": [],
  "profiles": [],
  "selectedAccount": "U1234567",
  "serverInfo": {
    "serverName": "JifN17091",
    "serverVersion": "Build 10.25.0p, Dec 5, 2023 5:48:12 PM"
  },
  "sessionId": "1234a5b.12345678",
  "isFT": false,
  "isPaper": false
}

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


Trading schedule
Provides contract trading schedules

GET /forecast/contract/schedules
 

Request Object
Query Params
conid: Integer
Contract identifier

Python
cURL
import requests
url = "{{base-url}}/forecast/contract/schedules?conid=767285167"
payload = {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
print(response.text)
 

Response Object
timezone: String
Exchange timezone

trading schedule: List
List of strikes

day_of_week: String

trading_times: List
List of trading time intervalse

open: String
Start of trading interval

close: String
End of trading interval

{
    "timezone": "US/Central",
    "trading_schedules": [
        {
            "day_of_week": "Saturday",
            "trading_times": [
                {
                    "open": "12:00 AM",
                    "close": "4:15 PM"
                },
                {
                    "open": "4:16 PM",
                    "close": "11:59 PM"
                }
            ]
        },
        {
            "day_of_week": "Sunday",
            "trading_times": [
                {
                    "open": "12:00 AM",
                    "close": "4:15 PM"
                },
                {
                    "open": "4:16 PM",
                    "close": "11:59 PM"
                }
            ]
        },
}
## Trading Schedule (NEW)
Returns the trading schedule for the 6 total days surrounding the current trading day. Non-Trading days, such as holidays, will not be returned.

GET /contract/trading-schedule

 

Request Object
Query Params
conid: String. Required
Provide the contract identifier to retrieve the trading schedule for.

exchange: String.
Accepts the exchange to retrieve data from. Primary exchange is assumed by default.

Python
cURL
request_url = f"{baseUrl}/contract/trading-schedule?conid=265598&exchange=ISLAND"
requests.get(url=requests_url)
 

Response Object
exchange_time_zone: String.
Returns the time zone the exchange trades in.

schedules: Object.
A schedule object containing the trading hours.
{
{date}: Array.
Array of hours objects detailing extended and standard trading.
[
extended_hours: Array.
Reference the total extended trading hours for the session.
{
cancel_daily_orders: Boolean.
Determines if DAY orders are canceled after ‘closing’ time.

closing: Integer.
Epoch timestamp of the exchange’s close.

opening: Integer.
Epoch timestamp of the exchange’s open.
}

liquid_hours: Array.
Reference the available trading hours for the regular session
{
closing: Integer.
Epoch timestamp of the exchange’s close.

opening: Integer.
Epoch timestamp of the exchange’s open.
}]}

{
  'exchange_time_zone': 'US/Central', 
  'schedules': {
    '20251218': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766095200,
        'opening': 1766012400}],
    'liquid_hours': [{
        'closing': 1766095200,
        'opening': 1766068200
    }]},
    '20251219': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766181600,
        'opening': 1766098800}],
    'liquid_hours': [{
        'closing': 1766181600,
        'opening': 1766154600
    }]},
    '20251222': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766440800,
        'opening': 1766358000}],
    'liquid_hours': [{
        'closing': 1766440800,
        'opening': 1766413800
    }]},
    '20251223': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766527200,
        'opening': 1766444400
    }],
    'liquid_hours': [{
        'closing': 1766527200,
        'opening': 1766500200
    }]},
    '20251224': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766600100,
        'opening': 1766530800}],
    'liquid_hours': [{
        'closing': 1766600100,
        'opening': 1766586600
    }]},
    '20251226': {
      'extended_hours': [{
        'cancel_daily_orders': True,
        'closing': 1766786400,
        'opening': 1766703600
    }]}  
  }
}

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


## Workflow to get market snapshot data:

  (1) The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot:

  (2) Obtain conid from /iserver/secdef/search:

  (3) Then use conid in the /iserver/marketdata/snapshot endpoint.
      100 conids can be requested at once
      10 requests per second

  (3.1) First call to onboard:
      call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})

  (3.2) Must call twice to get actual data, first call only returns empty data. Make a second call to get actual data:
      call_endpoint(path='iserver/marketdata/snapshot', params={"conids":"265598", "fields":"31,84,86"})

      Maximum 50 fields per request.


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
All market data fields are documented in separate files:

- **[Market Data Fields (Organized)](market_data_fields.md)** - Fields organized by financial category (Price Data, Volume, Options Greeks, Fundamentals, etc.)
- **[Market Data Fields (Original)](market_data_fields_original.md)** - Original field reference sorted by Field ID

Use the `market_data_fields()` MCP tool to retrieve the organized documentation programmatically.

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