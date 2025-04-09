### Set up Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Copy environment variables
Since the `.env` file is in a private repository, manually copy its contents from <https://github.com/guardian-exchange/ge-env/blob/master/.env> into `.env` file.

> TODO: Automate this in the future using: 
> ```bash
> wget https://raw.githubusercontent.com/guardian-exchange/ge-env/refs/heads/master/.env?token=<token>
> ```

### Run migrations
```bash
python manage.py migrate
```

### Run Django backend
```bash
python manage.py runserver
```
