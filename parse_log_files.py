from typing import List, Dict, Tuple
import sys
import json

# Mapping of sample layout in email and v2 log files
DEFAULT_LAYOUT = {
    "version": 0,
    "account_id": 1,
    "interface_id": 2,
    "srcaddr": 3,
    "dstaddr": 4,
    "srcport": 5,
    "dstport": 6,
    "protocol": 7,
    "packets": 8,
    "bytes": 9,
    "start": 10,
    "end": 11,
    "action": 12,
    "log_status": 13
}

# Mapping of integer protocols to str representations 
PROTOCOL_MAP =  {
    "6": "tcp",
    "17": "udp",
    "1": "icmp",
    "2": "igmp",
    "4": "ipip",
    "132": "sctp",
    "50": "esp",
    "51": "ah",
    "88": "eigrp",
    "89": "ospf"
}

def main():
    """
    Main program and intakes 2-3 arguments 
    First arg: lookup file
    Second arg: log file
    Third arg (optional): custom layout json for layout
    """
    if len(sys.argv) < 3:
        print("Usage: python3 parse_log_files.py <lookup_file.csv> <log_file> <optional log_layout_file.json>")
        sys.exit(1)
    # Lookup and Log Files
    lookup_file_path = sys.argv[1]
    log_file_path = sys.argv[2]
    # Option Layout File
    if len(sys.argv) > 3:
        layout_file_path = sys.argv[3]
        layout_file = json_to_layout(layout_file_path)
    else:
        layout_file = DEFAULT_LAYOUT
    parse_log_files(lookup_file_path, log_file_path, layout_file)
    

def parse_log_files(lookup_file_path : str, log_file_path : str, log_layout : Dict[str, int]):
    """
    Process log and lookup files, then write results to files.
    """
    # Opening lookup table file
    lookup_lines = open_file(lookup_file_path)
    # Splitting lookup file into header and tag data
    headers = split_line(lookup_lines[0], ",")
    tag_lines = lookup_lines[1:]
    # Creating dictionaries to track deliverables
    lookup_table, lookup_key_count, tag_count = extract_tag_data(headers, tag_lines)
    # Opening log files
    log_lines = open_file(log_file_path)
    # Adding data to different tables
    extract_log_data(log_lines, log_layout, headers, lookup_table, lookup_key_count, tag_count)
    # Writing deliverables 
    write_tag_counts("tag_counts.txt", tag_count)
    write_port_protocol("port_protocol_comb.txt", lookup_key_count)

def extract_tag_data(headers : List[str], tag_lines : List[str]) -> Tuple[Dict[Tuple, str], Dict[Tuple, int], Dict[str, int]]:
    """
    Extract tags and create lookup tables from tag lines.
    """
    # Creating lookup table
    header_length = len(headers)
    tag_count = { "Untagged": 0 } # Records times a tag is mapped to
    lookup_key_count = {} # Records different combinations of lookup table used
    lookup_table = {} # Lookup table made from lookup file, maps (log attributes) : tag
    
    for tag_line in tag_lines:
        # Splitting line into tokens, skipping empty lines
        tag_toks = split_line(tag_line, ",")
        if not tag_toks:
            continue
        # Checking if there are enough tokens
        if len(tag_toks) != (header_length):
            print(f"Error: tag line '{tag_line}' does not have enough tokens\nExpected {header_length} but got {len(tag_toks)}")
            continue
        # Managing tags
        lookup_key, tag = create_key_tag(headers, tag_toks)
        # Managing keys for lookup 
        tag_count[tag] = 0
        lookup_table[lookup_key] = tag
        lookup_key_count[lookup_key] = 0
    
    return  lookup_table, lookup_key_count, tag_count

def create_key_tag(headers : List[str], tag_toks : List[str]) -> Tuple[Tuple[str], str]:
    """Creates a key : tag combo from the lookup table file for progams own lookup table"""
    lookup_key = []
    tag = ""
    for header, data in zip(headers, tag_toks):
        if header == "tag":
            tag = data
        else:
            lookup_key.append(data)
    lookup_key = tuple(lookup_key)
    return lookup_key, tag

def extract_log_data(log_lines : List[str], 
                   log_layout : Dict[str, int ] ,
                   headers : List[str], 
                   lookup_table : Dict[Tuple, str],
                   lookup_key_count: Dict[Tuple, int], 
                   tags_count : Dict[str, int],
                   ) -> None: 
    """
    Process log files lines and records the different attribute combinations of the 
    and the total hits for the tag
    """
    # List that contains the columns needed for lookup map
    lookup_cols = [log_layout[header] for header in headers if header != "tag" and log_layout[header] < len(log_layout)] # not using tag and making sure indexs in 
    for log_line in log_lines:
        # Splitting log into tokens
        log_toks = split_line(log_line, " ")
        if not log_toks:
            continue
        if len(log_toks) != len(log_layout):
            print(f"Error: Log line '{log_line}' does not have enough tokens. Expected {len(log_layout)} but got {len(log_toks)}.")

        # Creating the key for the specific columns of the log
        log_key = process_log_key(log_toks, lookup_cols, log_layout)
        # Find tag in lookup table and incrementing tags used
        if log_key in lookup_table:
            tag = lookup_table[log_key]
            tags_count[tag] += 1
        else:
            tags_count["Untagged"] += 1
        # Incrementing log_key used
        if log_key not in lookup_key_count:
            lookup_key_count[log_key] = 0
        lookup_key_count[log_key] += 1
        
def process_log_key(log_toks : List[str], lookup_cols : List[int], log_layout : Dict[str, int]) -> Tuple[str]:
    """Create a hashable key from logs tokens from the lookup tables headers and returns  key"""
    log_key = []
    for col_i in lookup_cols:
        if col_i == log_layout["protocol"]:
            log_toks[col_i] = PROTOCOL_MAP[log_toks[col_i]]
        log_key.append(log_toks[col_i])
    return tuple(log_key)

def write_tag_counts(file_path : str, tag_counts : Dict[str, int]) :
    """Writes tag count deliverable"""
    try:
        with open(file_path, 'w') as file:
            file.write("Tag Counts: \nTag,Count \n")
            for tag in tag_counts:
                file.write(tag + ',' + str(tag_counts[tag]) + "\n")
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")

def write_port_protocol(file_path : str, lookup_key_counts : Dict[Tuple[str], int]) :
    """Write port protocol deliverable"""
    try:
        with open(file_path, 'w') as file:
            file.write("Port/Protocol Combination Counts:\nPort,Protocol,Count\n")
            for combo in lookup_key_counts :
                line = list(combo) + [str(lookup_key_counts[combo])]
                line = ",".join(line)
                file.write(line + '\n')
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")

def open_file(file_path : str) -> List[str]:
    try:
        with open(file_path, 'r') as file:
            file_lines = file.readlines()
            return file_lines
    except FileNotFoundError:
        # Handle the case where the file does not exist
        raise FileNotFoundError(f"Error: The file {file_path} does not exist.")
    except IOError as e:
        # Handle other I/O related errors
        raise IOError(f"Error: An I/O error occurred: {e}")

def split_line(line : str, delim : str) -> List[str]:
     # Cleaning line
    line = line.strip()
    # Skipping blank lines
    if not line:
        return []
    return [token for token in line.split(delim) if token]

def json_to_layout(layout_file_path : str) -> Dict[str, int]:
    try:
        with open(layout_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {layout_file_path} does not exist.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()