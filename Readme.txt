How To Run:

1.	Register for a Twilio account
2.	Install virtualenv
3.	Install and setup Flask.
4.	Install ngrok
5.	Execute run.py inside virtualenv to start the program
6.	Start ngrok on port 5000
7.	Set the url returned by ngrok as the reply url of your Twilio number
8.	Send messages to your Twilio email and enjoy!

Message Syntax:

Please reply with following keywords
1.      For Summary = summary
2.      To Send Mail = send; <email ids separated by ,>; <subject>; <body> 
3.      To Search = search:<email id to search> <text>

To read menu anytime reply menu

