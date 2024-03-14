Discord bot integration with the LMS Instructure / Canvas.

# How to use
1. Install the requirements (run a command prompt in the project's root and type "pip install -r requirements.txt"
2. Open the bot.py file and replace the important token information with the token information relating to you specifcally
3. Save and close bot.py, then launch it using start.bat
4. If you've done everything correctly, it should now work!
5. In the discord channel, use the bot's commands to set up your courses for it to understand what information it needs to grab

# How do I get discordToken?
This is the Discord bot's token, obtained from the discord developer portal.

# How do I get discordChannelID?
In Discord, go to the settings and enable developer mode. Then go to the channel you want the bot to speak in, and right click it in the channel listing, then "Copy ID".

# How do I get canvasToken?
From your Instructure / Canvas account, you'll likely need to make a request of some sort in your profile settings.

# How do I get canvasBaseUrl?
Just replace the "yourschool" part in the string with your relevent school's domain. For example, Northern Arizona University's might be "https://nau.instructure.com".

# It doesn't work, what do I do?
Make an issue.
