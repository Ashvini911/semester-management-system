USE semester_mgt;

CREATE ROLE IF NOT EXISTS 'r_auth'@'%';
CREATE ROLE IF NOT EXISTS 'r_ar'@'%';
CREATE ROLE IF NOT EXISTS 'r_hod'@'%';
CREATE ROLE IF NOT EXISTS 'r_dean'@'%';
CREATE ROLE IF NOT EXISTS 'r_clerk'@'%';

GRANT SELECT ON semester_mgt.USERS TO 'r_auth'@'%';
GRANT UPDATE (Password_Hash) ON semester_mgt.USERS TO 'r_auth'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE ON semester_mgt.SEMESTER TO 'r_ar'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON semester_mgt.COURSE TO 'r_ar'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON semester_mgt.TIME_TABLE TO 'r_ar'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON semester_mgt.EXAM TO 'r_ar'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON semester_mgt.LECTURE TO 'r_ar'@'%';
GRANT SELECT ON semester_mgt.ACADEMIC_STAFF_MEMBER TO 'r_ar'@'%';
GRANT SELECT ON semester_mgt.VENUE TO 'r_ar'@'%';
GRANT SELECT ON semester_mgt.MODERATOR TO 'r_ar'@'%';

GRANT SELECT, UPDATE ON semester_mgt.DEPARTMENT TO 'r_hod'@'%';
GRANT SELECT, UPDATE ON semester_mgt.DEGREE TO 'r_hod'@'%';
GRANT SELECT ON semester_mgt.HOD TO 'r_hod'@'%';

REVOKE SELECT ON semester_mgt.* FROM 'r_dean'@'%';
GRANT SELECT ON semester_mgt.DEPARTMENT TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.DEGREE TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.SEMESTER TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.TIME_TABLE TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.COURSE TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.ACADEMIC_STAFF_MEMBER TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.VENUE TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.MODERATOR TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.SECOND_EXAMINER TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.LECTURE TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.EXAM TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.DEMONSTRATOR TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.REQUIREMENT TO 'r_dean'@'%';
GRANT SELECT ON semester_mgt.DEMONSTRATOR_REQUIREMENT TO 'r_dean'@'%';

GRANT SELECT, INSERT ON semester_mgt.LECTURE TO 'r_clerk'@'%';
GRANT SELECT, INSERT ON semester_mgt.EXAM TO 'r_clerk'@'%';
GRANT SELECT ON semester_mgt.VENUE TO 'r_clerk'@'%';
GRANT SELECT ON semester_mgt.COURSE TO 'r_clerk'@'%';
GRANT SELECT ON semester_mgt.SEMESTER TO 'r_clerk'@'%';
GRANT SELECT ON semester_mgt.ACADEMIC_STAFF_MEMBER TO 'r_clerk'@'%';
GRANT SELECT ON semester_mgt.MODERATOR TO 'r_clerk'@'%';

-- Create semester_app with a strong secret out of band, then grant these roles.
GRANT 'r_auth'@'%', 'r_ar'@'%', 'r_hod'@'%', 'r_dean'@'%', 'r_clerk'@'%'
TO 'semester_app'@'localhost';

-- Keep authentication available by default for CLI password operations.
-- The Flask connection code selects exactly one role before issuing USE.
SET DEFAULT ROLE 'r_auth'@'%' TO 'semester_app'@'localhost';
