# Sdorica Inspector

![Ned Spear Logo](https://i.imgur.com/EqSn22E.png)

## Introduce

The web application is an tool for multiple users in a team to analyze game data and Unity AssetBundles online. It starts from POC, and is currently designed for Sdorica only. The project is inspired by [AssetStudio](https://github.com/Perfare/AssetStudio), using [UnityPack](https://github.com/HearthSim/UnityPack) for deserialization, and [django-vue-template](https://github.com/gtalarico/django-vue-template) for startup.

With the tool, you can analyze these data through the browser (whether desktop or mobile). While all the data has been stored on the server, you needn't to download all the AssetBundle to you computer. More over, you can share URL, JS code and convert rules between your team if needed, or call APIs for further purpose.

中文 (WIP)

## Features

- Imperium (msgpack format game data used by Rayark) and AssetBundles collecting & diff
- Searching containers/assets in all AssetBundles by keywords
- AssetBundle viewer: inspect raw assets data and media assets (currently support `Sprite`, `Texture2D` (support ETC2), `AudioClip` )
- [Spine web player](<http://esotericsoftware.com/spine-player>) integration, with converting Spine `v3.2.01` `.skel` to latest `.json` support (web player supports `.json` file only), and GIF export.
- Client-side script: Enhancing AssetBundle viewer/ Executing custom scripts by client-side JavaScript ( for example, convert asset data to human-readable text or [Wikitext](<https://en.wikipedia.org/wiki/Help:Wikitext>) )
- Convert rules: a diction for looking up the meaning of some ID when analyzing
- Select then lookup: "translate" selected words according to convert rules, or check the version of an AssetBundle.
- User groups for access control (read_only or standard) based on Django authentication system
- Discord [OAuth2](<https://discordapp.com/developers/docs/topics/oauth2>) Support, managing whitelisting through Django admin
- Dark theme (Vuetify)

[Screenshots](<https://github.com/CancerGary/sdorica-inspector/blob/master/screenshots.md>)

Live Demo: (WIP)

## Special Thanks

- [Shiaupiau](https://github.com/stu43005)
- [Sdorica Wiki](https://sdorica.xyz/)

## Teck Stack

- Backend: Django + Django REST framework + Celery (for async download)
- Frontend: Vue + Vuetify

## Environment variables

| Name (*=required)              | Default                                      | Meaning                                                      |
| ------------------------------ | -------------------------------------------- | ------------------------------------------------------------ |
| `DATABASE_URL` *               | -                                            | Database URL for [dj-database-url](https://github.com/jacobian/dj-database-url) |
| `SECRET_KEY`                   | `secrets.token_urlsafe(64)` on every startup | [Django SECRET_KEY](https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY) |
| `DJANGO_SETTINGS_MODULE`       | `backend.settings.prod`(wsgi.py)             | Django settings module                                       |
| `INSPECTOR_PYPY_PATH`          | -                                            | PyPy acceleration for ETC2Decoder                            |
| `DISCORD_OAUTH2_CLIENT_ID`     | -                                            | Discord OAuth2 client ID                                     |
| `DISCORD_OAUTH2_CLIENT_SECRET` | -                                            | Discord OAuth2 client secret                                 |

## Prerequisites

Before getting started you should have the following installed and running:

- [X] Yarn - [instructions](https://yarnpkg.com/en/docs/install)
- [X] Vue CLI 3 - [instructions](https://cli.vuejs.org/guide/installation.html)
- [X] Python 3 (Recommend 3.6) - [instructions](https://wiki.python.org/moin/BeginnersGuide)
- [X] Pipenv - [instructions](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)
- [ ] Redis - required only if you need to download ABs by Celery asynchronous task.

## Deploy

* Clone the repo.
* Set the environment variables according to your needs
* Run `deploy.sh` to install the requirements and build frontend code.
* (Optional) Create superuser using `pipenv run python manage.py createsuperuser`
* run `run.sh` to start the server.

## Project Structure

| Location             | Content                                          |
| -------------------- | ------------------------------------------------ |
| `/backend`           | Django Project & Backend Config                  |
| `/backend/api`       | Django App (`/api`)                              |
| `/src`               | Vue App .                                        |
| `/src/main.js`       | JS Application Entry Point                       |
| `/public/index.html` | Html Application Entry Point (`/`)               |
| `/public/static`     | Static Assets                                    |
| `/dist/`             | Bundled Assets Output (generated at `yarn build` |
| `/data/`             | Data or cache generated by Sdorica Inspector     |

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

More info: [Running Development Servers](https://github.com/gtalarico/django-vue-template#running-development-servers)