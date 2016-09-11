import time;
import urllib2;
import os;
import sys;
import json;
from slackclient import SlackClient;

# Let's do some Slack setup stuff first.
BOT_NAME = 'worfbot'

# Worfbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants (the Bot's ID for the listener, and the command trigger).
AT_BOT = ("<@" + BOT_ID + ">")
COMMAND = ("change")

# Make sure we can find the bot in-channel. Invite it if you hit an error.
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)

# THE GUTS OF IT:  Do the thing when the bot is called upon.
def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Say what?  I just change channel topics when I'm told. Use the *" + COMMAND + \
               "* command and I might be a bit more friendly."
    if not command.startswith(COMMAND):
	slack_client.api_call("chat.postMessage", channel=channel,
                     text=("Sorry, I only respond to *" + COMMAND + "*. Try that."), as_user=True)
    else:
	# Let's dance.
	slack_client.api_call("chat.postMessage", channel=channel,
                     text="Hi! I'll update the channel topic with the on-duty specialist info.", as_user=True)        
	# Detect current time
	currentTime = (time.strftime("%H:%M"))
	# Assign appropriate region code based on current time
	if (currentTime >= str("09:00") and currentTime <= str("16:59")):
	    regionCode = "NA"
	elif (currentTime >= str("17:00") and currentTime <= str("23:59")):
	    regionCode = "APAC"
	elif (currentTime >= str("00:00") and currentTime <= str("08:59")):
	    regionCode = "DUB"
	else:
	    regionCode = "Unknown"
	# Read in the specialists.txt file and convert to a string array. 
	file = urllib2.urlopen('http://pastebin.com/raw/NJRPMV4m')
	data=file.read().decode('utf-8')
	data = data.replace('\r\n','|')
	tzSpecialists = data.split('|')
	# Run through source file, and exit with agent detail if we find an element
	# where "regionCode" is a substring. Exit w/ error if not.
	# Lastly, print out the channel topic.
	for i, elem in enumerate(tzSpecialists):
	    if regionCode in elem:
		response="On-duty specialists: " + tzSpecialists[i].replace(regionCode + ",","")
   		slack_client.api_call("channels.setTopic", channel=channel, topic=response)
		break
	if regionCode not in elem:    
	    slack_client.api_call("chat.postMessage", channel=channel,
                     text=response, as_user=True)


# Listen for someone to mention the bot.
def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
	    # print(output_list)
            if output and u'text' in output and AT_BOT in output[u'text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
		print(output)
    return None, None

# Make sure we're listening to the channel
if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Worfbot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:  
		handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



