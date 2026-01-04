TARGET_COMMAND_URLS = {
    # File processing & handling
    "find": "https://man7.org/linux/man-pages/man1/find.1.html",
    "grep": "https://man7.org/linux/man-pages/man1/grep.1.html",
    "gawk": "https://linuxcommand.org/lc3_man_pages/awk1.html",
    "tar": "https://man7.org/linux/man-pages/man1/tar.1.html",
    "rsync": "https://man7.org/linux/man-pages/man1/rsync.1.html",
    "chmod": "https://man7.org/linux/man-pages/man1/chmod.1.html",
    "cat": "https://man7.org/linux/man-pages/man1/cat.1.html",
    "sed": "https://man7.org/linux/man-pages/man1/sed.1.html",
    "sort": "https://man7.org/linux/man-pages/man1/sort.1.html",
    "cut": "https://man7.org/linux/man-pages/man1/cut.1.html",
    "tr": "https://man7.org/linux/man-pages/man1/tr.1.html",
    "wc": "https://man7.org/linux/man-pages/man1/wc.1.html",
    "head": "https://man7.org/linux/man-pages/man1/head.1.html",
    "tail": "https://man7.org/linux/man-pages/man1/tail.1.html",
    "uniq": "https://man7.org/linux/man-pages/man1/uniq.1.html",
    # Networking
    "ip": "https://man7.org/linux/man-pages/man8/ip.8.html",
    "ss": "https://man7.org/linux/man-pages/man8/ss.8.html",
    "ping": "https://man7.org/linux/man-pages/man8/ping.8.html",
    "traceroute": "https://man7.org/linux/man-pages/man8/traceroute.8.html",
    "dig": "https://man.archlinux.org/man/dig.1",
    "tcpdump": "https://man7.org/linux/man-pages/man1/tcpdump.1.html",
    "nmap": "https://man7.org/linux/man-pages/man1/nmap.1.html",
    "nslookup": "https://man.archlinux.org/man/nslookup.1",
    "curl": "https://man7.org/linux/man-pages/man1/curl.1.html",
    "ethtool": "https://man7.org/linux/man-pages/man8/ethtool.8.html",
}

TARGET_COMMAND_SECTIONS = {
    # File processing & handling
    "find": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "EXPRESSION", 
        "POSITIONAL OPTIONS", "GLOBAL OPTIONS", "TESTS", "ACTIONS", 
        "OPERATORS", "UNUSUAL FILENAMES", "STANDARDS CONFORMANCE", 
        "ENVIRONMENT VARIABLES", "EXAMPLES"
    ],
    "grep": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "REGULAR EXPRESSIONS", 
        "ENVIRONMENT", "EXAMPLE"
    ],
    "awk": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "OPERANDS", "STDIN", 
        "INPUT FILES", "ENVIRONMENT VARIABLES", "STDOUT", "STDERR", 
        "OUTPUT FILES", "EXTENDED DESCRIPTION", "APPLICATION USAGE", "EXAMPLES"
    ],
    "tar": ["NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS"],
    "rsync": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "GENERAL", "USAGE", 
        "COPYING TO A DIFFERENT NAME", 
        "SORTED TRANSFER ORDER", "MULTI-HOST SECURITY", "ADVANCED USAGE", 
        "CONNECTING TO AN RSYNC DAEMON", 
        "USING RSYNC-DAEMON FEATURES VIA A REMOTE-SHELL CONNECTION", 
        "STARTING AN ASYNC DAEMON TO ACCEPT CONNECTIONS", 
        "EXAMPLES", "OPTIONS", "DAEMON OPTIONS", "FILTER RULES", "TRANSFER RULES", 
        "BATCH MODE", "SYMBOLIC LINKS", "ENVIRONMENT VARIABLES"
    ],
    "chmod": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "SETUID AND SETGID BITS", 
        "RESTRICTED DELETION FLAG OR STICKY BIT", "OPTIONS"
    ],
    "cat": ["NAME", "SYNOPSIS", "DESCRIPTION", "EXAMPLES"],
    "sed": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "COMMAND SYNOPSIS", "REGULAR EXPRESSIONS"
    ],
    "sort": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "cut": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "tr": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "wc": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "head": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "tail": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    "uniq": ["NAME", "SYNOPSIS", "DESCRIPTION"],
    # Networking
    "ip": [
        "NAME", "SYNOPSIS", "OPTIONS", "IP-COMMAND SYNTAX", "ENVIRONMENT", "EXAMPLES"
    ],
    "ss": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "STATE-FILTER", "EXPRESSION", 
        "HOST SYNTAX", "USAGE EXAMPLES"
    ],
    "ping": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "IPV6 LINK-LOCAL DESTINATIONS", 
        "ICMP PACKET DETAILS", "DUPLICATE AND DAMAGED PACKETS", "ID COLLISIONS", 
        "TRYING DIFFERENT DATA PATTERNS", "TTL DETAILS"
    ],
    "traceroute": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", 
        "LIST OF AVAILABLE METHODS", "NOTES"
    ],
    "dig": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "SIMPLE USAGE", 
        "QUERY OPTIONS", "MULTIPLE QUERIES"
    ],
    "tcpdump": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS", "EXAMPLES", "OUTPUT FORMAT"
    ],
    "nmap": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "TARGET SPECIFICATION", "HOST DISCOVERY", 
        "PORT SCANNING BASICS", "PORT SCANNING TECHNIQUES", 
        "PORT SPECIFICATION AND SCAN ORDER", "SERVICE AND VERSION DETECTION", 
        "OS DETECTION", "NMAP SCRIPTING ENGINE (NSE)", "TIMING AND PERFORMANCE", 
        "FIREWALL/IDS EVASION AND SPOOFING", "OUTPUT", 
        "MISCELLANOUS OPTIONS", "EXAMPLES"
    ],
    "nslookup": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "ARGUMENTS", "INTERACTIVE COMMANDS"
    ],
    "curl": [
        "NAME", "SYNOPSIS", "DESCRIPTION", "URL", "GLOBBING", "VARIABLES", "OUTPUT", 
        "PROTOCOLS", "PROGRESS METER", "OPTIONS", "ENVIRONMENT", 
        "PROXY PROTOCOL PREFIXES"
    ],
    "ethtool": ["NAME", "SYNOPSIS", "DESCRIPTION", "OPTIONS"],
}