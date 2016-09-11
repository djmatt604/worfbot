# worfbot
A small Python script that calls on a bot user to change the topic of a channel.

Things the script does:

- Sets up a listener for mentions of a bot user with a trigger word.

- When a trigger word is used, the bot fetches a data file and parses its content.

- If the right data is present, it's used to determine who is working based on
  some timezone rules and returns a string with those people in it.

- The returned string is then added to some other text, and the end result is
  sent back to the Slack channel to change the topic with an API call.
