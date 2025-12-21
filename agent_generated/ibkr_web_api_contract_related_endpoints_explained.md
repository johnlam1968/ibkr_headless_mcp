Contract
Search the security definition by Contract ID
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

{
  "secdef": [
    {
      "conid": 265598,
      "currency": "USD",
      "time": 43,
      "chineseName": "苹果公司",
      "allExchanges": "AMEX,NYSE,CBOE,PHLX,CHX,ARCA,ISLAND,ISE,IDEAL,NASDAQQ,NASDAQ,DRCTEDGE,BEX,BATS,NITEECN,EDGEA,CSFBALGO,JEFFALGO,NYSENASD,PSX,BYX,ITG,PDQ,IBKRATS,CITADEL,NYSEDARK,MIAX,IBDARK,CITADELDP,NASDDARK,IEX,WEDBUSH,SUMMER,WINSLOW,FINRA,LIQITG,UBSDARK,BTIG,VIRTU,JEFF,OPCO,COWEN,DBK,JPMC,EDGX,JANE,NEEDHAM,FRACSHARE,RBCALGO,VIRTUDP,BAYCREST,FOXRIVER,MND,NITEEXST,PEARL,GSDARK,NITERTL,NYSENAT,IEXMID,HRT,FLOWTRADE,HRTDP,JANELP,PEAK6,IMCDP,CTDLZERO,HRTMID,JANEZERO,HRTEXST,IMCLP,LTSE,SOCGENDP,MEMX,INTELCROS,VIRTUBYIN,JUMPTRADE,NITEZERO,TPLUS1,XTXEXST,XTXDP,XTXMID,COWENLP,BARCDP,JUMPLP,OLDMCLP,RBCCMALP,WALLBETH,IBEOS,JONES,GSLP,BLUEOCEAN,USIBSILP,OVERNIGHT,JANEMID,IBATSEOS,HRTZERO,VIRTUALGO",
      "listingExchange": "NASDAQ",
      "countryCode": "US",
      "name": "APPLE INC",
      "assetClass": "STK",
      "expiry": null,
      "lastTradingDay": null,
      "group": "Computers",
      "putOrCall": null,
      "sector": "Technology",
      "sectorGroup": "Computers",
      "strike": "0",
      "ticker": "AAPL",
      "undConid": 0,
      "multiplier": 0.0,
      "type": "COMMON",
      "hasOptions": true,
      "fullName": "AAPL",
      "isUS": true,
      "incrementRules": [
        {
          "lowerEdge": 0.0,
          "increment": 0.01
        }
      ],
      "displayRule": {
        "magnification": 0,
        "displayRuleStep": [
          {
            "decimalDigits": 2,
            "lowerEdge": 0.0,
            "wholeDigits": 4
          }
        ]
      },
      "isEventContract": false,
      "pageSize": 100
    }
  ]
}
 

All Conids by Exchange
Send out a request to retrieve all contracts made available on a requested exchange. This returns all contracts that are tradable on the exchange, even those that are not using the exchange as their primary listing.

Note: This is only available for Stock contracts.

GET /trsrv/all-conids

 

Request Object
Query Params
exchange: String. Required
Specify a single exchange to receive conids for.

Python
cURL
request_url = f"{baseUrl}/trsrv/all-conids?exchange=AMEX"
requests.get(url=request_url)
 

Response Object
ticker: String.
Returns the ticker symbol of the contract

conid: int.
Returns the contract identifier of the returned contract.

exchange: String.
Returns the exchanger of the returned contract.

[
  {
    "ticker": "BMO",
    "conid": 5094,
    "exchange": "NYSE"
  },
  {...},
  {
    "ticker": "ZKH",
    "conid": 671347171,
    "exchange": "NYSE"
  }
]
 

Contract information by Contract ID
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

