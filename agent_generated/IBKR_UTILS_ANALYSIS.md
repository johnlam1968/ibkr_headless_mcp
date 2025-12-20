# IBKR Utilities Analysis: ibkr_utils.py

**Analysis Date:** December 19, 2025  
**File:** `/home/john/CodingProjects/llm/.venv/lib/python3.13/site-packages/ibind/client/ibkr_utils.py`

## Overview

The `ibkr_utils.py` module provides essential utility classes, functions, and data structures that support the IBKR client mixins. This file contains core components for stock query processing, order management, question handling, and session maintenance.

## Key Components

### 1. StockQuery Dataclass

**Purpose:** Encapsulates query parameters for filtering stock data.

**Structure:**
```python
@dataclass
class StockQuery:
    symbol: str
    name_match: Optional[str] = None
    instrument_conditions: Optional[dict] = None
    contract_conditions: Optional[dict] = None
```

**Usage:** Used throughout the ContractMixin and MarketdataMixin for precise stock filtering.

**Type Alias:**
```python
StockQueries = OneOrMany[Union[StockQuery, str]]
```

---

### 2. Stock Filtering Functions

#### `process_instruments()`
**Purpose:** Filters a list of instruments based on specified name matching and conditions.

**Parameters:**
- `instruments`: List of instrument dictionaries
- `name_match`: String pattern for partial name matching
- `instrument_conditions`: Exact conditions for instrument attributes
- `contract_conditions`: Exact conditions for contract attributes

**Returns:** Filtered list of instruments

**Filtering Logic:**
1. Name matching (case-insensitive partial match)
2. Instrument property exact matching
3. Contract property exact matching

#### `filter_stocks()`
**Purpose:** High-level function to filter stocks based on StockQuery objects.

**Parameters:**
- `queries`: StockQueries (list of StockQuery objects or strings)
- `result`: Result object containing stock data
- `default_filtering`: Whether to apply default US contract filtering (default: True)

**Returns:** Filtered stocks wrapped in Result object

#### `process_query()`
**Purpose:** Processes a query (string or StockQuery) into filtering parameters.

**Default Behavior:** Applies `{'isUS': True}` contract filtering by default for US stocks.

---

### 3. Question Handling System

#### `QuestionType` Enum
**Purpose:** Enumeration of common warning messages encountered when submitting orders.

**Key Warning Types:**
- `PRICE_PERCENTAGE_CONSTRAINT`: Price exceeds 3% constraint
- `MISSING_MARKET_DATA`: Order submitted without market data
- `TICK_SIZE_LIMIT`: Exceeds tick size limit
- `ORDER_SIZE_LIMIT`: Exceeds size limit
- `TRIGGER_AND_FILL`: Order will likely trigger and fill immediately
- `ORDER_VALUE_LIMIT`: Exceeds total value limit
- `SIZE_MODIFICATION_LIMIT`: Size modification exceeds limit
- `MANDATORY_CAP_PRICE`: Price cap warning for fair market
- `CASH_QUANTITY`: Cash quantity responsibility warning
- `STOP_ORDER_RISKS`: Stop order risks warning
- `MULTIPLE_ACCOUNTS`: Order distributed over multiple accounts
- `DISRUPTIVE_ORDERS`: Potential order rejection warning

#### Message ID Mapping
The module maintains `_MESSAGE_ID_TO_QUESTION_TYPE` dictionary mapping IBKR message IDs to QuestionType enums and descriptions.

**Example Mappings:**
- `"o163"`: Price percentage constraint
- `"o354"`: Missing market data warning
- `"o382"`: Tick size limit
- `"o383"`: Order size limit
- `"p6"`: Multiple accounts distribution

#### `handle_questions()`
**Purpose:** Handles interactive questions that arise during order submission.

**Parameters:**
- `original_result`: Result object containing questions
- `answers`: Answers dictionary mapping QuestionType to boolean responses
- `reply_callback`: Callback function to reply to questions

**Process:**
1. Extracts questions from result data
2. Matches questions against known QuestionTypes
3. Uses provided answers to respond
4. Continues until all questions are answered or error occurs

**Maximum Attempts:** 20 questions before raising RuntimeError

---

### 4. Order Management

#### `OrderRequest` Dataclass
**Purpose:** Comprehensive order request structure with all IBKR order parameters.

