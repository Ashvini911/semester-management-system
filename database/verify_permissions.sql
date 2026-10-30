-- Run this file in MySQL Workbench as a MySQL administrator.
-- These statements are read-only and do not alter users, roles, or data.

-- 1. Confirm the application account and role accounts exist.
SELECT User, Host, plugin, account_locked, is_role
FROM mysql.user
WHERE (User = 'semester_app' AND Host = 'localhost')
   OR User IN ('r_auth', 'r_ar', 'r_hod', 'r_dean', 'r_clerk')
ORDER BY User, Host;

-- 2. Confirm that each role has been granted to the configured app account.
SELECT FROM_USER, FROM_HOST, TO_USER, TO_HOST, WITH_ADMIN_OPTION
FROM mysql.role_edges
WHERE TO_USER = 'semester_app' AND TO_HOST = 'localhost'
ORDER BY FROM_USER;

-- 3. Confirm that r_auth is the app account's default role.
SELECT USER, HOST, DEFAULT_ROLE_USER, DEFAULT_ROLE_HOST
FROM mysql.default_roles
WHERE USER = 'semester_app' AND HOST = 'localhost';

-- 4. Inspect the account's direct grants and database-level privileges.
SHOW GRANTS FOR 'semester_app'@'localhost';

SELECT GRANTEE, TABLE_SCHEMA, TABLE_NAME, PRIVILEGE_TYPE
FROM information_schema.TABLE_PRIVILEGES
WHERE TABLE_SCHEMA = 'semester_mgt'
  AND GRANTEE IN (
      '''semester_app''@''localhost''',
      '''r_auth''@''%''',
      '''r_ar''@''%''',
      '''r_hod''@''%''',
      '''r_dean''@''%''',
      '''r_clerk''@''%'''
  )
ORDER BY GRANTEE, TABLE_NAME, PRIVILEGE_TYPE;

-- 5. Inspect effective privileges with each assigned role applied.
SHOW GRANTS FOR 'semester_app'@'localhost' USING 'r_auth'@'%';
SHOW GRANTS FOR 'semester_app'@'localhost' USING 'r_ar'@'%';
SHOW GRANTS FOR 'semester_app'@'localhost' USING 'r_hod'@'%';
SHOW GRANTS FOR 'semester_app'@'localhost' USING 'r_dean'@'%';
SHOW GRANTS FOR 'semester_app'@'localhost' USING 'r_clerk'@'%';

-- Expected: r_auth has SELECT and column-limited UPDATE on USERS only;
-- business-role grants are scoped as documented in roles.sql.