{
  "cfi_code": "",
  "symbol": "AAPL",
  "cusip": null,
  "expiry_full": null,
  "con_id": 265598,
  "maturity_date": null,
  "industry": "Computers",
  "instrument_type": "STK",
  "trading_class": "NMS",
  "valid_exchanges": "SMART,AMEX,NYSE,CBOE,PHLX,ISE,CHX,ARCA,ISLAND,DRCTEDGE,BEX,BATS,EDGEA,JEFFALGO,BYX,IEX,EDGX,FOXRIVER,PEARL,NYSENAT,LTSE,MEMX,TPLUS1,IBEOS,OVERNIGHT,PSX",
  "allow_sell_long": false,
  "is_zero_commission_security": false,
  "local_symbol": "AAPL",
  "contract_clarification_type": null,
  "classifier": null,
  "currency": "USD",
  "text": null,
  "underlying_con_id": 0,
  "r_t_h": true,
  "multiplier": null,
  "underlying_issuer": null,
  "contract_month": null,
  "company_name": "APPLE INC",
  "smart_available": true,
  "exchange": "SMART",
  "category": "Computers"
}
 

Currency Pairs
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
 

Currency Exchange Rate
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
 

Find all Info and Rules for a given contract
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

{
  "cfi_code": "",
  "symbol": "AAPL",
  "cusip": null,
  "expiry_full": null,
  "con_id": 265598,
  "maturity_date": null,
  "industry": "Computers",
  "instrument_type": "STK",
  "trading_class": "NMS",
  "valid_exchanges": "SMART,AMEX,NYSE,CBOE,PHLX,ISE,CHX,ARCA,ISLAND,DRCTEDGE,BEX,BATS,EDGEA,JEFFALGO,BYX,IEX,EDGX,FOXRIVER,PEARL,NYSENAT,LTSE,MEMX,TPLUS1,IBEOS,OVERNIGHT,PSX",
  "allow_sell_long": false,
  "is_zero_commission_security": false,
  "local_symbol": "AAPL",
  "contract_clarification_type": null,
  "classifier": null,
  "currency": "USD",
  "text": null,
  "underlying_con_id": 0,
  "r_t_h": true,
  "multiplier": null,
  "underlying_issuer": null,
  "contract_month": null,
  "company_name": "APPLE INC",
  "smart_available": true,
  "exchange": "SMART",
  "category": "Computers",
  "rules": {
    "algoEligible": true,
    "overnightEligible": true,
    "costReport": false,
    "canTradeAcctIds": [
      "U1234567"
    ],
    "error": null,
    "orderTypes": [
      "limit",
      "midprice",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit",
      "relative",
      "marketonclose",
      "limitonclose"
    ],
    "ibAlgoTypes": [
      "limit",
      "stop_limit",
      "lit",
      "trailing_stop_limit",
      "relative",
      "marketonclose",
      "limitonclose"
    ],
    "fraqTypes": [
      "limit",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit"
    ],
    "forceOrderPreview": false,
    "cqtTypes": [
      "limit",
      "market",
      "stop",
      "stop_limit",
      "mit",
      "lit",
      "trailing_stop",
      "trailing_stop_limit"
    ],
    "orderDefaults": {
      "LMT": {
        "LP": "197.93"
      }
    },
    "orderTypesOutside": [
      "limit",
      "stop_limit",
      "lit",
      "trailing_stop_limit",
      "relative"
    ],
    "defaultSize": 100,
    "cashSize": 0.0,
    "sizeIncrement": 100,
    "tifTypes": [
      "IOC/MARKET,LIMIT,RELATIVE,MARKETONCLOSE,MIDPRICE,LIMITONCLOSE,MKT_PROTECT,STPPRT,a",
      "GTC/o,a",
      "OPG/LIMIT,MARKET,a",
      "GTD/o,a",
      "DAY/o,a"
    ],
    "tifDefaults": {
      "TIF": "DAY",
      "SIZE": "100.00"
    },
    "limitPrice": 197.93,
    "stopprice": 197.93,
    "orderOrigination": null,
    "preview": true,
    "displaySize": null,
    "fraqInt": 4,
    "cashCcy": "USD",
    "cashQtyIncr": 500,
    "priceMagnifier": null,
    "negativeCapable": false,
    "incrementType": 1,
    "incrementRules": [
      {
        "lowerEdge": 0.0,
        "increment": 0.01
      }
    ],
    "hasSecondary": true,
    "increment": 0.01,
    "incrementDigits": 2
  }
}
 

Search Algo Params by Contract ID
Returns supported IB Algos for contract.

A pre-flight request must be submitted before retrieving information

GET /iserver/contract/{{ conid }}/algos

 

