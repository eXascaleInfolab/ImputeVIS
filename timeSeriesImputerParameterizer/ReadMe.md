To run server:
```commandline
python manage.py runserver
```

To change port, append port as follows:
```commandline
python manage.py runserver 8080
```

To run on public IP:
```commandline
python manage.py runserver 0.0.0.0:8080
```

To create an app with its directories:
```commandline
python manage.py startapp <app_name>
```


To change database:  
https://docs.djangoproject.com/en/4.2/intro/tutorial02/#database-setup

Migrations are how Django stores changes to your models (and thus your database schema) - they’re files on disk.