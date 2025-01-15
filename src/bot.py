import asyncio
import random
import string
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import mysql.connector
from mysql.connector import pooling
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# load environment variables (token, database)
load_dotenv(dotenv_path="config.env")

# load the values of the environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = "users"
DB_HOST = os.getenv("DB_HOST")

server_id = #your server id
reset_limit_days = 7  # reset limit in days

# connection pooling setup
dbconfig = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
}
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool", pool_size=5, **dbconfig
)

# function to generate a random key
def generate_key(length=16):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

# function to clean up expired trials
async def cleanup_expired_trials():
    while True:
        db_conn = connection_pool.get_connection()
        cursor = db_conn.cursor()
        try:
            now = datetime.now()
            cursor.execute(
                "UPDATE logins SET trial_completed = TRUE, `key` = NULL WHERE trial_end < %s",
                (now,),
            )
            db_conn.commit()
        except mysql.connector.Error as err:
            print(f"Error during cleanup: {err}")
        finally:
            cursor.close()
            db_conn.close()

        await asyncio.sleep(120)

# function to manage duplicate HWIDs
async def manage_duplicates():
    while True:
        db_conn = connection_pool.get_connection()
        cursor = db_conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT hwid, COUNT(*) as count 
                FROM logins 
                GROUP BY hwid 
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()

            for duplicate in duplicates:
                hwid = duplicate['hwid']
                
                cursor.execute("""
                    SELECT id, discord_id 
                    FROM logins 
                    WHERE hwid = %s 
                    ORDER BY id
                """, (hwid,))
                rows = cursor.fetchall()

                for row in rows[1:]:
                    discord_id = row['discord_id']
                    
                    # get Discord username
                    user = await aclient.fetch_user(discord_id)
                    discord_username = user.name if user else "Unknown"
                    
                    # insert in the excluded_users table with the username
                    cursor.execute("""
                        INSERT INTO excluded_users (discord_id, discord_username, hwid, exclusion_date)
                        VALUES (%s, %s, %s, %s)
                    """, (discord_id, discord_username, hwid, datetime.now()))
                    
                    cursor.execute("DELETE FROM logins WHERE id = %s", (row['id'],))
                
                db_conn.commit()

        except mysql.connector.Error as err:
            print(f"Error managing duplicates: {err}")
        finally:
            cursor.close()
            db_conn.close()

        await asyncio.sleep(120)


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=server_id))
            self.synced = True
        print(f"Logged in as {self.user}")
        self.loop.create_task(cleanup_expired_trials())
        self.loop.create_task(manage_duplicates())

# bot instance and command tree
aclient = MyClient()
tree = app_commands.CommandTree(aclient)

@tree.command(
    guild=discord.Object(id=server_id),
    name="register_user",
    description="Register a new user or upgrade a trial user",
)
async def register_user(interaction: discord.Interaction, user_id: str):
    your_id = #your id

    if interaction.user.id != your_id:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
        return

    db_conn = connection_pool.get_connection()
    cursor = db_conn.cursor()

    try:
        cursor.execute(
            "SELECT `key`, trial_end, trial_completed FROM logins WHERE discord_id = %s",
            (user_id,),
        )
        result = cursor.fetchone()

        if result:
            trial_key, trial_end, trial_completed = result

            if trial_completed:
                new_key = generate_key()
                sql = "UPDATE logins SET `key` = %s, trial_completed = TRUE, trial_end = NULL WHERE discord_id = %s"
                cursor.execute(sql, (new_key, user_id))
                db_conn.commit()

                await interaction.response.send_message(
                    f"User successfully upgraded to full account!\nNew key: `{new_key}`",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "User is already registered but still has an active trial.",
                    ephemeral=True,
                )

        else:
            user = await aclient.fetch_user(user_id)
            discord_user_name = user.name if user else "Unknown"
            generated_key = generate_key()
            sql = "INSERT INTO logins (discord_id, username, `key`) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, discord_user_name, generated_key))
            db_conn.commit()

            await interaction.response.send_message(
                f"User {discord_user_name} registered successfully! The generated key is: `{generated_key}`",
                ephemeral=True,
            )

    except mysql.connector.Error as err:
        await interaction.response.send_message(
            f"Error registering or updating user: {err}", ephemeral=True
        )
    finally:
        cursor.close()
        db_conn.close()