**Required Fields:**
- `conid`: Contract identifier
- `side`: Order side ('BUY' or 'SELL')
- `quantity`: Order quantity
- `order_type`: Order type (LMT, MKT, STP, etc.)
- `acct_id`: Account ID

**Optional Fields (50+ parameters):**
- `price`: Limit price
- `conidex`: Contract ID + exchange
- `sec_type`: Security type
- `tif`: Time-in-force (default: 'GTC')
- `outside_rth`: Outside regular trading hours
- `trailing_amt`: Trailing amount
- `cash_qty`: Cash quantity
- `strategy`: IB Algo algorithm
- `strategy_parameters`: Algorithm parameters
- `custom_fields`: Additional unmapped fields

**Method:** `to_dict()` - Converts to dictionary excluding None values

#### `parse_order_request()`
**Purpose:** Converts OrderRequest to IBKR API format.

**Mapping:** Uses `_ORDER_REQUEST_MAPPING` to translate field names to API parameter names.

**Validation:** Ensures `conid` and `conidex` are not both provided.

#### `make_order_request()` (Deprecated)
**Purpose:** Legacy function for creating order requests (deprecated in favor of OrderRequest dataclass).

---

### 5. Session Management

#### `Tickler` Class
**Purpose:** Maintains OAuth connection alive by periodically calling the `tickle` method.

**Key Features:**
- Runs in separate daemon thread
- Prevents session expiration
- Configurable interval (default: 60 seconds)
- Graceful start/stop functionality

**Methods:**
- `start()`: Starts tickler thread
- `stop(timeout=None)`: Stops tickler thread with optional timeout

**Error Handling:** Logs timeout errors and other exceptions without crashing.

---

### 6. Data Processing Utilities

#### `cleanup_market_history_responses()`
**Purpose:** Processes and cleans up market history responses into structured records.

**Parameters:**
- `market_history_response`: Dictionary of symbols to Result/Exception objects
- `raise_on_error`: Whether to raise exceptions (default: False)

**Returns:** Dictionary of symbols to structured data or Exception objects

**Data Structure:**
```python
{
    "open": record['o'],
    "high": record['h'],
    "low": record['l'],
    "close": record['c'],
    "volume": record['v'],
    "date": datetime object
}
```

**Features:**
- Validates market data availability ('S' or 'R' in `mdAvailability`)
- Handles "No data" errors gracefully
- Converts timestamps to datetime objects

#### `date_from_ibkr()`
**Purpose:** Converts IBKR date strings (YYYYMMDDHHMMSS format) to datetime objects.

#### `extract_conid()`
**Purpose:** Extracts conid from various data structures (topic field or payload).

---

### 7. Helper Functions

#### `_filter()`
**Purpose:** Internal function for exact matching of dictionary conditions.

#### `find_answer()`
**Purpose:** Finds predefined answer for a question based on QuestionType matching.

#### `question_type_to_message_id()`
**Purpose:** Converts QuestionType to corresponding IBKR message ID.

#### `query_to_symbols()`
**Purpose:** Converts StockQueries to comma-separated symbol string.

---

## Type Definitions

### `Answers` Type
```python
Answers = Dict[Union[QuestionType, str], bool]
```
Mapping of order warnings to user responses (True = accept, False = reject).

### `OneOrMany` Type
From `ibind.support.py_utils`: Generic type for single or list values.

---

## Integration with Mixins

### ContractMixin Integration
- Uses `StockQuery` for stock filtering
- Uses `filter_stocks()` for query processing
- Uses `query_to_symbols()` for API calls

### MarketdataMixin Integration
- Uses `cleanup_market_history_responses()` for data processing
- Uses `StockQuery` for symbol-based queries

### Order Management Integration
- `OrderRequest` used by order submission methods
- `handle_questions()` used for interactive order validation
- `QuestionType` used for warning handling

---

## Key Design Patterns

### 1. Filter Chain Pattern
`process_instruments()` implements a filter chain for progressive refinement of stock results.

### 2. Question-Answer Pattern
`handle_questions()` implements iterative question handling with answer lookup.

### 3. Builder Pattern
`OrderRequest` dataclass provides a builder pattern for complex order creation.

### 4. Thread Management Pattern
`Tickler` implements proper thread lifecycle management for background tasks.

### 5. Error Resilience Pattern
`cleanup_market_history_responses()` implements graceful error handling with configurable raise behavior.

---

## Usage Examples

