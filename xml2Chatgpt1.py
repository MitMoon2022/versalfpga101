import openpyxl
import xml.etree.ElementTree as ET
import pandas as pd

# Load XML data
xml_data = """
<?xml version="1.0" ?>
<!-- Your XML data here -->
<BINSorterInstruction Company="Xilinx Asia Pacific" InstructionID="XLNX231222074340" Mode="3" RequestDate="22-DEC-23" Version="1.1">
    <!-- ... Rest of your XML ... -->
</BINSorterInstruction>
"""

# Parse XML
# Load the XML file
#tree = ET.parse('E4AQY370_list.xml')   #change the name of the .xml file accordingly
#root = ET.fromstring(xml_data)
#root = ET.parse("filename.xml").getroot()
root = ET.parse("E4AQY370_list.xml").getroot()

# Initialize lists to store data
LotID_List = []
SN_List = []
BINNo = []

# Function to extract SerialNo and Bin information
def extract_serial_and_bin(node):
    serial_no = node.find('SerialNo').text
    bin_id = node.find('Bin').text
    return serial_no, bin_id

#<LotID>E4AQY370</LotID>
#<FinalDest>X30BIN</FinalDest>
#<IsCloudBinning>TRUE</IsCloudBinning>
#<PartID>XCVN3716-VSVB2197</PartID>
#<PkgPin>VSVB2197</PkgPin>
#<Qty>127</Qty>
# Extract data from nested elements
lot_id = root.find('.//LotID').text
qty = root.find('.//Qty').text
part_id = root.find('.//PartID').text
pkg = root.find('.//PkgPin').text
print("lotid: ",lot_id)
print("qty: ",qty)
print("part_id:",part_id)
print("pkgPin:",pkg)

# Create a dictionary to store the extracted data
data_dict = {
    'LotID': lot_id,
    'Qty': qty,
    'PartID': part_id,
    'PkgPin': pkg
}

# Iterate through SortInfo nodes and extract data
for sort_info_node in root.findall('.//SortInfo/SNo'):
    LotID = root.find('.//LotID').text
    serial_no, bin_id = extract_serial_and_bin(sort_info_node)
    LotID_List.append(LotID)
    SN_List.append(serial_no)
    BINNo.append(bin_id)





# Create a DataFrame using Pandas
df = pd.DataFrame(list(zip(LotID_List, SN_List, BINNo)), columns=['LotID', 'SerialNumbers', 'Bin_no'])

# Convert the dictionary to a DataFrame
df_data = pd.DataFrame.from_dict(data_dict, orient='index', columns=['Value']).transpose()


# Print or do further processing with the DataFrame
#print(df)

#created filename
filename = 'default_2D.xlsx'

#Check le, use the <qty>
if lot_id and qty:
    filename = lot_id+"_"+qty+"org.xlsx"
    print(filename)

# Convert the DataFrame to an Excel file
#df.to_excel('Batch_2ID.xlsx', sheet_name=lot_id,index=False, engine='openpyxl')
df.to_excel(filename, sheet_name=lot_id,index=False, engine='openpyxl')
print("XML data has been converted to Excel successfully.")
