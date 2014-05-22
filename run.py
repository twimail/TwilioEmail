from flask import Flask, request, redirect, session
import twilio.twiml
from twilio.rest import TwilioRestClient
import datetime
import gmail_test
import os

# Twilio Account. Replace the following variables value with your own account.
account_sid = "ACb0d3304b2db2d21fc19341c13139cdfe" 
auth_token  = "8729ec847e9a78b227e164fe0a9e8f45" 
twilio_no = "+15675234076"

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)
 
callers = {}
contacts_dict = {}
client = TwilioRestClient(account_sid, auth_token)
username = None
password = None
flag = True
reply = ""
summary_emails = []
display_counter = 0
counter = 0
menu = "\nMain Menu\nPlease reply with following keywords\n1 For Summary = summary\n2 To Send Mail = send; <email ids separated by ,>; <subject>; <body> \n3 To Search = search:<email id to search> <text>\n\nTo read menu anytime reply menu"

# send_sms function to send the sms to the user
def send_sms(number,msg):
    message = client.messages.create(body=msg,
    to = number,
    from_= twilio_no)

# Function to write the contact dictionary into file
def write_dict_file():    
    contact_file = open("contact_dictionary.txt", 'w')
    for key,value in contacts_dict.iteritems():        
        contact_file.write(str(key)+" "+value[0]+" "+value[1]+" "+str(value[2])+" "+str(value[3])+" "+str(value[4])+"\n")
    contact_file.close()

#Function to load contact dictionary into main memory
def contacts_dict_load():
    contact_file = open("contact_dictionary.txt", 'r')
    while True:
        line = contact_file.readline()
        if len(line)==0:
            break
        t = line.split()
        contacts_dict[t[0]]=[t[1],t[2],int(t[3]),int(t[4]),int(t[5])]
    contact_file.close()

#Function to display summary emails
def display_mail(i):
        display_message = "\n"
        if len(summary_emails) == 0:
            display_message = "No new important emails at this time." 
            return display_message, 1
        for x in range(i,len(summary_emails)):
            email = summary_emails[i]
            try:
                message = "\n"+str(i+1)+" "+ email[0] + "\nSubject: "+ email[1]
                if len(email[2])<=(160-len(message)):
                    message += "\n" +email[2]
                print message
                if len(display_message+message)>=1500:
                    break
                else:
                    display_message += message
                i=i+1
            except:
                summary_emails.pop(i)
                continue
        if(len(summary_emails)>i):
                    display_message += "\nReply 'more' to read more emails\nReply 'readi' to read 'i'th mail in summary" 
        return display_message, i


@app.route("/", methods=['GET', 'POST'])
def interface():
    """Respond with the number of text messages sent between two parties."""

    global username
    global password
    global flag
    global display_counter
    global summary_emails
    global counter
    from_number = request.values.get('From')
    user_counter = 'counter'+str(from_number)
    counter = session.get(user_counter, 0)
    message = " "
    try:
        f = open("contact_dictionary.txt",'r')
        f.close()
    except:
        write_dict_file()
    contacts_dict_load()
    username = contacts_dict[from_number][0]
    password = contacts_dict[from_number][1]
    # increment the counter
    counter += 1
 
    # Save the new counter value in the session
    session[user_counter] = counter
 
    
    if from_number in callers:
        name = callers[from_number]
    else:
        name = "Monkey"
    
    reply = request.values.get('Body')
    if flag==False:
        reply = 'gmail'
    print reply

    # 'gmail' command
    if reply.lower()=='gmail':
        if contacts_dict.get(from_number)!= None:
            counter = 3
            message = menu
        else:
            message = "".join("\n\nEnter username and password\nl:username password")
            counter = 1
            username = ""
            password = ""
            session[user_counter] = 1
            flag = True
            
    # 'more' command
    elif reply.lower()=='more':
        message, display_counter = display_mail(display_counter)

    # 'read' command    
    elif 'read' in reply.lower():
        x = int(reply.lower()[4:])
        email = summary_emails[x-1]
        message = "\n"+ email[0] + "\nSubject: "+ email[1] + "\n"
        message += email[2][:1600-len(message)]
        
    # 'summary' command    
    elif reply.lower() == "summary":
         userlist = contacts_dict[from_number]
         y = userlist[2]
         m = userlist[3]
         d = userlist[4]
         summary_emails = gmail_test.get_summary(username,password, from_number, y, m, d)
         message, display_counter = display_mail(0)

    # 'send' command to send email     
    elif 'send;' in reply.lower():
         send_request = reply.split(';')
         to = send_request[1].split(',')
         subject = send_request[2]
         body = send_request[3]
         if len(to)==0:
             message = "Invalid Syntax. To Send Mail = send; <email ids separated by ','>; <subject>; <body>\n Example = send;suel@poly.edu,sj1532@nyu.edu;Hello;Hello Sir How are you?"
         success = gmail_test.send_email(username,password,to,body,subject)
         if success == True:
             message = "Email Sent Successfully.\n Reply 'menu' for Main Menu"
         else:
             message = "Email sending failed due to server error"

    # 'search' command        
    elif 'search:' in reply.lower():
         search_request = reply[7:]
         query=[]
         email= ""
         text = ""
         if len(search_request)==0:
             message="Invalid Syntax.\nCorrect syntax is = search:<email id> <text> \nExample = search:suel@poly.edu exam topics"
         else:
             query = search_request.split(' ',1)
             email = query[0]
             if len(query)>1:
                  text = query[1].split()
             else:
                  text = ""
         summary_emails = []
         summary_emails = gmail_test.search_user_emails(username, password, email, text)
         if summary_emails == False:
             message = "Login Failed"
         else:
             message, display_counter = display_mail(0)

    # 'menu' command         
    elif reply.lower() == 'menu':
         message = menu

    # status check 
    elif counter==2:
        login_msg = reply
        check = login_msg[:2]
        if check != "l:":
            message= "\n\nWrong Format\nCorrect format is\nl:username password"
        else:
            login_msg = login_msg [2:]
            l = login_msg.split(' ',1)
            username = l[0]
            password = l[1]
            g = gmail_test.login(username, password)
            if g==None:
                message = "".join("\n\nIncorrect Username/Password")
                flag = False
            else:
                now = datetime.datetime.now()
                contacts_dict[from_number] = [username,password,now.year,now.month,now.day-1]
                print contacts_dict
                summary_emails = gmail_test.getImp(username, password, from_number)
                message, display_counter = display_mail(0)
                send_sms(from_number,message)
                print message
                send_sms(from_number,"\n\nAnalysis Started\n\nWe will notify you on completion.")
                gmail_test.start_analysis(username, password, from_number)
                send_sms(from_number,"\n\nAnalysis Completed")
                counter += 1
                session[user_counter]+=1
                message = menu
    # Default value
    else:
         message = "Invalid keyword. Reply 'menu'for Main Menu"
         
    write_dict_file()
    resp = twilio.twiml.Response()
    if counter>=2:
        send_sms(from_number," "+message)
    else:
        resp.sms(message)
     
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)

