import datetime
from pathlib import Path
import sys

### Configuration File ###
# This file contains the configuration for the script, including file paths and other settings related to your school

# Year Creation and Open File
year = datetime.date.today().year

# School Contact Number
schoolNumber = xxx

""" File Paths """
# School
filePath              = f"V:\\Timetabler\\Current Timetable\\{year}"

# Laptop OneDrive
main_path_laptop      = f"C:\\Users\\xxx\\OneDrive - Department for Education\\Documents\\Timetabling\\{year}"

# Desktop OneDrive
main_path_desktop     = f"C:\\Users\\xxx\\OneDrive - Department for Education\\Documents\\Timetabling\\{year}"

# Check if the path exists and set the file path, make it easier to switch between locations.
try:
    if Path(filePath).exists():
        filePath = filePath
        
    elif Path(main_path_laptop).exists():
        filePath = main_path_laptop
    
    elif Path(main_path_desktop).exists():
        filePath = main_path_desktop

    print(f"Using the following Timetabling Location: {filePath}")

except: 
    print("Timetabling Folder Can Not Be Found!")
    sys.exit(1)

# Output Folder, if it exists, pass, else create it.
if Path("schools_online_import_files").exists():
    pass
else:  
    Path("schools_online_import_files").mkdir()

# Semester & Term file names
semester1_tfx_file  = f"\\TTD_{year}_S1.tfx"
semester2_tfx_file  = f"\\TTD_{year}_S2.tfx"

