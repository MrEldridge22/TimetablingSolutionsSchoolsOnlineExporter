import json
import pandas as pd
from pathlib import Path
import sys
import config


# Year Creation and Open File
year = config.datetime.date.today().year

""" File Paths """
# School
filePath              = f"V:\\Timetabler\\Current Timetable\\{year}"

# Laptop OneDrive
main_path_laptop      = f"C:\\Users\\deldridge\\OneDrive - Department for Education\\Documents\\Timetabling\\{year}"

# Desktop OneDrive
main_path_desktop     = f"C:\\Users\\demg\\OneDrive - Department for Education\\Documents\\Timetabling\\{year}"

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
seniors_sfx_file    = f"\\{year} Year SeniorSchool Students.sfx"
swd_sfx_file        = f"\\{year} Year SWD Students.sfx"
semester1_tfx_file  = f"\\TTD_{year}_S1.tfx"
semester2_tfx_file  = f"\\TTD_{year}_S2.tfx"

# School Contact Number
schoolNumber = 245

# Core Group SACE Subjects
# These are SACE subjects NOT assigned to students within Student Options, rather in Timetable Development instead.
tfx_subjects = [
    "1EIF10", # Exploring Identities and Futures
    "1EIM10"
]

def update_codes(df):
    """
    Updates the 'School Class Code' and 'SACE Code' columns in the DataFrame when issues on import are found!

    Parameters:
    df (pd.DataFrame): The input DataFrame containing class information

    Returns:
    pd.DataFrame: The DataFrame with the updated 'School Class Code' and 'SACE Code' column.
    """
    # Changes due to ClassCode exceeding 10 characters
    df['School Class Code'] = df['School Class Code'].str.replace('ATAR', 'UNI')
    df['School Class Code'] = df['School Class Code'].str.replace('SHPA', 'SPT')
    df['School Class Code'] = df['School Class Code'].str.replace('NUM', 'N')
    df['School Class Code'] = df['School Class Code'].str.replace('VOC', 'V')
    df['School Class Code'] = df['School Class Code'].str.replace('JEW', 'J')
    df['School Class Code'] = df['School Class Code'].str.replace('DPA', 'PA')
    df['School Class Code'] = df['School Class Code'].str.replace('DPRD', 'DP')
    df['School Class Code'] = df['School Class Code'].str.replace('SpStA', 'SA')
    df['School Class Code'] = df['School Class Code'].str.replace('SpStB', 'SB')
    df['School Class Code'] = df['School Class Code'].str.replace('MMA', 'MA')
    df['School Class Code'] = df['School Class Code'].str.replace('MMB', 'MB')
    df['School Class Code'] = df['School Class Code'].str.replace('SMB', 'MB')
    df['School Class Code'] = df['School Class Code'].str.replace('UCA', 'UA')

    
    # Changes due to SACE Code incorrect
    df['SACE Code'] = df['SACE Code'].str.replace('CXM', 'CXA')
    df['School Class Code'] = df['School Class Code'].str.replace('CXM', 'CXA')
    
    df['SACE Code'] = df['SACE Code'].str.replace('FOG', 'FOH')
    df['School Class Code'] = df['School Class Code'].str.replace('FOG', 'FOH')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('SOM', 'SUA')
    df['School Class Code'] = df['School Class Code'].str.replace('2SOM', '2SUA')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('BVM', 'BVA')
    df['School Class Code'] = df['School Class Code'].str.replace('2BVM', '2BVA')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('CVM', 'CEA')
    df['School Class Code'] = df['School Class Code'].str.replace('2CVM', '2CEA')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('DTM', 'DTA')
    df['School Class Code'] = df['School Class Code'].str.replace('2DTM', '2DTA')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('HWM', 'HWA')
    df['School Class Code'] = df['School Class Code'].str.replace('2HWM', '2HWA')

    df.loc[df['Stage'] == 2, 'SACE Code'] = df.loc[df['Stage'] == 2, 'SACE Code'].str.replace('SFM', 'SFA')
    df['School Class Code'] = df['School Class Code'].str.replace('2SFM', '2SFA')
                                                                  
    df['SACE Code'] = df['SACE Code'].str.replace('PEM', 'PEA')
    df['School Class Code'] = df['School Class Code'].str.replace('PEM', 'PEA')

    df['SACE Code'] = df['SACE Code'].str.replace('PEM', 'PEA')
    df['School Class Code'] = df['School Class Code'].str.replace('PEM', 'PEA')



    return df


