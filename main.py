import telebot
from telebot import types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import requests
import youtube_dl

# Initialize the Telegram bot
bot = telebot.TeleBot("YOUR_BOT_TOKEN")


# Use the credentials from the JSON file to authenticate with the Google Drive API
creds = Credentials.from_authorized_user_info(info=json.loads("JSON_CREDENTIALS_FILE"))
service = build('drive', 'v3', credentials=creds)


# Function to upload a file to Google Drive
def upload_to_drive(file, file_name, parent_id=None, team_drive_id=None):
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file, mimetype='application/octet-stream')
    if parent_id:
        file_metadata['parents'] = [parent_id]
    if team_drive_id:
        file_metadata['teamDriveId'] = team_drive_id
        file_metadata['supportsTeamDrives'] = True
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

  
# Function to create a folder in Google Drive
def create_folder(folder_name, parent_id=None, team_drive_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    if team_drive_id:
        file_metadata['teamDriveId'] = team_drive_id
        file_metadata['supportsTeamDrives'] = True
    file = service.files().create(body=file_metadata, fields='id').execute()
    return file.get('id')

  
# Function to clone/copy a file in Google Drive
def clone_file(file_id, new_file_name, parent_id=None, team_drive_id=None):
    file_metadata = {'name': new_file_name}
    if parent_id:
      file_metadata['parents'] = [parent_id]
    if team_drive_id:
      file_metadata['teamDriveId'] = team_drive_id
      file_metadata['supportsTeamDrives'] = True
      file = service.files().copy(fileId=file_id, body=file_metadata).execute()
    return file.get('id')


# Function to delete a file in Google Drive
def delete_file(file_id):
    service.files().delete(fileId=file_id).execute()

  
# Function to empty the trash in Google Drive
def empty_trash():
    service.files().emptyTrash().execute()
  
  
# Handle the '/upload' command
@bot.message_handler(commands=['upload'])
def handle_upload(message):
    # Retrieve the file's ID, name, and custom folder from the message text
    file_id = message.document.file_id
    file_name = message.document.file_name
    folder_name = message.text.split()[1]
    # Create the custom folder in Google Drive
    parent_id = create_folder(folder_name)
    # Download the file and upload it to the custom folder in Google Drive
    file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, bot.get_file(file_id).file_path)
    response = requests.get(file_url)
    upload_to_drive(response.content, file_name, parent_id)
    bot.reply_to(message, "File has been uploaded to Google Drive in the '{}' folder!".format(folder_name))
  

@bot.message_handler(commands=['upload_link'])
def handle_upload_link(message):
    # Retrieve the link, file name, and custom folder from the message text
    link = message.text.split()[1]
    file_name = message.text.split()[2]
    folder_name = message.text.split()[3]
    # Create the custom folder in Google Drive
    parent_id = create_folder(folder_name)
    # Download the file from the link and upload it to the custom folder in Google Drive
    response = requests.get(link)
    upload_to_drive(response.content, file_name, parent_id)
    bot.reply_to(message, "File has been uploaded to Google Drive in the '{}' folder!".format(folder_name))

# Handle the '/clone' command
@bot.message_handler(commands=['clone'])
def handle_clone(message):
    # Retrieve the file ID and new file name from the message text
    file_id = message.text.split()[1]
    new_file_name = message.text.split()[2]
    # Clone/copy the file in Google Drive
    clone_id = clone_file(file_id, new_file_name)
    bot.reply_to(message, "File has been cloned/copied in Google Drive with ID: {}".format(clone_id))

# Handle the '/delete' command
@bot.message_handler(commands=['delete'])
def handle_delete(message):
    # Retrieve the file ID from the message text
    file_id = message.text.split()[1]
    # Delete the file in Google Drive
    delete_file(file_id)
    bot.reply_to(message, "File has been deleted from Google Drive!")
    

def handle_empty_trash(message):
    # Empty the trash in Google Drive
    empty_trash()
    bot.reply_to(message, "Google Drive trash has been emptied!")


# Handle the '/upload_youtube' command
@bot.message_handler(commands=['upload_youtube'])
def handle_upload_youtube(message):
    # Retrieve the YouTube link, file name, and custom folder from the message text
    link = message.text.split()[1]
    file_name = message.text.split()[2]
    folder_name = message.text.split()[3]
    # Create the custom folder in Google Drive
    parent_id = create_folder(folder_name)
    # Use youtube-dl to download the video from YouTube
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(link, download=True)
    # Upload the video to the custom folder in Google Drive
    upload_to_drive(result['filename'], file_name, parent_id)
    bot.reply_to(message, "Video has been uploaded to Google Drive in the '{}' folder!".format(folder_name))


bot.polling()
  
  
  
  
  
  
  
  
  
  
