# Sdorica Inspector

Just a panel. Based on [gtalarico/django-vue-template](https://github.com/gtalarico/django-vue-template). Use Vuetify for fun.

### Structure


| Location             |  Content                                   |
|----------------------|--------------------------------------------|
| `/backend`           | Django Project & Backend Config            |
| `/backend/api`       | Django App (`/api`)                        |
| `/src`               | Vue App .                                  |
| `/src/main.js`       | JS Application Entry Point                 |
| `/public/index.html` | Html Application Entry Point (`/`)         |
| `/public/static`     | Static Assets                              |
| `/dist/`             | Bundled Assets Output (generated at `yarn build` |

## Setup

```
$ yarn install
$ pipenv install --dev & pipenv shell
$ python manage.py migrate
```

## Running Development Servers

```
$ python manage.py runserver
$ celery -A backend.api.celery worker --loglevel=info
$ celery -A backend.api.celery flower  # run flower if you need monitor
```

From another tab in the same directory:

```
$ yarn serve
```

The Vuejs application will be served from `localhost:8080` and the Django Api
and static files will be served from `localhost:8000`.

The dual dev server setup allows you to take advantage of
webpack's development server with hot module replacement.
Proxy config in `vue.config.js` is used to route the requests
back to django's Api on port 8000.

If you would rather run a single dev server, you can run Django's
development server only on `:8000`, but you have to build build the Vue app first
and the page will not reload on changes.

```
$ yarn build
$ python manage.py runserver
```


## Deploy

* Clone the repo
* Set `ALLOWED_HOSTS` on `backend.settings.prod.py`
* Run `deploy.sh` to install the requirements and build frontend code.
* run `run.sh` to start the server