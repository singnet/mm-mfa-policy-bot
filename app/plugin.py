from mmpy_bot.plugins.base import Plugin
from mmpy_bot import listen_to, schedule
from datetime import datetime
import logging

from repository import SqliteUserRepo
from settings import BotSettings


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if BotSettings.DEBUG else logging.INFO)


class MFAPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.team_ids = []
        self.admin_ids = []
        self.user_repo = SqliteUserRepo()

    @listen_to("^start$", direct_only = True)
    def initialize_daily_check(self, message):
        self.update_admins()

        if message.user_id not in self.admin_ids:
            logger.info(f"User {message.user_id} is not an admin")
            return

        schedule.every().day.at(BotSettings.CHECK_TIME).do(self.run_daily_check)

        # For testing
        # schedule.every(10).seconds.do(self.run_daily_check)

        try:
            self.driver.create_post(
                message = f"Daily check started, next check will be at {schedule.next_run().time()}",
                channel_id = message.channel_id,
            )
        except Exception as e:
            logger.error(f"Error sending message while starting daily check: {e}")

    @listen_to("^stop$", direct_only = True)
    def stop_daily_check(self, message):
        self.update_admins()

        if message.user_id not in self.admin_ids:
            logger.info(f"User {message.user_id} is not an admin")
            return

        try:
            self.driver.create_post(
                message = "Daily check stopped",
                channel_id = message.channel_id,
            )
        except Exception as e:
            logger.error(f"Error sending message while stopping daily check: {e}")

        schedule.clear()

    @listen_to("^report$", direct_only = True)
    def send_report_to_admin(self, message):
        self.update_admins()

        if message.user_id not in self.admin_ids:
            logger.info(f"User {message.user_id} is not an admin")
            return

        users = self.user_repo.get_users(only_without_mfa = True)
        if len(users) == 0:
            response_msg = "No users without MFA"
        else:
            response_msg = "Users without MFA:\n\n"
            for user in users:
                response_msg += f"- {user.username} - {user.days_left} days left\n"

        try:
            self.driver.create_post(
                message = response_msg,
                channel_id = message.channel_id,
            )
        except Exception as e:
            logger.error(f"Error sending report: {e}")

    @listen_to("^reset$", direct_only = True)
    def reset_days_left(self, message):
        self.update_admins()

        if message.user_id not in self.admin_ids:
            logger.info(f"User {message.user_id} is not an admin")
            return

        self.user_repo.reset_days_left()

        try:
            self.driver.create_post(
                message = "Days left reset",
                channel_id = message.channel_id,
            )
        except Exception as e:
            logger.error(f"Error sending message while resetting days left: {e}")

    def run_daily_check(self):
        self.sync_users()
        self.send_mfa_message_to_users()

    def update_admins(self):
        try:
            system_admins = self.driver.users.get_users(params={"role": "system_admin"})
            self.admin_ids = [admin["id"] for admin in system_admins]
        except Exception as e:
            logger.error(f"Error getting system admins: {e}")
        logger.debug(f"Admins: {self.admin_ids}")

    def sync_users(self):
        if not self.team_ids:
            self.update_team_ids()
        new_users_data = []
        per_page = 1
        for team_id in self.team_ids:
            page_number = 0
            while True:
                logger.info(f"Fetching users, page {page_number}")
                new_users_page = self.driver.users.get_users(params={
                    "in_team": team_id, "active": "true", "page": str(page_number), "per_page": str(per_page)
                })
                new_users_data += new_users_page
                if len(new_users_page) < per_page:
                    break
                page_number += 1
        active_users_ids = []
        last_check_datetime = datetime.now().isoformat()

        for user in new_users_data:
            if user["id"] in active_users_ids:
                logger.debug(f"User {user} already processed, skipping")
                continue
            logger.debug(f"Processing user {user}")
            active_users_ids.append(user["id"])
            self.user_repo.upsert_user(
                user_id = user["id"],
                username = user["username"],
                mfa_active = user.get("mfa_active", 0),
                last_check_datetime = last_check_datetime
            )

        self.user_repo.delete_inactive_users(active_users_ids)

    def send_mfa_message_to_users(self):
        users = self.user_repo.get_users(only_without_mfa = True)
        logger.debug(f"Users without MFA: {users}")

        for user in users:
            if user.days_left != 0:
                message = BotSettings.MFA_MESSAGE.format(user.days_left)
            else:
                message = BotSettings.FINAL_MFA_MESSAGE

            logger.debug(f"driver user_id: {self.driver.user_id}; user user_id: {user.user_id}")
            try:
                channel = self.driver.channels.create_direct_channel(
                    [self.driver.user_id, user.user_id]
                )

                self.driver.create_post(
                    message = message,
                    channel_id = channel["id"],
                )
            except Exception as e:
                logger.error(f"Error creating DM with user {user.user_id}: {e}")
                continue

    def update_team_ids(self):
        for team_name in BotSettings.BOT_TEAM_NAMES:
            try:
                result_team = self.driver.teams.get_team_by_name(name = team_name)
                self.team_ids.append(result_team["id"])
            except Exception as e:
                logger.error(f"Error getting team ID for team {team_name}: {e}")
            logger.info(f"Team ID: {self.team_ids} for team {team_name}")
