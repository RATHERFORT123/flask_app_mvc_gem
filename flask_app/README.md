# Flask MVC User/Admin App

## Quick Start (SQLite)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=run.py  # Windows: set FLASK_APP=run.py
python run.py
```
Login as admin: `admin@example.com` / `admin123`

## Using MySQL
Set `DATABASE_URL` in environment, e.g.
```
mysql+pymysql://user:password@localhost:3306/flask_mvc
```
Then run the app. For migrations:
```
flask db init
flask db migrate -m "init"
flask db upgrade
```

## Structure
See the `flask_app/` tree in your request.



<!-- PS C:\Users\Chetan\Downloads\flask_app_mvc> cd .\flask_app\
PS C:\Users\Chetan\Downloads\flask_app_mvc\flask_app> .\venv\Scripts\Activate.ps1
>> 
(venv) PS C:\Users\Chetan\Downloads\flask_app_mvc\flask_app> flask run --debug
 * Debug mode: on -->