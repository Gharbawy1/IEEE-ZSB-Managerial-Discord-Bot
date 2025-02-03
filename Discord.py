import os
# import discord
import re # for regex
import typing
from discord.ext import commands
from dotenv import load_dotenv
import discord
from typing import Optional

from discord import app_commands
from googleapiclient.http import MediaFileUpload
from datetime import datetime
import asyncio



# from discord import app_commands
from commands import authenticate_google_drive

# Load environment variables
load_dotenv()
print(os.getenv("TOKEN"))
DISCORD_TOKEN = os.getenv("TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
GUILD_ID = os.getenv("GUILD_ID")
print(os.getenv("TOKEN"))
# Here I create a Dict to use the key in the send task function 
TEAM_FOLDER_IDS = {
    "T&T": "1ngxwttt_Zk9yKGrYLyr2HjHhJDn2ocAD",
    "Media": "1V7oskd81M4XnKdK48k453naU3D6qM7Q7",
    "Marketing": "1LH0_-gX9lBhHZhqyibckqlAo-SkSDgug",
    "Ambassadors": "1kHut2A8kN0k9_-yGXIn9uBEL6ZhX3K92",
    "EM": "1zzhXKNt1XOFNfhOO9yNE4Yx77xzqwhCq",
    "BD": "1LGXLqzjB1-TEAnnQpR0rETdaK_ZHuvGl",
    "WIE":"1zXUS3Dw1nlp_vA0G-1PcJZYfEIjxx4fw"
}


# Set up Discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents) #bot object
tree = app_commands.CommandTree(client)

intents.messages = True
intents.message_content = True

@client.event
async def on_ready():
    """Notify when the bot is ready."""
    print(f'{client.user} has connected to Discord!')

# Finish Task Command
@tree.command(
    name="finish_task",
    description="Finish your task by uploading a file.",
    guild=discord.Object(id=GUILD_ID),
)
async def finish_task(interaction: discord.Interaction, file: discord.Attachment):
    try:
        await interaction.response.defer(thinking=True)

        # Save the file locally
        file_extension = file.filename[file.filename.rfind('.'):]  # Extract the file extension (e.g., .pdf, .docx)
        unsafe_file_name = f"{interaction.user.display_name} | {interaction.channel.name}{file_extension}"  # Construct new file name
        safe_file_name = re.sub(r'[<>:"/\\|?*]', '-', unsafe_file_name)  # Replace unsafe characters with '-'

        await file.save(safe_file_name)  # Save the file locally with the new name

        # Get the team based on the channel category
        channel = interaction.channel
        category_name = channel.category.name if channel.category else None

        # Ensure the channel is under one of the allowed categories
        if category_name not in TEAM_FOLDER_IDS:
            await interaction.followup.send("This command can only be used in 'finished-tasks' channels under valid team categories.")
            return

        # Get the team folder ID from the category name
        team_folder_id = TEAM_FOLDER_IDS.get(category_name)

        # Get the thread name based on the 'tasks' thread
        thread_name = interaction.channel.name  # Assuming thread name matches folder name
        folder_path = f"{team_folder_id}/{thread_name}"  # Path in Google Drive

        # Authenticate Google Drive
        drive_service = authenticate_google_drive()

        # Search for the thread folder in the team's directory
        query = f"'{team_folder_id}' in parents and name = '{thread_name}' and mimeType = 'application/vnd.google-apps.folder'"
        response = drive_service.files().list(q=query, fields="files(id)").execute()
        folder = response.get("files", [])
        
        if not folder:
            # Create a new folder if it doesn't exist
            folder_metadata = {
                "name": thread_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [team_folder_id],
            }
            folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
            folder_id = folder.get("id")
        else:
            folder_id = folder[0].get("id")  # Use the existing folder ID

        # Upload the file to the task folder in Google Drive
        file_metadata = {
            "name": safe_file_name,  # Use the new file name here
            "parents": [folder_id],
        }
        media = MediaFileUpload(safe_file_name, resumable=True)
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # Log the task submission in Google Sheets
        username = interaction.user.display_name
        user_id = str(interaction.user.id)
        handed_task = "Yes"
        submission_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            
        # This is Part for log Member Task Done #
        # FLOW : You Get the team name => know what is task number the member send "thread name" =>go to the tab in its sheet => and log 
        from commands import log_task_to_sheet
        if category_name == "Ambassadors":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1Sx1PExlBm6UuWE_XjqATQ1K0iN-vwb6hvzDRQEHQKzQ",thread_name)
        
        elif category_name == "EM":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1Sx1PExlBm6UuWE_XjqATQ1K0iN-vwb6hvzDRQEHQKzQ",thread_name)

        elif category_name == "T&T":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"12R0_7UcHw0Ia_7q6s-Gf9ZQ_N-pIJK-ARF2X06AbrSU",thread_name)

        elif category_name == "Media":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1O1npgal2t06VmbVy7IoiKKpwl6p2PUGJdbLfIp5Am_s",thread_name)

        elif category_name == "Marketing":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1vOWhcTyiYr9kx9MdO3rAJpGXcPQ4twmRcZbLpzLA6kY",thread_name)

        elif category_name == "BD":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1WcuenMTKIDCr2g4qXK59yWQgpYzj8IdoPjTXFkG3zDs",thread_name)
        
        elif category_name == "WIE":
            log_task_to_sheet(username,user_id,handed_task,submission_date,"1gSfnChXbEL6uZoB8Wy-Oyy7Q5eDfZdHisKHk3MV2JVk",thread_name)
        
        
        
        # Send confirmation
        await interaction.followup.send(f"File `{safe_file_name}` uploaded successfully to task folder: `{thread_name}` in team `{category_name}`.")
    
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")


