import json
import pandas as pd
import config


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


def get_enrollments(tfx_file, semester, swd=False):
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

    # Remove unwanted columns
    for col in students_df.columns:
        if col not in ["Code", "ClassCode", "BOSCode"]:
            students_df.drop(col, axis=1, inplace=True)
    
    # Merge Dataframes together to get required information for Schools Online    
    students_df = pd.merge(students_df, class_names_df[["ClassCode", "ClassNameID", "BOSClassCode1"]], on="ClassCode")
    students_df = pd.merge(students_df, timetable_df[["ClassNameID", "TeacherID"]], on="ClassNameID")
    students_df = pd.merge(students_df, teacher_df[["TeacherID", "Code"]], on="TeacherID")

    students_df.drop_duplicates(ignore_index=True, inplace=True)

    # Drop any students with no BOSClassCode1 - This should be all classes and students who are not studying SACE subjects.
    students_df.dropna(subset=["BOSClassCode1"], inplace=True)

    # Filter for SWD or Mainstream Enrollments
    if swd == True:
        students_df = students_df[students_df["BOSClassCode1"].str.contains("SWD")]
    else:
        students_df = students_df[~students_df["BOSClassCode1"].str.contains("SWD")]

    student_enrollments_df = pd.DataFrame()
    student_enrollments_df["Registration Number"] = students_df["BOSCode"]
    student_enrollments_df["Student Code"] = students_df["Code_x"]
    student_enrollments_df["Year"] = config.year
    student_enrollments_df["Semester"] = semester
    student_enrollments_df["Stage"] = pd.to_numeric(students_df["BOSClassCode1"].str.slice(stop=1), errors='coerce')
    student_enrollments_df["SACE Code"] = students_df["BOSClassCode1"].str.slice(start=1, stop=4)
    student_enrollments_df["Credits"] = students_df["BOSClassCode1"].str.slice(start=4, stop=6)
    student_enrollments_df["Enrolment Number"] = ""
    
    student_enrollments_df["Program Variant"] = ""
    student_enrollments_df["Teaching School Number"] = config.schoolNumber
    student_enrollments_df["Assessment School Number"] = config.schoolNumber
    
    student_enrollments_df["Enrolment Status"] = "E"
    student_enrollments_df["Repeat Indicator"] = "N"
    student_enrollments_df["ClassCode"] = students_df["ClassCode"]
    student_enrollments_df["Stage 1 Grade"] = ""
    student_enrollments_df["Partial Credits"] = ""
    student_enrollments_df["ED ID"] = students_df["Code_x"]


    student_enrollments_df.insert(0, "Contact School Number", config.schoolNumber)
    student_enrollments_df.insert(8,
                              "Results Due",
                              student_enrollments_df.apply(
                                lambda row: (
                                    'D' if "SWD" in row["ClassCode"] else
                                    'J' if row['Semester'] == 1 else  # Stage 1, Semester 1
                                    'D' if row['Semester'] == 2 else  # Stage 1, Semester 2
                                    'CHECK!'
                                ),
                                axis=1
                                )
    )
    student_enrollments_df.insert(12, "Class Number", generate_class_number(student_enrollments_df)["Sequence"])
    student_enrollments_df.rename(columns={"ClassCode": "School Class Code"}, inplace=True)

    student_enrollments_df.drop(columns=["Sequence"], axis=1, inplace=True)

    print(student_enrollments_df)

    return student_enrollments_df


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
    organised_df["Contact School Number"] = config.schoolNumber
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
    organised_classes_df["Contact School Number"] = config.schoolNumber
    organised_classes_df["Year"] = config.year

    # Move the 2 to the front
    organised_classes_df.insert(0, "Contact School Number", organised_classes_df.pop("Contact School Number"))
    organised_classes_df.insert(1, "Year", organised_classes_df.pop("Year"))

    # Filter only Stage 1 and 2
    organised_classes_df = organised_classes_df[
        organised_classes_df["Stage"].isin(["1", "2"]) &
        (~organised_classes_df["School Class Code"].str.contains('Care', case=False))
    ]

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
with open (f"{config.filePath}{config.semester1_tfx_file}", "r") as semester1_tfx_file:
    semester1_tfx = json.load(semester1_tfx_file)

