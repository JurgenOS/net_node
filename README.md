# net_node
small package for network devices cli automatization

### supported vendors:
 - Cisco
 - Huawei
 - Hp
 - H3c

### How to use:
 1. clone or download repo
 2. if you dowload .zip file, unzip and rename "net_node-main" folder to "net_node"
 3. run 'pip -e install net_node'
 4. enjoy

## Example
```python
from net_node import Node

ip_address = '1.1.1.1'
user = 'user_name'
password = 'password'

n = Node(ip_address)

# to save log, specify log directory name like 'log'
# n = Node('1.1.1.1', 'log')
# By default log directory is the current directory

n.user = user
n.password = password

n.snmp_community_list = [
    'snmp_community1',
    'snmp_community2'
]

n.get_info_snmp()
n.get_info()
n.log_in()

n.send_short_command(
    n.command_config_mode + 
    'interface gig 0/0/1' + '\n' +
    'shutdow' + '\n' + 
    n.command_to_root + 
    n.command_save
)

n.get_running_config()

n.log_out()

for line in n.running_config.split('\n'):
    print(line)
```
