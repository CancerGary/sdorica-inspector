import os

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from requests_oauthlib import OAuth2Session

from backend.api.models import Profile, DiscordInvite

OAUTH2_CLIENT_ID = os.environ.get('DISCORD_OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.environ.get('DISCORD_OAUTH2_CLIENT_SECRET')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true' if settings.DEBUG else 'false'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'


def login_view(request):
    '''
    email login view
    '''
    alert_msg = ""
    if request.method == 'POST' and request.POST.get('username') and request.POST.get('password'):
        # discord users don't have password, so it should fail.
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            try:
                # check if user have discord_id
                if user.profile.discord_id:
                    alert_msg = 'Please login by Discord.'
                else:
                    login(request, user)
                    return redirect('/')
            except Profile.DoesNotExist:
                # old users don't have user.profile
                login(request, user)
                return redirect('/')
        else:
            alert_msg = 'Invalid username or password. Maybe you can contact Puggi for help.'
    return render(request, template_name='login.html', context={'alert': alert_msg})


def discord_redirect_view(request):
    '''
    discord redirect view
    '''
    scope = 'identify'
    discord = make_session(scope=scope.split(' '), request=request)
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    request.session['oauth2_state'] = state
    return redirect(authorization_url)


def discord_callback_view(request):
    if request.GET.get('error'):
        return redirect('/')
    discord = make_session(state=request.session.get('oauth2_state'), request=request)
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.build_absolute_uri())
    request.session['oauth2_token'] = token
    # auth the user
    discord_user = discord.get(API_BASE_URL + '/users/@me').json()
    try:
        user = User.objects.get(profile__discord_id=discord_user['id'])
    except:
        # create new user
        user = User.objects.create_user(username=discord_user['username'])
        user.save()
        user.profile.discord_id = discord_user['id']
        user.profile.save()

    try:
        # check if the user is in the invite list
        DiscordInvite.objects.get(discord_id=discord_user['id'])
        login(request, user)
    except DiscordInvite.DoesNotExist:
        pass
    return redirect('/')


def token_updater_factory(request):
    def token_updater(token):
        request.session['oauth2_token'] = token

    return token_updater


def make_session(token=None, state=None, scope=None, request=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri="http://%s/discord_oauth/callback" % (request.META['HTTP_HOST']),
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater_factory(request))
