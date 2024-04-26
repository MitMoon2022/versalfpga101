import os
import pandas as pd
import numpy as np

def process_folders(path, desired_word):
    for entry in os.scandir(path):
        if entry.is_dir() and desired_word in entry.name:
            folder_path = os.path.join(path, entry.name)
            check_writemargin(folder_path)
            check_readmargin(folder_path)
            
def check_writemargin(folder_path):
    l1 =[]
    for files in os.listdir(folder_path):
            if files.endswith('wm_result.txt'):
                work_file = os.path.join(folder_path, files)
                writemargin = sort_result(work_file, 'WM')
                file_name = files.split('_')[:1]
                df = pd.DataFrame([file_name,file_name], columns=['SN'])
                df_concat = pd.concat([df, writemargin], axis = 1)
                l1.append(df_concat)
                
                pd.concat(l1).to_excel(folder_path + '_WMsummary.xlsx',index=False,sheet_name= 'WM Result')
                
def check_readmargin(folder_path):
    l1 =[]
    for files in os.listdir(folder_path):
            if files.endswith('rm_result.txt'):
                work_file = os.path.join(folder_path, files)
                readmargin = sort_result(work_file, 'RM')
                file_name = files.split('_')[:1]
                df = pd.DataFrame([file_name, file_name, file_name, file_name], columns=['SN'])
                df_DQ = pd.DataFrame(['DQS_T', 'DQS_T', 'DQS_C', 'DQS_C'], columns=['DQ'])
                df_DW = pd.DataFrame(['DW 02', 'DW 13', 'DW 02', 'DW 13'], columns=['DW'])
                df_concat = pd.concat([df, df_DQ, df_DW, readmargin], axis = 1)
                l1.append(df_concat)
                
                pd.concat(l1).to_excel(folder_path + '_RMsummary.xlsx',index=False,sheet_name= 'RM Result')

def sort_result(directory, case):
    data = []
    
    if case == 'WM':
        with open(directory, 'r') as file:
            lines = file.readlines()
            max_count = 33
            for j in range (1, max_count,1):
                for i in range(2, 9, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(5, 12, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(14, 21, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(17, 24, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
             
            reshaped_data = np.reshape(data, (4, 32))
            df = np.zeros((2,64))
            df[0, :32] = reshaped_data[0, :32]
            df[0, 32:] = reshaped_data[2, :32]
            df[1, :32] = reshaped_data[1, :32]
            df[1, 32:] = reshaped_data[3, :32]
            df = np.insert(df, 32, np.nan,axis=1)
            df_sorted = pd.DataFrame(df, columns= ['PC0','PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','PC11','PC12','PC13','PC14','PC15','PC16','PC17','PC18','PC19','PC20','PC21','PC22','PC23','PC24','PC25','PC26','PC27','PC28','PC29','PC30','PC31','','PC0','PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','PC11','PC12','PC13','PC14','PC15','PC16','PC17','PC18','PC19','PC20','PC21','PC22','PC23','PC24','PC25','PC26','PC27','PC28','PC29','PC30','PC31'])

    if case == 'RM':
        with open(directory, 'r') as file:
            lines = file.readlines()
            max_count = 33
            ##sort out left read margin
            for j in range (1, max_count,1):
                for i in range(2, 9, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(5, 12, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(14, 21, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(17, 24, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
            
            ##sort out right read margin
            for j in range (1, max_count,1):
                for i in range(26, 33, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(29, 36, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(38, 45, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
        
            for j in range (1, max_count,1):
                for i in range(41, 48, 6):
                    row = lines[i].strip().split(',')
                    word = row[j].strip()
                    if word != '0.0' :
                        data.append(word)
            
            reshaped_data = np.reshape(data, (8, 32))             
            df = np.zeros((4,64))
            df[0, :32] = reshaped_data[0, :32]
            df[0, 32:] = reshaped_data[4, :32]
            df[1, :32] = reshaped_data[1, :32]
            df[1, 32:] = reshaped_data[5, :32]
            df[2, :32] = reshaped_data[2, :32]
            df[2, 32:] = reshaped_data[6, :32]
            df[3, :32] = reshaped_data[3, :32]
            df[3, 32:] = reshaped_data[7, :32]
            df = np.insert(df, 32, np.nan,axis=1)
            df_sorted = pd.DataFrame(df, columns= ['PC0','PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','PC11','PC12','PC13','PC14','PC15','PC16','PC17','PC18','PC19','PC20','PC21','PC22','PC23','PC24','PC25','PC26','PC27','PC28','PC29','PC30','PC31','','PC0','PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','PC11','PC12','PC13','PC14','PC15','PC16','PC17','PC18','PC19','PC20','PC21','PC22','PC23','PC24','PC25','PC26','PC27','PC28','PC29','PC30','PC31'])
      
    return df_sorted

def summary(directory, desired_word):
    combined_csv = pd.DataFrame()
    for csv in os.listdir(directory):
        if csv.endswith("summary.xlsx") and desired_word in csv:
            csv_path = os.path.join(directory, csv)
            
            df = pd.read_excel(csv_path)
            combined_csv = pd.concat([combined_csv, df])
    
    combined_csv.to_excel(directory+desired_word+'Summary.xlsx', index=False, sheet_name= desired_word+" Summary")

##user define input
directory = r'Z:\Robot-SLT\XAP\SLT-01\Project\Versal\A3697\ES2\Data\Margin\\' 
desired_word = 'Prod'
##script start process    
process_folders(directory, desired_word)
summary(directory,'RM')
summary(directory,'WM')