@tree.command(
    guild=discord.Object(id=server_id),
    name="reset_hwid",
    description="Reset HWID to NULL",
)
async def reset_hwid(interaction: discord.Interaction):
    discord_user_id = interaction.user.id

    db_conn = connection_pool.get_connection()
    cursor = db_conn.cursor()

    cursor.execute(
        "SELECT last_reset FROM logins WHERE discord_id = %s", (discord_user_id,)
    )
    result = cursor.fetchone()

    if result is None:
        await interaction.response.send_message(
            "Error: user not found in the database.", ephemeral=True
        )
        cursor.close()
        db_conn.close()
        return

    if result[0]:
        last_reset = result[0]
        now = datetime.now()

        if isinstance(last_reset, str):
            last_reset = datetime.strptime(last_reset, "%Y-%m-%d %H:%M:%S")

        if now - last_reset < timedelta(days=reset_limit_days):
            remaining_hours = (
                last_reset + timedelta(days=reset_limit_days) - now
            ).total_seconds() // 3600
            await interaction.response.send_message(
                f"You have already reset your HWID in the last 7 days. Please try again in {remaining_hours:.0f} hours.",
                ephemeral=True,
            )
            cursor.close()
            db_conn.close()
            return

    button = Button(label="Reset HWID", style=discord.ButtonStyle.danger)

    async def button_callback(interaction: discord.Interaction):
        db_conn = connection_pool.get_connection()
        cursor = db_conn.cursor()
        try:
            sql = "UPDATE logins SET hwid = NULL, last_reset = %s WHERE discord_id = %s"
            cursor.execute(sql, (datetime.now(), discord_user_id))
            db_conn.commit()

            button.disabled = True
            remaining_hours = reset_limit_days * 24
            await interaction.response.edit_message(
                content=f"HWID for user {interaction.user.name} has been reset successfully! You can reset again in {remaining_hours} hours.",
                view=view,
            )
        except mysql.connector.Error as err:
            await interaction.response.send_message(f"Error: {err}", ephemeral=True)
        finally:
            cursor.close()
            db_conn.close()

    button.callback = button_callback

    view = View()
    view.add_item(button)
    await interaction.response.send_message(
        "Click the button to reset the HWID.", view=view, ephemeral=True
    )

@tree.command(
    guild=discord.Object(id=server_id),
    name="start_trial",
    description="Start a trial for the user",
)
async def start_trial(interaction: discord.Interaction):
    db_conn = connection_pool.get_connection()
    cursor = db_conn.cursor()

    try:
        # check if the user is in the excluded_users table
        cursor.execute(
            "SELECT 1 FROM excluded_users WHERE discord_id = %s",
            (interaction.user.id,),
        )
        if cursor.fetchone():
            await interaction.response.send_message(
                "You are not eligible to start a trial.", ephemeral=True
            )
            return

        # continue with the existing trial logic
        cursor.execute(
            "SELECT `key`, trial_end, trial_completed FROM logins WHERE discord_id = %s",
            (interaction.user.id,),
        )
        result = cursor.fetchone()

        if result:
            trial_key, trial_end, trial_completed = result

            if trial_completed:
                await interaction.response.send_message(
                    "You have already completed the trial.", ephemeral=True
                )
            elif trial_end > datetime.now():
                time_left = trial_end - datetime.now()
                time_left_formatted = str(time_left).split(":")[:2]
                await interaction.response.send_message(
                    f"Your trial is already active. Key: `{trial_key}`. Time left: {time_left_formatted[0]} hours and {time_left_formatted[1]} minutes.",
                    ephemeral=True,
                )
            else:
                cursor.execute(
                    "UPDATE logins SET trial_completed = TRUE, `key` = NULL WHERE discord_id = %s",
                    (interaction.user.id,),
                )
                db_conn.commit()
                await interaction.response.send_message(
                    "Your trial has expired.", ephemeral=True
                )
            return

        generated_key = generate_key()
        sql = "INSERT INTO logins (discord_id, username, `key`, trial_end, trial_completed) VALUES (%s, %s, %s, %s, %s)"
        trial_end_time = datetime.now() + timedelta(hours=3)
        cursor.execute(
            sql,
            (
                interaction.user.id,
                interaction.user.name,
                generated_key,
                trial_end_time,
                False,
            ),
        )
        db_conn.commit()

        trial_end_formatted = trial_end_time.strftime("%H:%M")
        await interaction.response.send_message(
            f"Your trial has started! Key: `{generated_key}`. Expires at: {trial_end_formatted}.",
            ephemeral=True,
        )

    except mysql.connector.Error as err:
        await interaction.response.send_message(f"Error: {err}", ephemeral=True)
    finally:
        cursor.close()
        db_conn.close()

aclient.run(TOKEN)