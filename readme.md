# Semester Management System (Flask + MySQL)
Every page is one folder holding its own .py, .html and .css (e.g. pages/login/login.py, login.html, login.css).
Shared: app.py, common.py, templates/base.html, static/css/base.css
1. Run `semestermgt file.sql` in MySQL.   2. `pip install -r requirements.txt`
3. Optional env: DB_HOST DB_USER DB_PASS DB_NAME SECRET_KEY
4. `python app.py seed` (password `Demo@12345678` for sample users)   5. `python app.py` -> http://127.0.0.1:5000
