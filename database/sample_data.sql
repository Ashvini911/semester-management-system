USE semester_mgt;

-- Set each account password after loading this file with:
-- flask --app run.py set-password <email>
INSERT INTO USERS
    (Email, First_Name, Last_Name, Username, Password_Hash, Role)
VALUES
    ('ar@example.com', 'Amali', 'Perera', 'amali_ar', 'RESET_WITH_FLASK_CLI', 'AR_OFFICER'),
    ('hod@example.com', 'Kamal', 'Silva', 'kamal_hod', 'RESET_WITH_FLASK_CLI', 'HOD'),
    ('dean@example.com', 'Nimal', 'Fernando', 'nimal_dean', 'RESET_WITH_FLASK_CLI', 'DEAN'),
    ('clerk@example.com', 'Saman', 'Kumara', 'saman_clerk', 'RESET_WITH_FLASK_CLI', 'CLERK');

INSERT INTO AR_OFFICER (Email) VALUES ('ar@example.com');
INSERT INTO HOD (Email) VALUES ('hod@example.com');
INSERT INTO DEAN (Email) VALUES ('dean@example.com');
INSERT INTO CLERK (Email) VALUES ('clerk@example.com');

INSERT INTO DEPARTMENT (Dep_Name, Email)
VALUES ('Computing', 'hod@example.com');

INSERT INTO DEGREE (Degree_Name, Credit, Duration, Dep_Name)
VALUES ('BSc Information Technology', 120, 4, 'Computing');

INSERT INTO SEMESTER (Semester_ID, Academic_Year, Start_Date, End_Date)
VALUES
    ('SEM1', '2026/2027', '2026-07-13', '2026-12-31'),
    ('SEM2', '2026/2027', '2027-01-15', '2027-06-30');

INSERT INTO TIME_TABLE (Timetable_ID, Semester_ID, `Year`, Place)
VALUES
    (1, 'SEM1', '2026/2027', 'Computing'),
    (2, 'SEM2', '2026/2027', 'Computing');

INSERT INTO COURSE (Course_Code, Course_Name, Credit, Semester_ID)
VALUES
    ('ICT1306', 'Object Oriented Programming', 2, 'SEM1'),
    ('ICT1402', 'Principles of Programming', 1, 'SEM2'),
    ('ICT1407', 'Database Systems', 1, 'SEM1');

INSERT INTO ACADEMIC_STAFF_MEMBER
    (Staff_ID, First_Name, Last_Name, Email, Contact_No, Staff_Type, Employment, Timetable_ID)
VALUES
    ('ST001', 'Nuwan', 'Perera', 'nuwan@example.com', '0711234567', 'LECTURER', 'PERMANENT', 1),
    ('ST002', 'Kumari', 'Silva', 'kumari@example.com', '0771234567', 'INTERNAL', 'PERMANENT', 2);

INSERT INTO VENUE (Venue_No, Venue_Name, Capacity, Floor, Building, Venue_Type)
VALUES
    ('V001', 'Main Lecture Hall', 120, 1, 'Main Block', 'LECTURE_HALL'),
    ('V002', 'Computing Lab', 40, 2, 'Technology Block', 'LAB');

INSERT INTO MODERATOR
    (Email, First_Name, Last_Name, Contact_No, Official_Address, Designation)
VALUES
    ('mod@example.com', 'Anusha', 'Perera', '0719876543', 'Anuradhapura', 'Senior Lecturer');

INSERT INTO SECOND_EXAMINER (Email, Moderator_Email)
VALUES ('examiner@example.com', 'mod@example.com');

INSERT INTO LECTURE
    (Course_Code, Staff_ID, Venue_No, Moderator_Email, `Date`, `Time`, Mode)
VALUES
    ('ICT1407', 'ST001', 'V001', 'mod@example.com', '2026-08-10', '09:00:00', 'Physical'),
    ('ICT1306', 'ST002', 'V002', 'mod@example.com', '2026-08-11', '10:00:00', 'Physical');

INSERT INTO EXAM (Semester_ID, Course_Code, `Type`, `Date`, `Time`)
VALUES
    ('SEM1', 'ICT1407', 'Midterm', '2026-09-10', '09:00:00'),
    ('SEM1', 'ICT1306', 'Final', '2026-12-10', '09:00:00');

INSERT INTO DEMONSTRATOR (First_Name, Last_Name, Email, Contact_No)
VALUES
    ('Kasun', 'Perera', 'kasun@example.com', '0714567890'),
    ('Nadeesha', 'Silva', 'nadeesha@example.com', '0774567890');

INSERT INTO REQUIREMENT (Requirement_Name, Description)
VALUES
    ('Computer Skills', 'Basic computer knowledge required'),
    ('Programming Skills', 'Basic programming knowledge required');

INSERT INTO DEMONSTRATOR_REQUIREMENT (Demonstrator_ID, Requirement_ID)
VALUES (1, 1), (2, 2);