Request Object
Path Parameters
conid: String. Required
Contract identifier for the requested contract of interest.

Query Parameters
algos: String. Optional
List of algo ids delimited by “;” to filter by.
Max of 8 algos ids can be specified.
Case sensitive to algo id.

addDescription: String. Optional
Whether or not to add algo descriptions to response. Set to 1 for yes, 0 for no.

addParams: String. Optional
Whether or not to show algo parameters. Set to 1 for yes, 0 for no.

Python
cURL
request_url = f"{baseUrl}/iserver/contract/265598/algos?algos=Adaptive;Vwap&addDescription=1&addParams=1"
requests.get(url=request_url)
 

Response Object
algos: Array of objects.
Contains all relevant algos for the contract.

[{

name: String.
Common name of the algo.

id: String.
Algo identifier used for requests

parameters: Array of objects.
All parameters relevant to the given algo.
Only returned if addParams=1

[{

guiRank: int.
Positional ranking for the algo. Used for Client Portal.

defaultValue: int.
Default parameter value.

name: String.
Parameter name.

id: String.
Parameter identifier for the algo.

legalStrings: Array
Allowed values for the parameter.

required: String.
States whether the parameter is required for the given algo order to place.
Returns a string representation of a boolean.

valueClassName: String.
Returns the variable type of the parameter.
}]
}]

{
  "algos": [
    {
      "name": "Adaptive",
      "id": "Adaptive",
      "parameters": [
        {
          "guiRank": 1,
          "defaultValue": "Normal",
          "name": "Adaptive order priority/urgency",
          "id": "adaptivePriority",
          "legalStrings": [
            "Urgent",
            "Normal",
            "Patient"
          ],
          "required": "true",
          "valueClassName": "String"
        }
      ]
    },
    {
      "name": "VWAP",
      "id": "Vwap",
      "parameters": [
        {
          "guiRank": 5,
          "defaultValue": false,
          "name": "Attempt to never take liquidity",
          "id": "noTakeLiq",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 11,
          "defaultValue": false,
          "name": "Opt-out closing auction",
          "id": "optoutClosingAuction",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 4,
          "defaultValue": false,
          "name": "Allow trading past end time",
          "id": "allowPastEndTime",
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 8,
          "defaultValue": false,
          "name": "Speed up when market approaches limit price",
          "description": "Compensate for decreased fill rate due to presence of limit price.",
          "id": "speedUp",
          "enabledConditions": [
            "MKT:speedUp:=:no"
          ],
          "valueClassName": "Boolean"
        },
        {
          "guiRank": 12,
          "name": "Trade when price is more aggressive than:",
          "description": "Evaluates with bid for buy order and ask for sell order",
          "id": "conditionalPrice",
          "valueClassName": "Double"
        },
        {
          "guiRank": 2,
          "name": "Start Time",
          "description": "Defaults to start of market trading",
          "id": "startTime",
          "valueClassName": "Time"
        },
        {
          "guiRank": 1,
          "minValue": 0.01,
          "maxValue": 50,
          "name": "Max Percentage",
          "description": "From 0.01 to 50.0",
          "id": "maxPctVol",
          "valueClassName": "Double"
        },
        {
          "guiRank": 3,
          "name": "End Time",
          "description": "Defaults to end of market trading",
          "id": "endTime",
          "valueClassName": "Time"
        }
      ]
    }
  ]
}
 

Search Bond Filter Information
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
 

Search Contract by Symbol
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

[
  {
    "conid": "43645865",
    "companyHeader": "IBKR INTERACTIVE BROKERS GRO-CL A (NASDAQ) ",
    "companyName": "INTERACTIVE BROKERS GRO-CL A (NASDAQ)",
    "symbol": "IBKR",
    "description": null,
    "restricted": null,
    "sections": [],
    "secType": "STK"
  }
]
 

Search Contract Rules
Returns trading related rules for a specific contract and side.

POST /iserver/contract/rules

 

Request Object
Body Parameters
conid: Number. Required
Contract identifier for the interested contract.

exchange: String.
Designate the exchange you wish to receive information for in relation to the contract.

isBuy: bool.
Side of the market rules apply too. Set to true for Buy Orders, set to false for Sell Orders
Defaults to true or Buy side rules.