### Stock Filtering
```python
# Create stock query
query = StockQuery(
    symbol="AAPL",
    name_match="Apple",
    contract_conditions={"isUS": True, "exchange": "NASDAQ"}
)

# Process query
symbol, name_match, inst_cond, contract_cond = process_query(query)

# Filter instruments
filtered = process_instruments(
    instruments=data["AAPL"],
    name_match=name_match,
    contract_conditions=contract_cond
)
```

### Order Creation
```python
# Modern approach (recommended)
order = OrderRequest(
    conid=265598,
    side="BUY",
    quantity=100,
    order_type="LMT",
    acct_id="DU1234567",
    price=150.50,
    tif="GTC",
    outside_rth=False
)

# Parse for API
api_order = parse_order_request(order)
```

### Question Handling
```python
# Define answers
answers = {
    QuestionType.PRICE_PERCENTAGE_CONSTRAINT: True,
    QuestionType.MISSING_MARKET_DATA: False
}

# Handle questions
result = handle_questions(order_result, answers, reply_callback)
```

### Market Data Processing
```python
# Fetch market data
responses = {
    "AAPL": client.marketdata_history_by_conid(...),
    "MSFT": client.marketdata_history_by_conid(...)
}

# Clean up responses
cleaned = cleanup_market_history_responses(responses, raise_on_error=False)
```

---

## Error Handling

### Graceful Degradation
- `cleanup_market_history_responses()`: Stores exceptions instead of crashing
- `Tickler`: Logs errors but continues running
- `filter_stocks()`: Skips invalid symbols with logging

### Validation
- `parse_order_request()`: Validates conid/conidex mutual exclusivity
- `date_from_ibkr()`: Validates date format
- `question_type_to_message_id()`: Validates QuestionType mapping

### Logging
- Comprehensive logging throughout with `_LOGGER`
- Different log levels (INFO, WARNING, ERROR) based on severity
- Structured error messages with context

---

## Dependencies

### Internal Dependencies
- `ibind.base.rest_client`: Result, pass_result
- `ibind.client.ibkr_definitions`: decode_data_availability
- `ibind.support.errors`: ExternalBrokerError
- `ibind.support.logs`: project_logger
- `ibind.support.py_utils`: UNDEFINED, ensure_list_arg, VerboseEnum, OneOrMany, exception_to_string
- `ibind.var`: IBIND_TICKLER_INTERVAL

### Standard Library
- `datetime`: Date/time handling
- `threading`: Tickler thread management
- `dataclasses`: Data structure definitions
- `typing`: Type hints
- `warnings`: Deprecation warnings
- `pprint`: Pretty printing for debugging

---

## Performance Considerations

### Memory Efficiency
- `OrderRequest.to_dict()`: Excludes None values to reduce payload size
- `process_instruments()`: Filters in-place when possible
- `cleanup_market_history_responses()`: Processes data lazily

### Thread Safety
- `Tickler`: Uses threading.Event for clean shutdown
- Thread-safe logging throughout

### API Efficiency
- `query_to_symbols()`: Batches symbols for fewer API calls
- `filter_stocks()`: Reduces data transfer by filtering server-side when possible

---

## Best Practices

### 1. Use StockQuery for Precise Filtering
Always use `StockQuery` objects instead of raw strings for better control over filtering.

### 2. Prefer OrderRequest Dataclass
Use `OrderRequest` instead of deprecated `make_order_request()` function.

### 3. Implement Question Handling
Always implement `handle_questions()` for robust order submission.

### 4. Use Tickler for Long Sessions
Start `Tickler` for sessions longer than a few minutes to prevent timeouts.

### 5. Handle Market Data Errors Gracefully
Use `raise_on_error=False` in `cleanup_market_history_responses()` for production systems.

### 6. Validate Inputs
Use the built-in validation functions before making API calls.

---

## Notes

- This module is critical for the proper functioning of the IBKR client mixins
- Many functions assume US market defaults (isUS=True)
- The QuestionType system may need updates as IBKR adds new warning types
- The Tickler interval (60 seconds) is configurable via `ibind.var.IBIND_TICKLER_INTERVAL`
- Always check for deprecation warnings when using legacy functions

---

**Analysis Complete:** ✅  
**Total Components Analyzed:** 7 major categories  
**Key Classes:** 3 (StockQuery, QuestionType, Tickler, OrderRequest)  
**Key Functions:** 15+  
**Lines of Code:** ~800

*For the most up-to-date information, refer to the official IBKR API documentation and the `ibind` package source code.*
