import os
import datetime
import pandas as pd

def get_file_creation_time(file_path):
    data=[]
    timestamp = os.path.getctime(file_path)
    time= datetime.datetime.fromtimestamp(timestamp)
    data.append(time)
    df_new = pd.DataFrame(data, columns = ['Create Time'])
    return df_new

def get_file_modified_time(file_path):
    data=[]
    timestamp = os.path.getmtime(file_path)
    time= datetime.datetime.fromtimestamp(timestamp)
    data.append(time)
    df_new = pd.DataFrame(data, columns = ['Modified Time'])
    return df_new

def read_txt_files_info(path,desired_word):
    l1=[]
    for entry in os.scandir(path):
        if entry.is_dir() and desired_word in entry.name:
            folder_path = os.path.join(path, entry.name)
            txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]

            for file in txt_files:
                file_path = os.path.join(folder_path, file)
                creation_time = get_file_creation_time(file_path)
                modified_time = get_file_modified_time(file_path)
                file_name = file.split('.txt')[0].split('_')[:8]
                sn = file_name[0]
                type = file_name[7]
                #print(sn,type)
                df = pd.DataFrame([[sn, type]], columns=['SN','Read Type'])
                df_concat = pd.concat([df, creation_time,modified_time], axis = 1)
                l1.append(df_concat)
                
                pd.concat(l1).to_excel(path + 'TestTime.xlsx',index=False,sheet_name= 'Test Time') 
                
                
                




# Specify the folder path
folder_path = r'Z:\Robot-SLT\XAP\SLT-01\Project\Versal\A3697\ES2\Data\Margin\\'
desired_word = 'Prod'
# Call the function to read the .txt file information
read_txt_files_info(folder_path,desired_word)