def update_teacher_code(df):
    """
    Updates the Teacher Code column in the DataFrame to be in a format we want.    

    Parameters:
    df (pd.DataFrame): The input DataFrame containing teacher information.

    Returns:
        pd.DataFrame: The DataFrame with the updated 'Teacher Code' column.
    """
    
    ### This makes the teacher code to be the first 7 characters of the Given Names and the first character of the Family Name. ###
    df["Teacher Code"] = df.apply(
        lambda row: (row["Given Names"][:min(7, len(row["Given Names"]))] + row["Family Name"][0]), axis=1
    )
    return df


def expand_studentPreferences_column(df):
    """
    Expands the 'StudentPreferences' column in the DataFrame, which contains dictionaries,
    into separate columns. Drops any rows where 'ClassID' is not assigned to the student.

    Parameters:
    df (pd.DataFrame): The input DataFrame with a 'StudentPreferences' column containing dictionaries.

    Returns:
    pd.DataFrame: The expanded DataFrame with separate columns for each key in the 'StudentPreferences' dictionaries.
    """
    # Expand the dictionary column row by row
    df = df.explode("StudentPreferences")
    expanded_df = df["StudentPreferences"].apply(pd.Series)
    
    # Concatenate the original dataframe (minus the dictionary column) with the expanded columns
    df_expanded = pd.concat([df.drop(columns=["StudentPreferences"]), expanded_df], axis=1)
    try:
        df_expanded.drop(columns=0, axis=1, inplace=True)
    except KeyError:
        print('0 Column can not be found, continuing!')

    # Drop all class options NOT assigned to the student.
    df_expanded = df_expanded[df_expanded["ClassID"].notna()]
    # df_expanded.drop(columns="ClassID", axis=1, inplace=True)

    df_expanded.drop(columns="OptionID", axis=1, inplace=True)
    
    return df_expanded


def generate_class_number(df):
    """
    Generates a Class Number for each unique ClassCode within groups defined by Stage, SACE Code, and Credits.

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns 'Stage', 'SACE Code', 'Credits', and 'ClassCode'.

    Returns:
    pd.DataFrame: The DataFrame with an additional 'Sequence' column containing the sequence numbers.
    """
    # Create a new column for the sequence
    df['Sequence'] = 0
    
    # Group by SubjectCode
    grouped = df.groupby(["Stage", "SACE Code", "Credits"])
    
    for name, group in grouped:
        # Create a dictionary to store the sequence for each ClassCode
        class_code_dict = {}
        sequence = 1
        
        for index, row in group.iterrows():
            class_code = row['ClassCode']
            if class_code not in class_code_dict:
                # print(class_code, sequence)
                class_code_dict[class_code] = sequence
                sequence += 1
            df.at[index, 'Sequence'] = class_code_dict[class_code]
    
    return df


