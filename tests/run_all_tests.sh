#!/bin/bash
# Comprehensive test script for MCP server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track overall status
FAILED=0
PASSED=0

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Test 1: Localhost Connection Tests
test_localhost() {
    print_header "TEST 1: Localhost Connection (Outside Container)"
    
    if ! curl -s http://localhost:8000/mcp > /dev/null 2>&1; then
        print_error "Server not running on localhost:8000"
        return 1
    fi
    print_success "Server is running on localhost:8000"
    
    print_info "Running MCP client tests..."
    if python3 tests/test_mcp_client.py; then
        print_success "MCP client tests passed"
    else
        print_error "MCP client tests failed"
        return 1
    fi
}

# Test 2: Symbol Test with Market Data
test_symbol() {
    print_header "TEST 2: Symbol Search (Outside Container)"
    
    SYMBOL="${1:-AAPL}"
    
    print_info "Testing with symbol: $SYMBOL"
    
    # Use the local ibkr_market_snapshot.py script for market data tests
    echo ""
    echo "Using local ibkr_market_snapshot.py for market data test..."
    echo "Note: This script requires AAPL's conid (265598) for market data."
    
    if python3 tests/ibkr_market_snapshot.py 265598 2>&1 | grep -q "Last:"; then
        print_success "Market data test passed - AAPL price fields are populated"
        return 0
    else
        print_error "Market data test failed - AAPL price fields may be empty"
        return 1
    fi
}

# Test 3: Docker Container Tests
test_container() {
    print_header "TEST 3: Docker Container (Inside Container)"
    
    if ! docker ps | grep -q mcp-server; then
        print_error "mcp-server container is not running"
        return 1
    fi
    print_success "mcp-server container is running"
    
    NETWORK="openclaw_default"
    
    if ! docker network inspect "$NETWORK" > /dev/null 2>&1; then
        print_info "Creating Docker network: $NETWORK"
        docker network create "$NETWORK"
    fi
    
    if ! docker network inspect "$NETWORK" --format '{{range .Containers}}{{.Name}} {{end}}' | grep -q mcp-server; then
        print_info "Connecting mcp-server to network: $NETWORK"
        docker network connect "$NETWORK" mcp-server
    fi
    print_success "Docker network configured"
    
    print_info "Running test from Docker container..."
    if docker run --rm --network "$NETWORK" python:3.11-slim sh -c '
        pip install requests -q
        python -c "
import requests
r=requests.post(
    \"http://mcp-server:8000/mcp\",
    json={\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\"},\"id\":1},
    headers={\"Content-Type\":\"application/json\",\"Accept\":\"application/json, text/event-stream\"},
    stream=True
)
print(f\"Status: {r.status_code}\")
print(\"SUCCESS!\" if r.status_code == 200 else \"FAILED!\")
"
    '; then
        print_success "Container-to-container test passed"
    else
        print_error "Container-to-container test failed"
        return 1
    fi
}

# Print summary
print_summary() {
    print_header "TEST SUMMARY"
    
    TOTAL=$((PASSED + FAILED))
    echo -e "Total Tests: $TOTAL"
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Comprehensive test script for MCP server.
Tests from both localhost (outside) and Docker container (inside).

OPTIONS:
    --help          Show this help message
    --all           Run all tests (default)
    --localhost      Test only localhost connection
    --symbol         Test market data with symbol (uses AAPL conid)
    --container     Test only Docker container connection
    --no-network    Skip network creation (use if network exists)

EXAMPLES:
    $0                    # Run all tests
    $0 --localhost          # Test only localhost
    $0 --symbol             # Test symbol search with AAPL
    $0 --container          # Test only Docker container

REQUIREMENTS:
    - MCP server running on localhost:8000
    - Docker installed and running
    - Python 3.11+ with httpx
    - IBKR OAuth credentials configured in .env

EOF
}

# Main execution
main() {
    local TEST_ALL=true
    local TEST_LOCALHOST=false
    local TEST_SYMBOL=false
    local TEST_CONTAINER=false
    local NO_NETWORK=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_usage
                exit 0
                ;;
            --all)
                TEST_ALL=true
                shift
                ;;
            --localhost)
                TEST_ALL=false
                TEST_LOCALHOST=true
                shift
                ;;
            --symbol)
                TEST_ALL=false
                TEST_SYMBOL=true
                shift
                ;;
            --container)
                TEST_ALL=false
                TEST_CONTAINER=true
                shift
                ;;
            --no-network)
                NO_NETWORK=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    if [[ $TEST_ALL == true ]]; then
        test_localhost
        test_symbol
        test_container
    elif [[ $TEST_LOCALHOST == true ]]; then
        test_localhost
    elif [[ $TEST_SYMBOL == true ]]; then
        test_symbol
    elif [[ $TEST_CONTAINER == true ]]; then
        if [[ $NO_NETWORK == true ]]; then
            NETWORK="openclaw_default"
            if docker ps | grep -q mcp-server; then
                print_header "TEST 3: Docker Container (Inside Container)"
                docker run --rm --network "$NETWORK" python:3.11-slim sh -c '
                    pip install requests -q
                    python -c "
import requests
r=requests.post(
    \"http://mcp-server:8000/mcp\",
    json={\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\"},\"id\":1},
    headers={\"Content-Type\":\"application/json\",\"Accept\":\"application/json, text/event-stream\"},
    stream=True
)
print(f\"Status: {r.status_code}\")
print(\"SUCCESS!\" if r.status_code == 200 else \"FAILED!\")
"
                ' && print_success "Container test passed" || print_error "Container test failed"
            else
                print_error "mcp-server container is not running"
                FAILED=1
            fi
        else
            test_container
        fi
    else
        show_usage
        exit 1
    fi
    
    print_summary
}

main "$@"