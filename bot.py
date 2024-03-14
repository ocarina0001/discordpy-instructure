import discord
from discord.ext import tasks
import requests
import datetime
import asyncio
import json
import os
import re

# IMPORTANT README PLEASE
# Insert the necessary information into these variables for the program to work!
discordToken = "yourdiscordtoken"
discordChannelID = 0 # Your channel ID
canvasToken = "yourcanvastoken"
canvasBaseUrl = "https://yourschool.instructure.com"

# to do
# link up email

# important discord stuff
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# declare variables
canvasHeaders = {
    'Authorization': f'Bearer {canvasToken}'
}
#canvasCourseIDList = ["21855"]
# this will allow the display output to actually look how i want
canvasCourseDict = {}
if os.path.isfile('canvasCourseDict.txt'):
    with open('canvasCourseDict.txt', 'r+') as file:
        if os.path.getsize('canvasCourseDict.txt') == 0:
            file.close()
        else:
            canvasCourseDict = json.load(file)
            file.close()
# store assignment ID alongside a bool for completed, maybe added when added course name?
canvasCompletedAssignments = []
if os.path.isfile('canvasCompletedAssignments.txt'):
    with open('canvasCompletedAssignments.txt', 'r+') as file:
        if os.path.getsize('canvasCompletedAssignments.txt') == 0:
            file.close()
        else:
            canvasCompletedAssignments = json.load(file)
            file.close()
canvasTopicList = [
    "assignments",
    "quizzes",
    "discussion_topics"
]
courseList = []
courseInformation = []
dateFormat = "%B %d"
iso8601Format = "%Y-%m-%dT%H:%M:%SZ"
missedAssignments = 0

# main code
@client.event
async def on_ready():
    print('Canvas bot is ready!')
    main.start()
    
