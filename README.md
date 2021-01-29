# A REAL ESTATE PLATFORM BUILT WITH DJANGO

Visit website @ https://homerealty.herokuapp.com/


## Benefits 
1. Prospective clients can make purchase, rent and investment orders directly
   from the website.

2. Properties can be presented easily from the admin page with choice to include
   features, pictures and plans.

## Features
1. Instant email notification of customer enquiries

2. Automated sales receipt

3. With one click, you can email receipt to clients

4. A blog

5. A smart search engine that searches properties based on relevance to search
   keywords.



## Follow these steps to run this project on your local machine

1. Clone repo and execute the following commands on your shell/terminal

```json
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
2. Fill in the necessary data in .env file
3. Go to settings.py in blogman directory and change value of DEBUG to True

Visit website @ https://homerealty.herokuapp.com/