def get_enrollments_dataframe(sfx_file, msswd="ms"):
    """
    Processes the Student Optionsd (.sfx) file to generate an enrollments DataFrame with necessary columns for Schools Online.

    Parameters:
    sfx_file (dict): The input JSON-like structure containing 'Lines', 'Classes', and 'Students'.
    msswd (str): String to ensure that SWD classes are resulted at the end of the year, defaults to ms for MainStream.

    Returns:
    pd.DataFrame: The processed DataFrame with the required columns for Schools Online Enrollments File.
    """
    ### Get Subjects and Classes ###
    # Get lines and puts into Dataframe
    lines_df = pd.json_normalize(sfx_file, record_path="Lines")
    for col in lines_df.columns:
        if col not in ["LineID", "Subgrid"]:
            lines_df.drop([col], inplace=True, axis=1)


    # Get Classes
    classes_df = pd.json_normalize(sfx_file, record_path="Classes")
    # Remove Unwanted Columns
    for col in classes_df.columns:
        if col not in ["ClassID", "LineID", "ClassCode", "SubjectCode", "SubjectName"]:
            classes_df.drop([col], inplace=True, axis=1)

    # Join classes and Lines
    classes_df = pd.merge(classes_df, lines_df, left_on="LineID", right_on="LineID", how="left").drop("LineID", axis=1)

    # Get Students and Choices into Dataframe
    students_df = pd.json_normalize(sfx_file, record_path="Students")
    
    # Remove Unwanted Columns
    for col in students_df.columns:
        if col not in ["StudentCode", "FirstName", "LastName", "BOSCode", "YearLevel", "StudentPreferences"]:
            students_df.drop([col], inplace=True, axis=1)

    # Expand Student Preferences Column
    students_df_expanded = expand_studentPreferences_column(students_df)
    
    # Merge Students with Classes
    organised_df = pd.merge(students_df_expanded, classes_df, left_on="ClassID", right_on="ClassID", how='left').drop("ClassID", axis=1)

    # Add in extra columns needed for Schools Online
    organised_df["Contact School Number"] = schoolNumber
    organised_df["Registration Number"] = organised_df["BOSCode"]
    organised_df["Student Code"] = organised_df["StudentCode"]
    organised_df["Year"] = datetime.date.today().year
    organised_df["Semester"] = organised_df["Subgrid"]
    organised_df["Stage"] = pd.to_numeric(organised_df["SubjectCode"].str.slice(stop=1), errors='coerce')
    organised_df["SACE Code"] = organised_df["SubjectCode"].str.slice(start=1, stop=4)
    organised_df["Credits"] = organised_df["SubjectCode"].str.slice(start=4, stop=6)
    organised_df["Enrolment Number"] = ""
    organised_df["Results Due"] = organised_df.apply(
        lambda row: (
            'D' if row['Credits'] == "20" else
            'D' if msswd == "swd" else
            'J' if row['Semester'] == 1 and row['Stage'] == 1 else  # Stage 1, Semester 1
            'D' if row['Semester'] == 2 and row['Stage'] == 1 else  # Stage 1, Semester 2
            'J' if row['SACE Code'] in ['RPA', 'RPM', 'AIF', 'AIM'] and row['Semester'] == 1 else  # Stage 2, Semester 1 for special codes
            'D' if row['SACE Code'] in ['RPA', 'RPM', 'AIF', 'AIM'] and row['Semester'] == 2 else  # Stage 2, Semester 2 for special codes
            'D'  # Default return for all other Stage 2 subjects
        ),
        axis=1
    )
    organised_df["Program Variant"] = ""
    organised_df["Teaching School Number"] = schoolNumber
    organised_df["Assessment School Number"] = schoolNumber
    organised_df["Class Number"] = generate_class_number(organised_df)["Sequence"]
    organised_df["Enrolment Status"] = "E"
    organised_df["Repeat Indicator"] = "N"
    organised_df["School Class Code"] = organised_df["ClassCode"]
    organised_df["Stage 1 Grade"] = ""
    organised_df["Partial Credits"] = ""
    organised_df["ED ID"] = organised_df["Student Code"]

    # Remove Other Columns
    organised_df.drop(["BOSCode", "SubjectName", "StudentCode", "FirstName", "LastName", "ClassCode", "Sequence", "SubjectCode", "Subgrid", "YearLevel"], axis=1, inplace=True)

    organised_df = update_codes(organised_df)

    return organised_df