@client.event
async def on_message(message):
    # prevents talking to itself
    if message.author == client.user:
        return
    arguments = re.findall(r'"[^"]+"|\S+', message.content)
    # get
    if arguments[0] == "!get" or arguments[0] == "!g":
        await GetInformation()
    # course
    if arguments[0] == "!course":
        # add
        try:
            if arguments[1] == "add":
                try:
                    if arguments[2].isnumeric():
                        try:
                            if isinstance(arguments[3], (str)) and arguments[3].startswith('"') and arguments[3].endswith('"'):
                                courseName = arguments[3].strip('"')
                                canvasCourseDict[int(arguments[2])] = courseName
                                if os.path.isfile('canvasCourseDict.txt'):
                                    with open('canvasCourseDict.txt', 'w') as file:
                                        save = json.dumps(canvasCourseDict)
                                        file.write(save)
                                        file.close()
                                await message.channel.send(f"Successfully added new course.")
                            else:
                                await message.channel.send(f"ERR: Invalid third arguement. Must be a string, surrounded by double quotes.")
                        except Exception as e:
                            await message.channel.send(f"ERR: Missing valid third arguement. Must be a string, surrounded by double quotes.\nException: {e}")
                except Exception as e:
                    await message.channel.send(f"ERR: Missing valid second arguement. Must be numeric.\nException: {e}")
            # remove
            elif arguments[1] == "remove":
                try:
                    for courseID, courseName in canvasCourseDict.items():
                        arguments[2] = arguments[2].strip('"')
                        if arguments[2] == courseID or arguments[2] == courseName:
                            canvasCourseDict.pop(courseID)
                            if os.path.isfile('canvasCourseDict.txt'):
                                with open('canvasCourseDict.txt', 'w') as file:
                                    save = json.dumps(canvasCourseDict)
                                    file.write(save)
                                    file.close()
                            await message.channel.send("Successfully removed course.")
                            break
                        elif arguments[2] == "all":
                            canvasCourseDict.clear()
                            if os.path.isfile('canvasCourseDict.txt'):
                                with open('canvasCourseDict.txt', 'w') as file:
                                    save = json.dumps(canvasCourseDict)
                                    file.write(save)
                                    file.close()
                            await message.channel.send("Successfully removed all courses.")
                            break
                except Exception as e:
                    await message.channel.send(f"ERR: Missing valid second arguement. Must be 'all', the course's ID, or the course's name in double quotes.\nException: {e}")
        except Exception as e:
            await message.channel.send(f"ERR: Missing valid first argument. Must be 'add' or 'remove'.\nException: {e}")
    # discord clear channel
    elif arguments[0] == "!purge":
        try:
            async for message in message.channel.history(limit=None):
                await asyncio.sleep(0.75)
                await message.delete()
            await message.channel.send("Successfully purged channel.")
            await asyncio.sleep(3)
            async for message in message.channel.history(limit=None):
                await asyncio.sleep(0.75)
                await message.delete()
        except Exception as e:
            await message.channel.send(f"ERR: Unknown error.\nException: {e}")
    # complete
    elif arguments[0] == "!complete" or arguments[0] == "!c":
        try:
            if arguments[1].isnumeric():
                pass
            else:
                arguments[1] = arguments[1].strip('"')
            for assignment in courseInformation:
                #print(f"arguments[1]: {type(arguments[1])} | assignment: {type(assignment['id'])}")
                if arguments[1] == assignment['name'] or int(arguments[1]) == assignment['id']:
                    canvasCompletedAssignments.append(assignment['id'])
                    if os.path.isfile('canvasCompletedAssignments.txt'):
                        with open('canvasCompletedAssignments.txt', 'w') as file:
                            save = json.dumps(canvasCompletedAssignments)
                            file.write(save)
                            file.close()
                    await message.channel.send(f"Successfully set assignment {assignment['name']} as complete.")
                    break
                else:
                    pass
                    #await message.channel.send(f"ERR: Invalid first arguement. Must be the numeric ID for the assignment or assignment's name in double quotes.")
        except Exception as e:
            await message.channel.send(f"ERR: Missing valid first argument. Must be the numeric ID for the assignment or assignment's name in double quotes.\nException: {e}")
    # assign
    elif arguments[0] == "!assign":
        # assignment name ( find id with name in coureseInformation to remove from list )
        try:
            if arguments[1].isnumeric():
                pass
            else:
                arguments[1] = arguments[1].strip('"')
            for assignment in courseInformation:
                if arguments[1] in canvasCompletedAssignments or arguments[1] == assignment['name']:
                    canvasCompletedAssignments.remove(assignment['id'])
                    if os.path.isfile('canvasCompletedAssignments.txt'):
                        with open('canvasCompletedAssignments.txt', 'w') as file:
                            save = json.dumps(canvasCompletedAssignments)
                            file.write(save)
                            file.close()
                    await message.channel.send(f"Successfully re-assigned previously completed assignment {assignment['name']}.")
                    break
            if arguments[1] == "all":
                canvasCompletedAssignments.clear()
                if os.path.isfile('canvasCompletedAssignments.txt'):
                    with open('canvasCompletedAssignments.txt', 'w') as file:
                        save = json.dumps(canvasCompletedAssignments)
                        file.write(save)
                        file.close()
                await message.channel.send(f"Successfully re-assigned all previously completed assignments.")
        except Exception as e:
            await message.channel.send(f"ERR: Missing valid first arguement. Must be 'all', the numeric ID for the assignment, or assignment's name in double quotes.\nException: {e}")
    # help
    elif arguments[0] == "!help" or arguments[0] == "!h":
        await message.channel.send(f"```!get\n!course\n!purge\n!complete\n!assign\n!help```")

@tasks.loop(hours=24) # should do every 1 hour or so, but probably more like once a day
async def main():
    discordChannel = client.get_channel(discordChannelID)
    print("Main task loop starts...")
    await GetInformation()
          
