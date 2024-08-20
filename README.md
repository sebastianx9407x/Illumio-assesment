# Illumio Technical

## Overview

This is my submission for the technical assessment. All implementation is done in parse_log_files.py. My approach involves reading the lookup file and constructing a dictionary with the format (dstport, protocol): tag. After creating this lookup table, I process each log line individually, extracting the (dstport, protocol) attributes for that specific log entry. I then check if this combination exists in the previously created lookup table. If a match is found, the corresponding tag's count is incremented in a dictionary. Additionally, the (dstport, protocol) combinations are tracked and incremented in a separate dictionary

## Assumptions

### Lookup Table File
1. Program will raise error if there is failure to open
2. The header column will always be present in the first row of the lookup file.
3. The fields `dstport`, `protocol`, and `tag` will always be present in the lookup file, although their order may vary.
4. If a row in the lookup file is missing a required field, the entire tag associated with that row will be skipped.

### Flow Log Records File
1. The default v2 format for flow log records will always be used unless otherwise specified in the inputs.
2. If a log entry is missing a required field, it will be skipped, and an error message will be printed to the terminal.
3. Only the following protocols will be used: 
```python
     {
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
```
Any other protocol will result in an error.

### Output File
1. The formats of the output file will be present like that of the email for the assessment and failure to write to either file will print error to the terminal
2. Files will be created regardless if there is data or not
3. The counts of each tag will be written to a file called `tag_counts.txt`.
4. The counts of port/protocol combinations will be written to `port_protocol_comb.txt`.


## Analysis

### Data Structures
- **Lookup Table**: A dictionary mapping tuples of log attributes to tags would take O(t) space where t is the number of unique mappings in the layout table.
- **Log Combination Table**: A dictionary tracking counts of different combinations of flow log (dstport, protocol) combos and would be O(p * n) where p is the total number of ports and n is the total number of protocols is the number of mappings in the flow log records.
- **Tag Count**: A dictionary recording how many times each tag is encountered would be O(t) where t is the number of mappings in the layout table since worse case scenario there is t unique tags.
- **Space**: From this, we can conclude that the Space complexity is 
O(p*n) + 2*O(t) = O(p*n) + O(t) where p = total ports, n = total protocol and t = total unique tags 

- **Time Complexity** The time complexity for this program could be pretty complex. Still, for simplicity, I would say O(3 * n) + O(13 * m ) = O(n) + O(m ) where n is the total number of lines in the lookup file and m is the total number of lines in the flow log file since we read through both files only once. I also use different methods like strip and split that would also iterate over these lines but would keep both linear. 
## How to Run

1. **Required Files**:
   - **Lookup Table CSV**: This file should contain a header row and the necessary data for mapping `(dstport, protocol)` pairs to tags.
   - **Flow Log File**: The log file to be processed using the lookup table.

2. **Optional File**:
   - **Custom Layout JSON**: If you are using a format other than the default v2, you can provide a custom JSON layout file. This file should be formatted similarly to `sample_layout.json` and must include mappings for `dstport` and `protocol`.

     ```json
     
     "field, column"
     {
     
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
     ```

3. **Run the Script**:
- layout
   ```bash
   python3 script_name.py <lookup_file_path> <log_file_path> [<optional_json_layout>]
    ```
- ex1
    ```bash
    python3 parse_log_files.py sample_lookup_table.csv 
    ```
- ex2
    ```bash
   python3 parse_log_files.py sample_lookup_table.csv sample_flow_logs.txt  
    ```