ALLOWED_ROLES = ['T&T Team Lead','BD Team Lead','EM Team Lead','Ambassadors Team Lead','Marketing Team Lead','Media Team Lead']

@tree.command(
    name="send_task_message",
    description="Send a task message to the appropriate team.",
    guild=discord.Object(id=GUILD_ID),
)
@app_commands.describe(
    message_content="The content of the message (optional)",
    file="An optional file attachment",
    scheduled_time="Scheduled time (Year-Month-Day HH:MM, optional)",
    task_num="The task number (e.g., Task 1)",
    team="The team to send the task message to",
)
@app_commands.choices(
    team=[
        app_commands.Choice(name="T&T", value="T&T"),
        app_commands.Choice(name="Media", value="Media"),
        app_commands.Choice(name="Marketing", value="Marketing"),
        app_commands.Choice(name="Ambassadors", value="Ambassadors"),
        app_commands.Choice(name="EM", value="EM"),
        app_commands.Choice(name="BD", value="BD"),
        app_commands.Choice(name="WIE", value="WIE"),

    ]
)

async def send_task_message(
    interaction: discord.Interaction,
    message_content: Optional[str] = None,
    file: Optional[discord.Attachment] = None,
    scheduled_time: Optional[str] = None,
    task_num: int = None,
    team: app_commands.Choice[str] = None,
):    
    """Send a task message with options to the team category channel and create a thread."""
    # Check if the user has the necessary role
    if not any(role.name in ALLOWED_ROLES for role in interaction.user.roles):
        await interaction.response.send_message(
            "You don't have permission to use this command.", ephemeral=True
        )
        return
    
    
    guild = interaction.guild
    category_name = team.value #Such EM ,BD ,... [ Team Name ]
    
    
    await interaction.response.defer(thinking=True)
    
    # Create a new tab for the task in the team sheet 
    from commands import create_tab_in_sheet
    if category_name == "Ambassadors":
        create_tab_in_sheet("1Q6poWri2n2hLkPCk08EI6FjssKevq268WyNRRkTxF10",f"Task_{task_num}")
    elif category_name == "EM":
        create_tab_in_sheet("1Sx1PExlBm6UuWE_XjqATQ1K0iN-vwb6hvzDRQEHQKzQ",f"Task_{task_num}")
    elif category_name == "T&T":
        create_tab_in_sheet("12R0_7UcHw0Ia_7q6s-Gf9ZQ_N-pIJK-ARF2X06AbrSU", f"Task_{task_num}")
    elif category_name == "Media":
        create_tab_in_sheet("1O1npgal2t06VmbVy7IoiKKpwl6p2PUGJdbLfIp5Am_s", f"Task_{task_num}")
    elif category_name == "Marketing":
        create_tab_in_sheet("1vOWhcTyiYr9kx9MdO3rAJpGXcPQ4twmRcZbLpzLA6kY", f"Task_{task_num}")
    elif category_name == "BD":
        create_tab_in_sheet("1WcuenMTKIDCr2g4qXK59yWQgpYzj8IdoPjTXFkG3zDs", f"Task_{task_num}")
    elif category_name == "WIE":
        create_tab_in_sheet("1gSfnChXbEL6uZoB8Wy-Oyy7Q5eDfZdHisKHk3MV2JVk", f"Task_{task_num}")
    
    
    category = discord.utils.get(guild.categories, name=category_name) # Get the category
    task_channel = discord.utils.get(category.channels, name="tasks")  # Get The tasks Channel
    
    thread_name = f"Task_{task_num}"
    thread = await task_channel.create_thread(name=thread_name, type=discord.ChannelType.public_thread)

    #To create in the finished-tasks a thread when lead create a thread to send the task
    finished_task_channel = discord.utils.get(category.channels, name="finished-tasks")  # Get The finished-tasks Channel
    finished_thread_name = f"Task_{task_num}"
    await finished_task_channel.create_thread(name=finished_thread_name, type=discord.ChannelType.public_thread)
    

    folder_id = TEAM_FOLDER_IDS.get(team.value)
    # Create a folder in Google Drive with the thread name
    drive_service = authenticate_google_drive()
    folder_metadata = {
        "name": thread_name,
        "mimeType": "application/vnd.google-apps.folder",  # Specify folder type
        "parents": [folder_id],  # Set the parent folder
    }   
    drive_service.files().create(body=folder_metadata).execute()

    #await interaction.response.defer()  # Acknowledges the interaction and gives more time

    try:
        # Handle the scheduling part
        file_path = file.filename  # Gets the file name
        await file.save(file_path)  # Saves the file locally
        if scheduled_time:
            # If a scheduled time is provided, the folder is created immediately, but the message is delayed.
            # Parse the scheduled time
            schedule_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M")
            current_dt = datetime.now()

            # Calculate delay in seconds
            delay = (schedule_dt - current_dt).total_seconds()

            # Create the folder immediately for scheduling
            folder_metadata = {
                "name": thread_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [folder_id],
            }
            drive_service.files().create(body=folder_metadata).execute()

            # Schedule the message
            await asyncio.sleep(delay)
            await thread.send(
                content=message_content or "",
                file=discord.File(file_path) if file_path else None,
            )
        else:
            # Immediate message processing
            # There is also be a file 
            await thread.send(
                content=message_content or "",
                file=discord.File(file_path) if file_path else None,
            )
        
        await interaction.followup.send(f"Task {task_num} has been successfully created!")

    except Exception as e:
        await print(f"An error occurred: {str(e)}")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print("Command Added")
# Run the bot
client.run(DISCORD_TOKEN)

