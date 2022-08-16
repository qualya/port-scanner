# server-scanner
#### Features:
- Scan IPs and ports within specified ranges to find open servers
- Process addresses of open servers as web pages or Minecraft servers to get more information about large lists of open servers
- Process individual addresses, addresses from a text file, or process addresses using the program's file structure system
- Extract data from the file structure into a single file

#### Installation:
- Clone the project
- Run `pip install -r requirements.txt`

#### File Structure:
Scanned addresses that have open servers will be stored in the servers folder. Within that folder, there will be folders seperating open servers by the first number of the IP address. Within that folder, there will be txt files for each of the scanned port numbers. For example, the address 123.45.67.89:80 would be found in /servers/123/80.txt.\
Similarly, servers that are processed as either web pages or Minecraft servers will follow the same structure except in the servers-data folder instead of the servers folder.
