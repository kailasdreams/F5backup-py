#---------------------------------------------------------------------------------------------------------------------#



print (''' Code Written by kailas and  Strictly Data loss or any other damage Coder is not responsible.  ''' )



import os
import requests
import pandas as pd
import base64
import urllib3
from os.path import expanduser
from datetime import datetime

# Disable SSL warnings (for development use only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Excel file path
excel_file = 'C:/Users/OM-SAI/Desktop/New folder/f5_device_credentials.xlsx'  ### Define the File hostame path 5_device_credentials.xlsx

# Read Excel sheet into a DataFrame
df = pd.read_excel(excel_file)

# Backup directory
backup_dir = expanduser("~") + '/backups/f5_configs/'

# Ensure backup directory exists

if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# Function to create a backup for each F5 device
def backup_f5_device(f5_hostname, api_user, api_password):
    f5_url = f'https://{f5_hostname}/mgmt/tm/sys/ucs'
    ucs_file = f'F5_{f5_hostname +"_"+ datetime.now().strftime("%Y%m%d_%H%M%S") }.ucs'
    payload = {'command': 'save', 'name': ucs_file}
    
    # Base64 encode credentials for Basic Auth
    auth_string = base64.b64encode(f"{api_user}:{api_password}".encode()).decode()
    
    # Headers for the REST API request
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json'
    }
    
    # Send POST request to trigger UCS backup on F5 device
    response = requests.post(f5_url, json=payload, headers=headers, verify=False)
    
    if response.status_code == 200:
        print(f"Backup created successfully: {ucs_file} on {f5_hostname}")
        
        # Now download the UCS backup file
        download_url = f'https://{f5_hostname}/mgmt/shared/file-transfer/ucs-downloads/{ucs_file}'
        
        # Send GET request to download the file
        download_response = requests.get(download_url, headers=headers, stream=True, verify=False)
        
        # Handle Partial Content (206) and successful responses
        if download_response.status_code in [200, 206]:
            backup_file_path = os.path.join(backup_dir, ucs_file)
            with open(backup_file_path, 'wb') as f:
                for chunk in download_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(f"Backup downloaded successfully to {backup_file_path}")
        else:
            print(f"Failed to download UCS backup for {f5_hostname}. HTTP Status: {download_response.status_code}")
    else:
        print(f"Failed to create UCS backup for {f5_hostname}. HTTP Status: {response.status_code}")

# Loop through each row in the Excel file and perform backup
for index, row in df.iterrows():
    f5_hostname = row['F5 Hostname']
    api_user = row['Username']
    api_password = row['Password']
    
    # Perform backup for the current F5 device
    backup_f5_device(f5_hostname, api_user, api_password)




#---------------------------------------------------------------------------------------------------------------------#