modifyOrder: bool.
Used to find trading rules related to an existing order.

orderId: Number. Required for modifyOrder:true
Specify the order identifier used for tracking a given order.

Python
cURL
request_url = f"{baseUrl}/iserver/contract/rules"
json_content = {
  "conid": 265598,
  "exchange": "SMART",
  "isBuy": true,
  "modifyOrder": true,
  "orderId": 1234567890
}
requests.post(url=request_url, json=json_content)
 

Response Object
algoEligible: bool.
Indicates if the contract can trade algos or not.

overnightEligible: bool.
Indicates if outsideRTH trading is permitted for the instrument

costReport: bool.
Indicates whether or not a cost report has been requested (Client Portal only).

canTradeAcctIds: Array of Strings.
Indicates permitted accountIDs that may trade the contract.

error: String.
If rules information can not be received for any reason, it will be expressed here.

orderTypes: Array of Strings
Indicates permitted order types for use with standard quantity trading.

ibAlgoTypes: Array of Strings.
Indicates permitted algo types for use with the given contract.

fraqTypes: Array of Strings.
Indicates permitted order types for use with fractional trading.

forceOrderPreview: bool.
Indicates if the order preview is forced upon the user before submission.

cqtTypes: Array of Strings.
Indicates accepted order types for use with cash quantity.

orderDefaults: Object of objects
Indicates default order type for the given security type.

orderTypesOutside: Array of Strings.
Indicates permitted order types for use outside of regular trading hours.

defaultSize: int.
Default total quantity value for orders.

cashSize: float.
Default cash value quantity.

sizeIncrement: int.
Indicates quantity increase for the contract.

tifTypes: Array of Strings.
Indicates allowed tif types supported for the contract.

tifDefaults: Object.
Object containing details about your TIF value defaults.
These defaults can be viewed and modified in TWS’s within the Global Configuration.

limitPrice: float.
Default limit price for the given contract.

stopprice: float.
Default stop price for the given contract.

orderOrigination: String.
Order origin designation for US securities options and Options Clearing Corporation

preview: bool.
Indicates if the order preview is required (for client portal only)

displaySize: int.

fraqInt: int.
Indicates decimal places for fractional order size

cashCcy: String.
Indicates base currency for the instrument.

cashQtyIncr: int.
Indicates cash quantity increment rules.

priceMagnifier: int.
Signifies if a contract is not trading in the standard cash denomination.
If a symbol is priced in Cents, Pence, or the currency’s fractional equivalent, the relative value will be displayed. For standard instruments, Null will be passed.

negativeCapable: bool.
Indicates if the value of the contract can be negative (true) or if it is always positive (false).

incrementType: int.
Indicates the type of increment style.

incrementRules: Array of objects.
Indicates increment rule values including lowerEdge and increment value.

hasSecondary: bool.

modTypes: Array of Strings.
Lists the available order types supported when modifying the order.

increment: float.
Minimum increment values for prices

incrementDigits: int.
Number of decimal places to indicate the increment value.

{
  "algoEligible": true,
  "overnightEligible": true,
  "costReport": false,
  "canTradeAcctIds": [
    "U1234567"
  ],
  "error": null,
  "orderTypes": [
    "limit",
    "midprice",
    "market",
    "stop",
    "stop_limit",
    "mit",
    "lit",
    "trailing_stop",
    "trailing_stop_limit",
    "relative",
    "marketonclose",
    "limitonclose"
  ],
  "ibAlgoTypes": [
    "limit",
    "stop_limit",
    "lit",
    "trailing_stop_limit",
    "relative",
    "marketonclose",
    "limitonclose"
  ],
  "fraqTypes": [],
  "forceOrderPreview": false,
  "cqtTypes": [
    "limit",
    "market",
    "stop",
    "stop_limit",
    "mit",
    "lit",
    "trailing_stop",
    "trailing_stop_limit"
  ],
  "orderDefaults": {
    "LMT": {
      "LP": "549000.00"
    }
  },
  "orderTypesOutside": [
    "limit",
    "stop_limit",
    "lit",
    "trailing_stop_limit",
    "relative"
  ],
  "defaultSize": 100,
  "cashSize": 0.0,
  "sizeIncrement": 1,
  "tifTypes": [
    "IOC/MARKET,LIMIT,RELATIVE,MARKETONCLOSE,MIDPRICE,LIMITONCLOSE,MKT_PROTECT,STPPRT,a",
    "GTC/o,a",
    "OPG/LIMIT,MARKET,a",
    "GTD/o,a",
    "DAY/o,a"
  ],
  "tifDefaults": {
    "TIF": "DAY",
    "SIZE": "100.00"
  },
  "limitPrice": 549000.0,
  "stopprice": 549000.0,
  "orderOrigination": null,
  "preview": true,
  "displaySize": null,
  "fraqInt": 0,
  "cashCcy": "USD",
  "cashQtyIncr": 500,
  "priceMagnifier": null,
  "negativeCapable": false,
  "incrementType": 1,
  "incrementRules": [
    {
      "lowerEdge": 0.0,
      "increment": 0.01
    }
  ],
  "hasSecondary": true,
  "increment": 0.01,
  "incrementDigits": 2
}
 

