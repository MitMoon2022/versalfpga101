import os
import pandas as pd

def main (path):
    l1=[]
#sort out useful info from txt name
#check_Fmax to check for last passing freq
    for files in os.listdir(path):
        if files.endswith('read.txt'):
            work_file = os.path.join(path, files)
            Fmax = check_Fmax (work_file)
            file_name = files.split('_')[:4]
            df = pd.DataFrame([file_name], columns=['SN','Voltage','Temperature','Site'])
            df_concat = pd.concat([df, Fmax], axis = 1)
            l1.append(df_concat)
             
            pd.concat(l1).to_excel(path + '_Fmax.xlsx',index=False,sheet_name= 'Fmax Result') 
        
def check_Fmax (path):
    files = path
    data=[]
    with open(files, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if i % 2 == 1:  # select the result row 
                words = line.split()
                if words[6] == 'PASS':  #check TG pass/fail
                    Fmax = words[0] #record last passing Freq
    data.append(Fmax)
    df_new = pd.DataFrame(data, columns = ['Fmax'])
                  
    return df_new

def summary(directory, desired_word):
    combined_csv = pd.DataFrame()
    for csv in os.listdir(directory):
        if csv.endswith("_Fmax.xlsx") and desired_word in csv:
            csv_path = os.path.join(directory, csv)
            
            df = pd.read_excel(csv_path)
            combined_csv = pd.concat([combined_csv, df])
    
    combined_csv.to_excel(directory+'FmaxSummary.xlsx', index=False)
    
def process_folders(path, desired_word):
    for entry in os.scandir(path):
        if entry.is_dir() and desired_word in entry.name:
            folder_path = os.path.join(path, entry.name)
            main(folder_path)
            
#directory = r'C:\Users\davionc\Documents\project\HBM\ES2\VST\Fmax\\' 
directory = r'Y:\Robot-SLT\XAP\SLT-01\Project\Versal\A3697\ES2\Data\Fmax\\'
desired_word = 'Prod'

process_folders(directory, desired_word)
summary(directory,desired_word)