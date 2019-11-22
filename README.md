# Alarm Grotta
This project was designed to be a wrapper, it adds a new feature to the Alarm System I own at home.
Currently, it only has got a very basic way to manage the alarm status: using a dedicated Android/iOS app or by directly calling a special phone number.
My goal was to give the users at home a simple way to turn the alarm on/off: so why not using voice instead of an app?
The current Alarm System at home doesn't have an integrated Alexa Skill to turn on/off the alarm. 
I created it, and integrated it with a Node middleware that specifically interacts with the Alarm endpoint.


### About the Alexa Skill
A dedicated Alexa skill was created using Python language. It helps the user to schedule the alarm arming at home, so it can change the Alarm status at a preferred time. This way the user has got some time to leave the house with no rush. 
Using a simple voice command, the building will be automatically armed.
This skill will never be published to the Skill Store and was created and designed for family member use only. 

Concept: Using Amazon Echo Dot you can ask something like: 'Alexa, ask Alarm Grotta to turn on the alarm in 10 minutes' or 'Alexa, ask Alarm Grotta to turn off the alarm'.

### About the middleware
the Node script is just a simple bridge between the Alexa trigger command and the actual Alarm APIs.
This API was published in a dedicated server production environment using PM2 module.
When the AWS Lambda function is being triggered by the user's voice, it calls my API at '/alarm' route, specifying the preferred command (i.e. 'on' or 'off') and a delay in minutes (i.e. delay=5). 
After the specified delay, my API calls the actual Alarm API, changing the status to the preferred user status.

![Design Diagram](/other/diagram.jpg)

### Used Languages
- Nodejs
- Python
- Italian :pizza: