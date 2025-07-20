# mattermost bot for checking MFA

## Requirements

- python 3.10+
- python packages:
    - mmpy_bot==2.2.1

## Installation

```bash
git clone https://github.com/Arondondon/mm-mfa-policy-bot.git
cd mm-mfa-policy-bot
pip install -r requirements.txt
```

## Running

First you need to fill in the settings in `settings.py`. The description is attached there.

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
