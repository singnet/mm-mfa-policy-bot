
mfa_message = '''
### MFA Reminder (**{} days left**)

You do not have MFA enabled. Please enable it in your profile settings to keep your account secure. After the expiration date, your account may be deactivated.'''

final_message = '''
### WARNING :warning: 

### MFA Reminder (**0 days left**)

You do not have MFA enabled. Please enable it immediately in your profile settings, otherwise your account will be deactivated!'''

class BotSettings:
    MATTERMOST_URL = ""
    MATTERMOST_PORT = 443
    BOT_TOKEN = "" # bot token for authorization
    BOT_TEAM_NAME = "" # name of the team (already created) in which the bot will work
    BOT_TEAM_ID = "" # id of the team (already created) in which the bot will work
    SSL_VERIFY = False
    DAYS_ALLOWED = 7 # number of days to enable MFA
    CHECK_TIME = 8 # int value 0-23 time (hours) (UTC) when the check is started daily
    DB_PATH = "" # absolute path to sqlite db file, e.g. "/path/to/mfa_bot_db.db"
    DEBUG = False # debug mode for logging
    MFA_MESSAGE = mfa_message
    FINAL_MFA_MESSAGE = final_message