with open (f"{config.filePath}{config.semester2_tfx_file}", "r") as semester2_tfx_file:
    semester2_tfx = json.load(semester2_tfx_file)

# Get Teachers Dataframe
teachers_df = get_teachers_dataframe(semester1_tfx, semester2_tfx)

# Get Enrollments Dataframes
semester1_tfx_enrollments = get_enrollments(semester1_tfx, 1) # Semester 1
semester2_tfx_enrollments = get_enrollments(semester2_tfx, 2) # Semester 2

# # Get Mainstream Classes
# semester1_classes_import = get_classes_dataframe(teachers_df, semester1_tfx, 1, seniors_df)
# semester2_classes_import = get_classes_dataframe(teachers_df, semester2_tfx, 2, seniors_df)

# classes_import = pd.concat([semester1_classes_import, semester2_classes_import])
# classes_import.drop_duplicates(subset=["Teacher Code", "School Class Code"], ignore_index=True, inplace=True)

# # Get SWD Classes, have set both semesters to 1 as they generally run full year SACE subjects
# semester1_swd_classes_import = get_classes_dataframe(teachers_df, semester1_tfx, 1, swd_df, "swd")
# semester2_swd_classes_import = get_classes_dataframe(teachers_df, semester2_tfx, 2, swd_df, "swd")
# swd_classes_import = pd.concat([semester1_swd_classes_import, semester2_swd_classes_import])
# swd_classes_import.drop_duplicates(subset=["Teacher Code", "School Class Code"], ignore_index=True, inplace=True)

# # Check for multiple teachers
# duplicate_classes = check_multiple_teachers(pd.concat([classes_import, swd_classes_import]))
# if duplicate_classes is not None:
#     duplicate_classes.to_csv("schools_online_import_files\\Duplicate_Classes.csv", index=False)
#     print("Duplicate Classes Found! Check Duplicate_Classes.csv for more information.")

# # Get all classes for Teachers
# all_classes = pd.concat([semester1_classes_import, semester2_classes_import, semester1_swd_classes_import, semester2_swd_classes_import])

# ### OUTPUT FILES ###
# # Teachers
# get_only_sace_teachers(teachers_df, all_classes).to_csv("schools_online_import_files\\TCHRIMP.csv", index=False)

# # Classes
# classes_file_output(classes_import[(classes_import["Semester"] == 1)], 1, "1")
# classes_file_output(classes_import[(classes_import["Semester"] == 2)], 2, "1")
# classes_file_output(classes_import, 1, "2")

# classes_file_output(swd_classes_import, 1, "1", True)
# classes_file_output(swd_classes_import, 2, "1", True)
# classes_file_output(swd_classes_import, 1, "2", True)

# # Enrollments
# seniors_df[(seniors_df["Semester"] == 1) & (seniors_df["Stage"] == 1)].to_csv('schools_online_import_files\\Stage1_S1_ENRLIMP.csv', index=False)
# seniors_df[(seniors_df["Semester"] == 2) & (seniors_df["Stage"] == 1)].to_csv('schools_online_import_files\\Stage1_S2_ENRLIMP.csv', index=False)

# seniors_df[(seniors_df["Semester"] == 1) & (seniors_df["Stage"] == 2)].to_csv('schools_online_import_files\\Stage2_ENRLIMP.csv', index=False)

# swd_df[(swd_df["Semester"] == 1) & (swd_df["Stage"] == 1)].to_csv('schools_online_import_files\\SWD_Stage1_ENRLIMP.csv', index=False)
# swd_df[(swd_df["Semester"] == 1) & (swd_df["Stage"] == 2)].to_csv('schools_online_import_files\\SWD_Stage2_ENRLIMP.csv', index=False)

print("Done!")