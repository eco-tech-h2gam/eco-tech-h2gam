build: heroku.yml
web: sh setup.sh && conda init bash && conda eco-tech-h2gam create -f environment.yml && conda activate eco-tech-h2gam && streamlit run app.py

# Uncomment this `release` process if you are using a database, so that Django's model
# migrations are run as part of app deployment, using Heroku's Release Phase feature:
# https://docs.djangoproject.com/en/5.0/topics/migrations/
# https://devcenter.heroku.com/articles/release-phase
#release: ./manage.py migrate --no-input