def get_tfx_enrollments(tfx_file, semester, swd=False):
    """
    Gets the Exploring Identities and Futures Enrollments from the Timetable Development File and puts it into the required format for Schools Online
    
    Parameters:
    tfx_file (dict): The JSON Semester Timetable Development (tfx) file.

    Returns:
    pd.DataFrame: Dataframe containing all AIF Enrollment..
    """
    # Grab the JSON records from the tfx files
    class_names_df = pd.json_normalize(tfx_file, record_path="ClassNames")
    class_names_df.rename(columns={"Code": "ClassCode"}, inplace=True) # Rename to match student information
    timetable_df = pd.json_normalize(tfx_file, record_path="Timetable")
    teacher_df = pd.json_normalize(tfx_file, record_path="Teachers")
    students_df = pd.json_normalize(tfx_file, record_path="Students")
    
    # Expand out the student lessons JSON into columns, each students subjects are listed in JSON format under the StudentLessons field
    students_df = students_df.explode("StudentLessons")
    json_df = pd.json_normalize(students_df["StudentLessons"])
    # Combine back into the student dataframe
    students_df = pd.concat([students_df.drop(columns=["StudentLessons"]).reset_index(drop=True), json_df[["ClassCode"]]], axis=1)

    # Filter for SACE subjects
    students_df["ClassCode"] = students_df["ClassCode"].fillna("") # Remove NaN and replace with empty string
    pattern = '|'.join(tfx_subjects)
    students_df = students_df[students_df["ClassCode"].str.contains(pattern)]

    # Remove unwanted columns
    for col in students_df.columns:
        if col not in ["Code", "ClassCode", "BOSCode"]:
            students_df.drop(col, axis=1, inplace=True)
    
    # Merge Dataframes together to get required information for Schools Online    
    students_df = pd.merge(students_df, class_names_df[["ClassCode", "ClassNameID"]], on="ClassCode")
    students_df = pd.merge(students_df, timetable_df[["ClassNameID", "TeacherID"]], on="ClassNameID")
    students_df = pd.merge(students_df, teacher_df[["TeacherID", "Code"]], on="TeacherID")

    students_df.drop_duplicates(ignore_index=True, inplace=True)

    final_tfx_students = pd.DataFrame()
    final_tfx_students["Registration Number"] = students_df["BOSCode"]
    final_tfx_students["Student Code"] = students_df["Code_x"]
    final_tfx_students["Year"] = datetime.date.today().year
    final_tfx_students["Semester"] = semester
    final_tfx_students["Stage"] = pd.to_numeric(students_df["ClassCode"].str.slice(stop=1), errors='coerce')
    final_tfx_students["SACE Code"] = students_df["ClassCode"].str.slice(start=1, stop=4)
    final_tfx_students["Credits"] = students_df["ClassCode"].str.slice(start=4, stop=6)
    final_tfx_students["Enrolment Number"] = ""
    
    final_tfx_students["Program Variant"] = ""
    final_tfx_students["Teaching School Number"] = schoolNumber
    final_tfx_students["Assessment School Number"] = schoolNumber
    
    final_tfx_students["Enrolment Status"] = "E"
    final_tfx_students["Repeat Indicator"] = "N"
    final_tfx_students["ClassCode"] = students_df["ClassCode"]
    final_tfx_students["Stage 1 Grade"] = ""
    final_tfx_students["Partial Credits"] = ""
    final_tfx_students["ED ID"] = students_df["Code_x"]

       
    final_tfx_students.insert(0, "Contact School Number", schoolNumber)
    final_tfx_students.insert(8,
                              "Results Due",
                              final_tfx_students.apply(
                                lambda row: (
                                    'D' if "SWD" in row["ClassCode"] else
                                    'J' if row['Semester'] == 1 else  # Stage 1, Semester 1
                                    'D' if row['Semester'] == 2 else  # Stage 1, Semester 2
                                    'CHECK!'
                                ),
                                axis=1
                                )
    )
    final_tfx_students.insert(12, "Class Number", generate_class_number(final_tfx_students)["Sequence"])
    final_tfx_students.rename(columns={"ClassCode": "School Class Code"}, inplace=True)

    final_tfx_students.drop(columns=["Sequence"], axis=1, inplace=True)

    # Filter for SWD or Mainstream Enrollments
    if swd == True:
        final_tfx_students = final_tfx_students[final_tfx_students["School Class Code"].str.contains("SWD")]
    else:
        final_tfx_students = final_tfx_students[~final_tfx_students["School Class Code"].str.contains("SWD")]

    return final_tfx_students


def organise_teachers_df(df):
    """
    Organises the teachers DataFrame into the Format required by Schools Online.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing teacher information.

    Returns:
    pd.DataFrame: The organized DataFrame with the required columns.
    """
    for col in df.columns:
        if col not in ["LastName", "FirstName", "Code", "Salutation", "TeacherID"]:
            df.drop(columns=col, axis=1, inplace=True)
    
    organised_df = pd.DataFrame()

    organised_df["TeacherID"] = df["TeacherID"]
    organised_df["Contact School Number"] = schoolNumber
    organised_df["TeacherCode"] = df["Code"]
    organised_df["Family Name"] = df["LastName"]
    organised_df["Initials"] = df["FirstName"].str[0]
    organised_df["Title"] = df["Salutation"]
    organised_df["Type"] = "T"
    organised_df["Teachers Registration Number"] = ""
    organised_df["Email Address"] = ""
    organised_df["Given Names"] = df["FirstName"]
    organised_df["Date of Birth"] = ""
    organised_df["Gender"] = ""

    # print(organised_df)
    return organised_df
    