# methods
async def GetInformation():
    discordChannel = client.get_channel(discordChannelID)
    print("Starting GetInformation function...")
    # clear for to prevent repeat courses
    if len(canvasCourseDict) == 0:
        print("There are no courses! Returning...")
        await discordChannel.send("There are no courses to get information for.")
        return
    currentDate = datetime.datetime.now()
    #print(f"currentDate: {currentDate}")
    isoFormattedCurrentDate = currentDate.strftime(iso8601Format)
    #print(f"formattedCurrentDate: {formattedCurrentDate}")
    aheadDate = currentDate + datetime.timedelta(weeks=1) # weeks=1
    isoFormattedAheadDate = aheadDate.strftime(iso8601Format)
    courseList.clear()
    courseInformation.clear()
    missedAssignments = 0
    # for each course id in list, check course things
    for courseID, courseName in canvasCourseDict.items():
        for topic in canvasTopicList:
            courseUrl = f'{canvasBaseUrl}/api/v1/courses/{courseID}/{topic}?per_page=100'
            response = requests.get(courseUrl, headers=canvasHeaders)
            #print(f"response: {response}\n\n\n")
            course = response.json()
            #print(f"course: {course}\n\n\n")
            if type(course) is not list:
                continue
            if not course:
                print(f"{courseName} has no {topic}, skipping...")
                continue
            course[0]['course_id'] = courseID
            courseList.append(course)
            print(f"{courseName}: Getting {topic}...")
            await asyncio.sleep(1)
    #print(f"{courseList}\n\n\n") # can print not display really long lists?
    # in assignment list, check if due date between today and next week
    for courseAssignment in courseList:
        for assignment in courseAssignment:
            #print(f"courseAssignment: {courseAssignment}\n\n\n")
            #print(f"assignment: {assignment}\n\n\n")
            if type(assignment) is not dict:
                #print("assignment is not a dictionary, skipping...")
                continue
            assignmentDueRaw = assignment.get("due_at")
            #print(f"assignmentDueRaw: {assignmentDueRaw}")
            if assignmentDueRaw == None:
                #print("assignmentDueRaw is None, skipping...")
                #print(f"{assignment}\n\n\n")
                continue
            #print(f"assignment: {assignment['name']}")
            assignmentDue = datetime.datetime.strptime(assignmentDueRaw, iso8601Format) - datetime.timedelta(days=1)
            # calc vars
            objectAheadDate = datetime.datetime.strptime(isoFormattedAheadDate, iso8601Format)
            objectCurrentDate = datetime.datetime.strptime(isoFormattedCurrentDate, iso8601Format)
            #print(f"due: {assignmentDue} | today: {objectCurrentDate} | ahead: {objectAheadDate}")
            if between(assignmentDue, objectCurrentDate, objectAheadDate):
                #print("assignment falls between today and next week, appending...")
                # determine assignment type
                try:
                    if assignment["is_quiz_assignment"]:
                        assignmentType = "QUIZ"
                    elif assignment["submission_types"][0] == "discussion_topic":
                        assignmentType = "DISCUSSION"
                    else:
                        assignmentType = "ASSIGNMENT"
                except:
                    print("Something is wrong with an assignment! Check Canvas and the bot's output to see what it is.")
                    missedAssignments += 1
                    continue
                # format assignmentDue
                assignmentDue = assignmentDue.strftime(dateFormat)
                courseInformation.append(
                    {
                        'name': assignment['name'],
                        'type': assignmentType,
                        'link': assignment['html_url'],
                        'course_id': assignment['course_id'],
                        'id': assignment['id'],
                        'due': assignmentDue
                    }
                )
    await DisplayInformation(courseInformation, missedAssignments)

async def DisplayInformation(courseInformation, missedAssignments):
    # for each thing in course info, display info
    print("Displaying information...")
    discordChannel = client.get_channel(discordChannelID)
    for courseID, courseName in canvasCourseDict.items():
        #print("Working on each course...")
        tempSend = ""
        tempTitle = f"# {courseName}\n"
        for assignment in courseInformation:
            #print("Working on each assignment...")
            #print(f"courseID: {courseID} | assignmentID: {assignment['id']}")
            if int(assignment['course_id']) == int(courseID): # matching course, display under send
                if assignment['id'] not in canvasCompletedAssignments:
                    tempSend += f"**{assignment['type']}: **{assignment['name']}: **Due {assignment['due']}**\n[Hyperlink]({assignment['link']}) ID: {assignment['id']}\n\n"
        if tempSend == "":
            tempSend += f"You're all done for this class!"
        tempSend = tempTitle + tempSend
        #print(tempSend)
        chunks = [tempSend[i:i+2000] for i in range(0, len(tempSend), 2000)]
        for chunk in chunks:
            await discordChannel.send(chunk)
    if missedAssignments > 0:
        await discordChannel.send(f"*~{missedAssignments} thing(s) could not be displayed.*")
    print("Displayed info!")

def between(number, lower, upper):
    return lower <= number <= upper

# more discord stuff
client.run(discordToken)