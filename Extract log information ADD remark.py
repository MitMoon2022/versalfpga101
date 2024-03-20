'Extract log information -  apply at wrapper\log\top    XXX.log'

import os
import csv
import re

filename = "fLogG_5.csv"

header1 = ["SN", "Test site", "Chip Temperature", 'DNA', "killsystest", 'read_dna', 'contact_check',
           'apuburst_r001', 'rpuburst_r001', 'aie2char_r001', 'STARTDT', 'ENDDT', 'remark']

Param1 = "Versal_VC2802_ES1_LPNOM_ALL"

def write_to_file(output):
    with open(filename, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header1, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(output)

cwd = os.getcwd()
files = os.listdir(cwd)

keys = ['SN', 'Test site']
lis_dic = []

for file in files:
    if file.endswith('.log'):
        data = {}
        with open(os.path.join(cwd, file), 'r') as f:
            for line in f:
                words = line.strip().split(":")
                if len(words) == 2:
                    key = words[0]
                    value = words[1]
                    data[key] = value.strip()
                else:
                    key = words[0].replace('TEST', "").strip()
                    value = words[-1].replace('Result', "").replace("PASS", 'P').replace('1', 'P').replace("FAIL",
                                                                                                              'F')
                    if key == Param1:
                        val_time_start = re.sub(r'.*START (.*)::End(.*)::Result.*', r'\1', line)
                        val_time_end = re.sub(r'.*START (.*)::End(.*)::Result.*', r'\2', line)
                        data["STARTDT"] = val_time_start.strip()
                        data["ENDDT"] = val_time_end.strip()
                    else:
                        data[key] = value.strip()

        # Adding the "remark" column based on specified keys
        if 'apuburst_r001' in data and 'rpuburst_r001' in data and 'aie2char_r001' in data:
            if data['apuburst_r001'] == 'P' and data['rpuburst_r001'] == 'P' and data['aie2char_r001'] == 'P':
                data['remark'] = 'P'
            else:
                data['remark'] = 'F'
        else:
            data['remark'] = 'Na'

        lis_dic.append(data)

write_to_file(lis_dic)
print(f'Successfully wrote to {filename}')
