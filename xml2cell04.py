# pip install pandas openpyxl     ;required pandas and openpyxl 
import xml.etree.ElementTree as ET
import pandas as pd

# Load the XML file
tree = ET.parse('4ANR792_2d.xml')   #change the name of the .xml file
root = tree.getroot()
#print(root)
# Define a list to store the data
LotID_List = []
SN_List =[]

# Extract attributes from the SerialInstruction element
request_date = root.get('RequestDate')
print(request_date)
#instruction_id = root.find('SerialInstruction').get('InstructionID')
#company = root.find('SerialInstruction').get('Company')

# Extract data from nested elements
lot_id = root.find('.//LotID').text
qty = root.find('.//Qty').text

print("lotid: ",lot_id)
print("qty: ",qty)

serialInfo_count = root.find('.//SerialInfo').get('count')
print(serialInfo_count)

# Iterate through the XML and extract data
for item in root.iter('SNo'):
    #print(item)
    nameID = item.get('ID')
    #print(nameID)
    LotID_List.append(nameID)

for SN in root.iter('SerialNo'):
    #print(SN.text)
    SN_List.append(SN.text)

# Create a Pandas DataFrame from the extracted data
#df = pd.DataFrame(SN_List, columns=['SerialNo'])

# Create a Pandas DataFrame from the extracted data
df = pd.DataFrame({'LotID': LotID_List,'SerialNumbers': SN_List})

#created filename
filename = 'default_2D.xlsx'

#if lot_id and serialInfo_count:
#    filename = lot_id+"_"+serialInfo_count+".xlsx"
#    print(filename)

#Check le, use the <qty>
if lot_id and qty:
    filename = lot_id+"_"+qty+".xlsx"
    print(filename)
# Convert the DataFrame to an Excel file
#df.to_excel('Batch_2ID.xlsx', sheet_name=lot_id,index=False, engine='openpyxl')
df.to_excel(filename, sheet_name=lot_id,index=False, engine='openpyxl')
print("XML data has been converted to Excel successfully.")