def get_teachers_dataframe(sem1_tfx, sem2_tfx):
    """
    Combines teacher data from two semesters, organises it, removes duplicates, and renames columns.

    Parameters:
    sem1_tfx (dict): The JSON Semester 1 Timetable Development (tfx) file.
    sem2_tfx (dict): The JSON Semester 2 Timetable Development (tfx) file.

    Returns:
    pd.DataFrame: The combined and organized DataFrame with teacher information.
    """
    sem1_teachers_df = pd.json_normalize(sem1_tfx, record_path="Teachers")
    sem2_teachers_df = pd.json_normalize(sem2_tfx, record_path="Teachers")

    teachers_df = pd.concat([organise_teachers_df(sem1_teachers_df), organise_teachers_df(sem2_teachers_df)])

    teachers_df = teachers_df.drop_duplicates()
    
    teachers_df.rename(columns={'TeacherCode': "Teacher Code"}, inplace=True)

    # print(teachers_df)

    return teachers_df


def organise_classes_dataframe(teacher_df, classes_tfx, semester, msswd="ms"):
    """
    Organises the classes DataFrame by merging teacher and class information, filtering, and adding necessary columns as required for the Classes Import File for Schools Online.

    Parameters:
    teacher_df (pd.DataFrame): DataFrame containing teacher information.
    classes_tfx (dict): The Timetable Development file (tfx)
    semester (int): The semester number.

    Returns:
    pd.DataFrame: The organised DataFrame with class information.
    """
    classes_df = pd.json_normalize(classes_tfx, record_path="ClassNames")
    timetable_df = pd.json_normalize(classes_tfx, record_path="Timetable")

    teachers_classes_df = pd.merge(teacher_df, timetable_df, how='left', on="TeacherID")
    teachers_class_details_df = pd.merge(teachers_classes_df, classes_df, how='left', on="ClassNameID")

    teachers_class_details_df.drop_duplicates(subset=["TeacherID", "ClassNameID"], inplace=True)
    teachers_class_details_df.dropna(subset=["SubjectCode"], inplace=True)
    
    # print(teachers_class_details_df)
    teachers_class_details_df = update_teacher_code(teachers_class_details_df)

    organised_classes_df = pd.DataFrame()
    
    organised_classes_df["Stage"] = teachers_class_details_df["SubjectCode"].str.slice(stop=1)
    organised_classes_df["SACE Code"] = teachers_class_details_df["SubjectCode"].str.slice(start=1, stop=4)
    organised_classes_df["Credits"] = teachers_class_details_df["SubjectCode"].str.slice(start=4, stop=6)
    organised_classes_df["Class Number"] = "" # Leave blank and match up by Code Afterwards
    organised_classes_df["Program Variant"] = ""
    organised_classes_df["Semester"] = semester
    organised_classes_df["Teacher Code"] = teachers_class_details_df["Teacher Code"]

    organised_classes_df["School Class Code"] = teachers_class_details_df["Code"]
    organised_classes_df["Results Due"] = organised_classes_df.apply(
        lambda row: (
            'D' if row['Credits'] == "20" else
            'D' if msswd == "swd" else
            'J' if row['Semester'] == 1 and row['Stage'] == "1" else  # Stage 1, Semester 1
            'D' if row['Semester'] == 2 and row['Stage'] == "1" else  # Stage 1, Semester 2
            'J' if row['SACE Code'] in ['RPA', 'RPM', 'AIF', 'AIM'] and row['Semester'] == 1 else  # Stage 2, Semester 1 for special codes
            'D' if row['SACE Code'] in ['RPA', 'RPM', 'AIF', 'AIM'] and row['Semester'] == 2 else  # Stage 2, Semester 2 for special codes
            'D'  # Default return for all other Stage 2 subjects
        ),
        axis=1
    )
    # Have to put these at the end as they are static values to be filled in
    organised_classes_df["Contact School Number"] = schoolNumber
    organised_classes_df["Year"] = datetime.date.today().year

    # Move the 2 to the front
    organised_classes_df.insert(0, "Contact School Number", organised_classes_df.pop("Contact School Number"))
    organised_classes_df.insert(1, "Year", organised_classes_df.pop("Year"))

    # Filter only Stage 1 and 2
    organised_classes_df = organised_classes_df[
        organised_classes_df["Stage"].isin(["1", "2"]) &
        (~organised_classes_df["School Class Code"].str.contains('Care', case=False))
    ]
    # print("Organised Classes")
    # print(organised_classes_df)
    organised_classes_df = update_codes(organised_classes_df)
    return organised_classes_df


