

# HOST_NAME_REG = b'^[<\[]{0,2}' \
#                 b'[a-zA-Z0-9_ ()|\\\/@.,-]{2,}\s?[a-zA-Z0-9_()|\\\/@.,-]{0,}' \
#                 b'([>\]#]|((>)? \(enable\)))( >)?\s*?$'


HOST_NAME_REG = b'((?P<first_parenthesis>^[<\[]{1,2})[a-zA-Z0-9_ ()|\\\/@.,#-]{2,}\s?[a-zA-Z0-9_()|\\\/@.,#-]{0,}((?(first_parenthesis)[>\]])|((>)? \(enable\)))( >)?\s*?$)|(^[a-zA-Z0-9_()|\\\/@.,-]{2,}(#|>)\s*?$)'


corrupted_images_names = [
    'asr1002x-universalk9_npe_noli.03.10.03.S.153-3.S3-ex',
    'asr1000rp1-adventerprisek9.03.16.07b.S.155-3.S7b-ext.',
    'c2960-lanlitek9-mz.150-2.SE6',
    'c2960s-universalk9-mz.122-55.SE7',
    'c2960s-universalk9-mz.122-55.SE8',
]

node_id_reg = '([a-z0-9]+),?\s' # cisco = processor id, huawei = platform id

max_vty_line_number_reg = '-(\d+)>'