Search SecDef information by conid
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

[
  {
    "conid": 667629330,
    "symbol": "AAPL",
    "secType": "OPT",
    "exchange": "SMART",
    "listingExchange": null,
    "right": "P",
    "strike": 195.0,
    "currency": "USD",
    "cusip": null,
    "coupon": "No Coupon",
    "desc1": "AAPL",
    "desc2": "JAN 05 '24 195 Put",
    "maturityDate": "20240105",
    "multiplier": "100",
    "tradingClass": "AAPL",
    "validExchanges": "SMART,AMEX,CBOE,PHLX,PSE,ISE,BOX,BATS,NASDAQOM,CBOE2,NASDAQBX,MIAX,GEMINI,EDGX,MERCURY,PEARL,EMERALD,MEMX,IBUSOPT"
  }
]
 

Search Strikes by Underlying Contract ID
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

{
  "call":[
    185.0,
    190.0,
    195.0,
    200.0
  ],
  "put":[
    185.0,
    190.0,
    195.0,
    200.0
  ]
}
 

Security Future by Symbol
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

{
  "ES": [
    {
      "symbol": "ES",
      "conid": 495512552,
      "underlyingConid": 11004968,
      "expirationDate": 20231215,
      "ltd": 20231214,
      "shortFuturesCutOff": 20231214,
      "longFuturesCutOff": 20231214
    },
    {...}
  ],
  "MES": [
    {
      "symbol": "MES",
      "conid": 586139726,
      "underlyingConid": 362673777,
      "expirationDate": 20231215,
      "ltd": 20231215,
      "shortFuturesCutOff": 20231215,
      "longFuturesCutOff": 20231215
    },
    {...}
  ]
}
 

Security Stocks by Symbol
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

{
  "AAPL": [
    {
      "name": "APPLE INC",
      "chineseName": "苹果公司",
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 265598,
          "exchange": "NASDAQ",
          "isUS": true
        },
        {
          "conid": 38708077,
          "exchange": "MEXI",
          "isUS": false
        },
        {
          "conid": 273982664,
          "exchange": "EBS",
          "isUS": false
        }
      ]
    },
    {
      "name": "LS 1X AAPL",
      "chineseName": null,
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 493546048,
          "exchange": "LSEETF",
          "isUS": false
        }
      ]
    },
    {
      "name": "APPLE INC-CDR",
      "chineseName": "苹果公司",
      "assetClass": "STK",
      "contracts": [
        {
          "conid": 532640894,
          "exchange": "AEQLIT",
          "isUS": false
        }
      ]
    }
  ]
}
 

Trading Schedule by Symbol
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

[
  {
    "id": "p102082",
    "tradeVenueId": "v13133",
    "timezone": "America/New_York",
    "schedules": [      
      {
        "clearingCycleEndTime": "2000",
        "tradingScheduleDate": "20000103",
        "sessions": [
          {
            "openingTime": "0930",
            "closingTime": "1600",
            "prop": "LIQUID"
          }
        ],
        "tradingtimes": [
          {
            "openingTime": "0400",
            "closingTime": "2000",
            "cancelDayOrders": "Y"
          }
        ]
      },
      {...}
    ]
  }
]
 