def get_classes_dataframe(teachers_df, sem_tfx, semester, sace_enrollments_df, msswd="ms"):
    """
    Combines and organizes class data from teachers, semester information, and SACE enrollments.

    Parameters:
    teachers_df (pd.DataFrame): DataFrame containing teacher information.
    sem_tfx (dict): The Timetable Development file (tfx)
    semester (int): The semester number.
    sace_enrollments_df (pd.DataFrame): DataFrame containing SACE enrollment information.

    Returns:
    pd.DataFrame: The combined and organized DataFrame with class information.
    """
    df = organise_classes_dataframe(teachers_df, sem_tfx, semester, msswd)

    # Merge and handle column name conflicts
    df = pd.merge(df, sace_enrollments_df[["School Class Code", "Class Number"]], on="School Class Code", how='left', suffixes=('', '_y'))
    df["Class Number"] = df["Class Number_y"]
    df.drop(columns="Class Number_y", axis=1, inplace=True)

    df.drop_duplicates(subset=["Teacher Code", "School Class Code"], ignore_index=True, inplace=True)
    df.dropna(subset=["Class Number"], inplace=True) # This will sort for SWD and Mainstream
    # print('Get Classes Dataframe')
    # print(df)

    # Replace Part of Class Code

    df = update_codes(df)
    
    return df


def get_only_sace_teachers(teacher_df, classes_df):
    """
    Filters the teacher DataFrame to include only those who are teaching SACE classes.

    Parameters:
    teacher_df (pd.DataFrame): DataFrame containing teacher information.
    classes_df (pd.DataFrame): DataFrame containing class information, including 'Teacher Code' and 'Year'.

    Returns:
    pd.DataFrame: The filtered DataFrame containing only SACE teachers.
    """
    teacher_df = update_teacher_code(teacher_df)
    sace_teachers_df = pd.merge(teacher_df, classes_df[["Teacher Code", "Year"]], how='left', on="Teacher Code")
    sace_teachers_df.dropna(subset=["Year"], inplace=True)
    sace_teachers_df.drop(columns=["TeacherID", "Year"], axis=1, inplace=True)
    sace_teachers_df.drop_duplicates(ignore_index=True, inplace=True)

    return sace_teachers_df


def check_multiple_teachers(df):
    """
    Checks if there are any classes with multiple teachers.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing class information

    Returns:
    df (pd.DataFrame)
    """
    # Find duplicate School Class Codes and export to a csv.
    duplicates = df[df.duplicated(subset=["School Class Code"], keep=False)]
    if len(duplicates) > 0:
        return duplicates
    else:
        pass


def classes_file_output(df, semester, stage, swd=False):
    """
    Outputs the classes DataFrame to a CSV file and does some sanity checks along the way.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing class information.
    semester (int): The semester number.
    stage (int): The stage number.
    swd (bool): Boolean to indicate if the classes are for SWD students.

    Returns:
    None
    """

    # Code Length Check if School Class Code is greater than 10 characters
    good_codes = True
    for row in df.iterrows():
        if len(row[1]["School Class Code"]) > 10:
            print(f"Class Code: {row[1]['School Class Code']} is greater than 10 characters!")
            good_codes = False
    
    if good_codes:
        print("All Class Codes are good! Clear to Upload Classes File!")
    else:
        print("Please update class codes in update codes function before uploading!")
    
    # Output to CSV
    df = df[df["Stage"] == str(stage)]
    if stage == "1":
        if swd == True:
            df.to_csv(f'schools_online_import_files\\SWD_Stage{stage}_S{semester}_CLASSIMP.csv', index=False)
        else:
            df.to_csv(f'schools_online_import_files\\Stage{stage}_S{semester}_CLASSIMP.csv', index=False)
    else:
        if swd == True:
            df.to_csv(f'schools_online_import_files\\SWD_Stage{stage}_CLASSIMP.csv', index=False)
        else:
            df.to_csv(f'schools_online_import_files\\Stage{stage}_CLASSIMP.csv', index=False)


### CODE START ###

