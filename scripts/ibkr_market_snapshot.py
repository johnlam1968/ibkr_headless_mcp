#!/usr/bin/env python3
"""
IBKR Market Data Snapshot Script
Simple script to fetch market data for given conids.
Used by cron jobs - takes conids as argument.

Usage: python3 ibkr_market_snapshot.py <conid1,conid2,...> [--fields FIELDS] [--delay SECONDS]
"""

import json
import sys
import subprocess
import time
import argparse

WRAPPER = "/home/node/.openclaw/workspace/bin/ibkr_mcp_wrapper.py"

# Default fields - underlying asset watchlist (53 fields, edited by user)
# Note: IBKR API max 50 fields per request - batch if needed
DEFAULT_FIELDS = (
    "31,55,70,71,82,83,84,86,87,"
    "6008,6070,6457,7051,"
    "7084,7085,7086,7087,7088,7089,"
    "7282,7283,7285,7289,7290,7291,"
    "7293,7294,7295,7296,"
    "7607,7633,7638,7644,7655,"
    "7674,7675,7676,7677,"
    "7682,7683,7684,7685,7686,7687,7688,7689,7690,"
    "7718,7741,7762"
)


def call_endpoint(path, params):
    """Call IBKR endpoint via wrapper"""
    cmd = ["python3", WRAPPER, "call_endpoint", f"path:{path}", f"params:{params}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None


def authenticate():
    """Authenticate with IBKR"""
    return call_endpoint("iserver/accounts", "{}")


def get_snapshot(conids, fields=None, delay=50):
    """Get market data snapshot for conids
    
    Args:
        conids: comma-separated conid string
        fields: comma-separated field codes (uses DEFAULT_FIELDS if None)
        delay: seconds to wait between first and second API call (default 25)
    """
    if fields is None:
        fields = DEFAULT_FIELDS
    
    params = json.dumps({"conids": conids, "fields": fields})
    
    # Call TWICE as per IBKR API requirements
    # First call initiates the request
    result1 = call_endpoint("iserver/marketdata/snapshot", params)
    
    # Delay to let IBKR calculate derived fields (especially EMA, price data)
    time.sleep(delay)
    
    # Second call gets the actual data
    result2 = call_endpoint("iserver/marketdata/snapshot", params)
    return result2 if result2 else result1


# Field code mapping (generated via ibind snapshot_ids_to_keys)
FIELD_NAMES = {
    31: "last_price", 55: "symbol", 70: "high", 71: "low",
    82: "change", 83: "change_percent", 84: "bid_price", 86: "ask_price",
    87: "volume", 6008: "conid", 6070: "sec_type", 6457: "underlying_conid",
    7051: "company_name", 7084: "implied_vol_hist_vol_percent",
    7085: "put_call_interest", 7086: "put_call_volume", 7087: "hist_vol_percent",
    7088: "hist_vol_close_percent", 7089: "opt_volume",
    7282: "average_volume_90", 7283: "option_implied_vol_percent",
    7285: "put_call_ratio", 7289: "market_cap", 7290: "p_e", 7291: "eps",
    7293: "52_week_high", 7294: "52_week_low", 7295: "open", 7296: "close",
    7607: "opt_volume_change_percent", 7633: "implied_vol_percent",
    7638: "option_open_interest", 7644: "shortable", 7655: "morningstar_rating",
    7674: "ema_200", 7675: "ema_100", 7676: "ema_50", 7677: "ema_20",
    7682: "change_since_open", 7683: "upcoming_event",
    7684: "upcoming_event_date", 7685: "upcoming_analyst_meeting",
    7686: "upcoming_earnings", 7687: "upcoming_misc_event",
    7688: "recent_analyst_meeting", 7689: "recent_earnings",
    7690: "recent_misc_event", 7718: "beta", 7741: "prior_close",
    7762: "volume_long",
}


def format_output(data):
    """Format the output nicely with field names"""
    if not data or "data" not in data:
        return "No data"
    
    output_lines = []
    
    for item in data.get("data", []):
        symbol = item.get("55", "-")
        output_lines.append(f"\n{symbol} ============================================================")
        
        # === Price (7 fields) ===
        output_lines.append("[Price]")
        output_lines.append("  Last: {} Bid: {} Ask: {}".format(
            item.get("31", "-"), item.get("84", "-"), item.get("86", "-")))
        output_lines.append("  High: {} Low: {}".format(
            item.get("70", "-"), item.get("71", "-")))
        output_lines.append("  Change: {} Change%: {}".format(
            item.get("82", "-"), item.get("83", "-")))
        
        # === Volume (2 fields) ===
        vol = item.get("87", "-")
        avg_vol = item.get("88", "-")
        if vol != "-":
            output_lines.append("[Volume] Volume: {} AvgVolume: {}".format(vol, avg_vol))
        
        # === Fundamentals (3 fields) ===
        mcap = item.get("7289", "-")
        pe = item.get("7290", "-")
        eps = item.get("7608", "-")
        if mcap != "-" or pe != "-" or eps != "-":
            output_lines.append("[Fundamentals] Company: MarketCap: {} P/E: {} EPS: {}".format(
                mcap, pe, eps))
        
        # === Volatility (3 fields) ===
        iv = item.get("7283", "-")
        hv = item.get("7087", "-")
        pc = item.get("7085", "-")
        if iv != "-" or hv != "-" or pc != "-":
            output_lines.append("[Volatility] IV%: {} HistVol%: {} PCRatio: {}".format(iv, hv, pc))
        
        # === EMA (4 fields) ===
        ema200 = item.get("7674", "-")
        ema100 = item.get("7675", "-")
        ema50 = item.get("7676", "-")
        ema20 = item.get("7677", "-")
        if ema200 != "-" or ema100 != "-" or ema50 != "-" or ema20 != "-":
            output_lines.append("[EMA] EMA(200): {} EMA(100): {} EMA(50): {} EMA(20): {}".format(
                ema200, ema100, ema50, ema20))
        
        # === Options (5 fields) ===
        opt_vol = item.get("7057", "-")
        opt_oi = item.get("7058", "-")
        call_vol = item.get("7059", "-")
        put_vol = item.get("7060", "-")
        exch_codes = item.get("7065", "-")
        if opt_vol != "-" or opt_oi != "-":
            output_lines.append("[Options] OptVolume: {} OptOI: {} CallVol: {} PutVol: {} Exch: {}".format(
                opt_vol, opt_oi, call_vol, put_vol, exch_codes))
        
        # === Exchange ===
        exchange = item.get("6509", "-")
        if exchange != "-":
            output_lines.append("[Exchange] {}".format(exchange))
    
    return "\n".join(output_lines)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="IBKR Market Data Snapshot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ibkr_market_snapshot.py 756733,320227571
  python3 ibkr_market_snapshot.py 756733 --delay 30
  python3 ibkr_market_snapshot.py 756733 --fields="31,84,86,7289"
        """
    )
    parser.add_argument("conids", nargs="?", help="Comma-separated conids")
    parser.add_argument("--fields", "-f", default=None, help="Comma-separated field codes (default: all fields)")
    parser.add_argument("--delay", "-d", type=int, default=50, help="Delay seconds between API calls (default: 50)")
    
    args = parser.parse_args()
    
    if not args.conids:
        print("Usage: python3 ibkr_market_snapshot.py <conid1,conid2,...> [--fields FIELDS] [--delay SECONDS]", file=sys.stderr)
        print(f"Default fields: {DEFAULT_FIELDS}", file=sys.stderr)
        print("\nField codes:", file=sys.stderr)
        for code, name in FIELD_NAMES.items():
            print(f"  {code}: {name}", file=sys.stderr)
        sys.exit(1)
    
    # Authenticate
    print("Authenticating with IBKR...", file=sys.stderr)
    auth_result = authenticate()
    if not auth_result:
        print("Failed to authenticate!", file=sys.stderr)
        sys.exit(1)
    
    # Get snapshot
    print(f"Fetching market snapshots for {len(args.conids.split(','))} conids (delay={args.delay}s)...", file=sys.stderr)
    result = get_snapshot(args.conids, args.fields, delay=args.delay)
    
    if result:
        # Map field IDs to human-readable names
        def map_fields(item):
            if not isinstance(item, dict):
                return item
            mapped = dict(item)
            
            # Map numeric field IDs to names
            for field_id, field_name in FIELD_NAMES.items():
                str_id = str(field_id)
                if str_id in mapped:
                    mapped[field_name] = mapped.pop(str_id)
            
            # Map 6509 (returned by IBKR even if not requested) to readable name
            if '6509' in mapped:
                mapped['market_data_availability'] = mapped.pop('6509')
            
            # Rename _raw fields to their mapped names
            if '87_raw' in mapped:
                mapped['volume_long'] = mapped.pop('87_raw')
            if '7282_raw' in mapped:
                mapped['average_volume_90_raw'] = mapped.pop('7282_raw')
            
            # Remove unnecessary fields
            for key in ['conidEx', '6119', 'server_id', '6508']:
                mapped.pop(key, None)
            
            # Map 6509 (Market Data Availability) codes to text
            # Z=SMART, B=CBOE, etc.
            return mapped
        
        # Transform each item in the result
        if isinstance(result, dict) and 'data' in result:
            result['data'] = [map_fields(item) for item in result.get('data', [])]
        elif isinstance(result, list):
            result = [map_fields(item) for item in result]
        
        print(json.dumps(result))
    else:
        print("Failed to get market data", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
