# TimetablingSolutionsSchoolsOnlineExporter
Export SACE Schools Online Files from Timetabling Solutions Timetable Product

Edit your school data and file paths and names to the Timetable files in the config.py script.

Hints and Tips:
Your Class Codes need to be a MAXIMUM of 10 characters Long, any longer than this and the import will fail.
Staff Codes are a maximum of 10 charaters. This script is set up to create staff codes as the first name followed by the first  initial of their last name. There is a limit of 8 characters for Schools Online Teacher information so the first name is striped down to 7 characters. 
For example:
Joe Blogs has the teacher code JoeB
Jonathan Foobar has the teacher code JonathaF
NOTE: If a Teacher has a special character in their first name this will create an issue on uploading, a check will be added into the script at a later date.

This script DOES NOT create the student details upload file as addresses are not stored within Timetabling Solutions, these will need to come from your main Educational Management System (EDSAS / EMS for Department for Education in South Australia)

Timetable Files Requirements
Student Options Files must have Students SACE ID's in the BOS Code Column in task 2A - Student Details
Student Option Files must have SACE Codes in the BOS Code column in task 3A - Option Names

As my site also has a Disability Unit attached and these are also timetabled with our timetable files, these classes have an extra SWD added onto the BOS Code, this helps split out the SWD files for seperate upload.

The Duplicate_Classes.csv file is an output where the script has identified 2 or more classes sharing the same class code. A potential cause of this would be if a class was being team taught by 2 teachers under the one code or if a class had a permanent relief as set in the Edit Timetable task.