# Open Files
with open (f"{filePath}{semester1_tfx_file}", "r") as semester1_tfx_file:
    semester1_tfx = json.load(semester1_tfx_file)

with open (f"{filePath}{semester2_tfx_file}", "r") as semester2_tfx_file:
    semester2_tfx = json.load(semester2_tfx_file)

with open (f"{filePath}{seniors_sfx_file}", "r") as seniors_sfx_file:
    seniors_sfx = json.load(seniors_sfx_file)

with open (f"{filePath}{swd_sfx_file}", "r") as swd_sfx_file:
    swd_sfx = json.load(swd_sfx_file)

# Get Teachers Dataframe
teachers_df = get_teachers_dataframe(semester1_tfx, semester2_tfx)

# Get Enrollments Dataframes
seniors_df  = get_enrollments_dataframe(seniors_sfx)
swd_df      = get_enrollments_dataframe(swd_sfx, "swd")
semester1_tfx_enrollments = get_tfx_enrollments(semester1_tfx, 1) # Semester 1 tfx only classes
semester2_tfx_enrollments = get_tfx_enrollments(semester2_tfx, 2) # Semester 2 tfx only classes
seniors_df = pd.concat([seniors_df, semester1_tfx_enrollments, semester2_tfx_enrollments])

# Get Mainstream Classes
semester1_classes_import = get_classes_dataframe(teachers_df, semester1_tfx, 1, seniors_df)
semester2_classes_import = get_classes_dataframe(teachers_df, semester2_tfx, 2, seniors_df)

classes_import = pd.concat([semester1_classes_import, semester2_classes_import])
classes_import.drop_duplicates(subset=["Teacher Code", "School Class Code"], ignore_index=True, inplace=True)

# Get SWD Classes, have set both semesters to 1 as they generally run full year SACE subjects
semester1_swd_classes_import = get_classes_dataframe(teachers_df, semester1_tfx, 1, swd_df, "swd")
semester2_swd_classes_import = get_classes_dataframe(teachers_df, semester2_tfx, 2, swd_df, "swd")
swd_classes_import = pd.concat([semester1_swd_classes_import, semester2_swd_classes_import])
swd_classes_import.drop_duplicates(subset=["Teacher Code", "School Class Code"], ignore_index=True, inplace=True)

# Check for multiple teachers
duplicate_classes = check_multiple_teachers(pd.concat([classes_import, swd_classes_import]))
if duplicate_classes is not None:
    duplicate_classes.to_csv("schools_online_import_files\\Duplicate_Classes.csv", index=False)
    print("Duplicate Classes Found! Check Duplicate_Classes.csv for more information.")

# Get all classes for Teachers
all_classes = pd.concat([semester1_classes_import, semester2_classes_import, semester1_swd_classes_import, semester2_swd_classes_import])

### OUTPUT FILES ###
# Teachers
get_only_sace_teachers(teachers_df, all_classes).to_csv("schools_online_import_files\\TCHRIMP.csv", index=False)

# Classes
classes_file_output(classes_import[(classes_import["Semester"] == 1)], 1, "1")
classes_file_output(classes_import[(classes_import["Semester"] == 2)], 2, "1")
classes_file_output(classes_import, 1, "2")

classes_file_output(swd_classes_import, 1, "1", True)
classes_file_output(swd_classes_import, 2, "1", True)
classes_file_output(swd_classes_import, 1, "2", True)

# Enrollments
seniors_df[(seniors_df["Semester"] == 1) & (seniors_df["Stage"] == 1)].to_csv('schools_online_import_files\\Stage1_S1_ENRLIMP.csv', index=False)
seniors_df[(seniors_df["Semester"] == 2) & (seniors_df["Stage"] == 1)].to_csv('schools_online_import_files\\Stage1_S2_ENRLIMP.csv', index=False)

seniors_df[(seniors_df["Semester"] == 1) & (seniors_df["Stage"] == 2)].to_csv('schools_online_import_files\\Stage2_ENRLIMP.csv', index=False)

swd_df[(swd_df["Semester"] == 1) & (swd_df["Stage"] == 1)].to_csv('schools_online_import_files\\SWD_Stage1_ENRLIMP.csv', index=False)
swd_df[(swd_df["Semester"] == 1) & (swd_df["Stage"] == 2)].to_csv('schools_online_import_files\\SWD_Stage2_ENRLIMP.csv', index=False)

print("Done!")