# mattermost bot for checking MFA

## Requirements

- python 3.10+
- python packages:
    - mmpy_bot==2.2.1

## Installation

```bash
git clone https://github.com/singnet/mm-mfa-policy-bot.git
cd mm-mfa-policy-bot
pip install -r requirements.txt
```

## Running

First you need to fill in the settings in `settings.py`. The description is attached there.

```bash
nano app/settings.py
# changing file
# saving and exiting
```

Then run the bot:

```bash
python3 app/bot.py
```

## Usage

The bot supports the following commands:
- `start` - starts the daily check
- `report` - sends a report of users without MFA
- `reset` - resets the days left for all users
- `stop` - stops the daily check

> The commands will only work in DM between a user with the `system_admin` role and a bot.

## Additionally

In test, you can run the bot like above or in the background

```bash
nohup python3 app/bot.py > bot.log 2>&1 & # in "mm-mfa-policy-bot" directory
```

and stop it with

```bash
ps aux | grep bot.py
kill <PID>
```
## Lounch As a Service

In production, it is best to configure and run the bot as `systemd service`.
To do this find `etc/systemd/system/mm-mfa-policy-bot.service` and update it with correct path to your app.
Copy that file to your systemd directory (for Ubuntu it will be /etc/systemd/system).

```bash
sudo systemctl daemon-reload
sudo systemctl enable mm-mfa-policy-bot.service
sudo systemctl start mm-mfa-policy-bot.service
```
