import gmail
import sys
import traceback
import datetime
import operator
import smtplib
from email.mime.text import MIMEText

READ_EMAILS = 0
UNREAD_EMAILS = 1
SPAM_EMAILS = 2
ATTACHMENT_EMAILS = 3
SENT_EMAILS = 4

year = 0
month = 0
date = 0

email_id = "twimail.api"
password = "twimail.api1"

def login(uName, uPass):
    try:
        return gmail.login(uName , uPass)
    except:
        return None

user_contact_dict = {}

def load_dict(from_number):
    dict_file = open("contacts" + str(from_number)+ ".txt" , 'r')    
    for line in dict_file:
        values = []
        details = line.split('|')        
        mId = details[0]        
        details = details[1:len(details)]
        details[0] = float(details[0])
        details[1] = float(details[1])
        details[2] = float(details[2])
        details[3] = float(details[3])
        details[4] = float(details[4].replace('\n',""))        
        for value in details:
            values.append(value)
        user_contact_dict[mId] = values    

def insert_dict(key, value):
    try:
        pre_value = user_contact_dict[key]                
        post_value = [x + y for x,y in zip(pre_value, value)]        
        user_contact_dict[key] = post_value
    except KeyError:
        user_contact_dict[key] = value


def format_email(mail_id):
    mail_id = mail_id.strip()
    mail = mail_id.split('<')
    if len(mail) > 1:
        mail = mail[1].split('>')
    mail = mail[0]
    return mail

def format_body(body):
    body = body.strip()
    body = body.replace('\n', "  ")
    return body

def calculate_score(email_id):
    values = user_contact_dict[format_email(email_id)]
    score = values[READ_EMAILS] * 10 - values[UNREAD_EMAILS] * 5 - values[SPAM_EMAILS] * 100 + values[ATTACHMENT_EMAILS] * 15 + values[SENT_EMAILS] * 25    
    return score

        
##
def has_attachment(email):
    if len(email.attachments) != 0:
        return True
    else:
        return False
##
def scoring_sent(email):
    try:
        sent_ids = email.to.split(',')
        if len(sent_ids) != 0:
            for ids in sent_ids:
                ids = format_email(ids)                
                value = [0,0,0,0,0]                            
                value[SENT_EMAILS] = 1.0 / len(sent_ids)
                insert_dict(ids, value)
        cc_ids = email.cc
        if cc_ids != None:
            cc_ids = cc_ids.split(',')
            if len(cc_ids) != 0:
                for eids in cc_ids:
                    eids = format_email(eids)
                    value = [0,0,0,0,0]
                    value[SENT_EMAILS] = 0.5 / len(cc_ids)
                    insert_dict(eids , value)                    
        else:
            return        
    except:
        print "scoring sent"
        traceback.print_exc()
##
def to_ids_check(email):
    try:
        to_ids = email.to.split(',')        
        if len(to_ids) != 0:            
            for ids in to_ids:
                ids = format_email(ids)
                if email_id in ids:
                    return [True, 1 / len(to_ids)]
            return [False, 0]        
            
    except:
        print "to ids check"
        traceback.print_exc()
##
def cc_ids_check(email):
    try:
        cc_ids = email.cc
        if cc_ids != None:
            cc_ids = cc_ids.split(',')            
            return 0.5 / len(cc_ids)
        else:
            return 0
    except:
        print "cc ids check"
        traceback.print_exc()
##
def check_email_inbox(email):
    try:
        l = to_ids_check(email)        
        if l[0] == True:            
            return l[1]
        else:
            return cc_ids_check(email)
    except:
        print "check mail"
        traceback.print_exc()            
##        
def scoring_inbox(email):    
    where = check_email_inbox(email)
    mail = format_email(email.fr)                
    ranking_list = [0.0,0.0,0.0,0.0,0.0]
    if has_attachment(email):
        ranking_list[ATTACHMENT_EMAILS]+=1.0
    if email.is_read():
        ranking_list[READ_EMAILS]+=where + 0.5
    else:
        ranking_list[UNREAD_EMAILS]+= where
    insert_dict(mail , ranking_list)
##    
##
def scoring_spam(email):    
    mail = format_email(email.fr)
    ranking_list = [0.0,0.0,0.0,0.0,0.0]
    ranking_list[SPAM_EMAILS]+=1.0
    insert_dict(mail , ranking_list)
##
##        

def inbox(g):
    inbox_mails = g.inbox().mail()
    for email in inbox_mails:
        try:        
            email.fetch()
            scoring_inbox(email)                    
        except UnicodeDecodeError:
            continue
        except:
            print "reading mails inbox"
            traceback.print_exc()
            continue

##

def spam(g) :
    spam_mails = g.spam().mail()
    for email in spam_mails:
        try:        
            email.fetch()
            scoring_spam(email)                    
        except UnicodeDecodeError:
            continue
        except:
            print "reading mails spam"
            traceback.print_exc()
            continue
##    
##

def sent(g):
    sent_mails = g.sent_mail().mail()
    for email in sent_mails:
        try:            
            email.fetch()        
            scoring_sent(email)                    
        except UnicodeDecodeError:
            continue
        except:
            print "reading mails spam"
            traceback.print_exc()
            continue
    
def write_dict_file(from_number):    
    contact_file = open("contacts"+ str(from_number)+".txt", 'w')
    for key,value in user_contact_dict.iteritems():        
        contact_file.write(key + "|" + str(value[READ_EMAILS])+ "|" +
                           str(value[UNREAD_EMAILS])+ "|" + str(value[SPAM_EMAILS])+ "|" + str(value[ATTACHMENT_EMAILS])+ "|" + str(value[SENT_EMAILS]) + "\n")
    user_contact_dict.clear()
    contact_file.close()

def getImp(uName, uPass, from_number):    
    g = login(uName, uPass)
    message = []
    imp_mails = g.important().mail(unread=True)    

    for email in imp_mails:
        try:        
            email.fetch()
            email_id = format_email(email.fr)
            message.append([email_id, email.subject , format_body(email.body)])
        except:            
            continue
    message.reverse()
    g.logout()
    return message
#print getImp(email_id, password, +4072749173)

def start_analysis(uName, uPass, from_number):
    g = login(uName, uPass)
    if g != None:
        inbox(g)
        sent(g)
        spam(g)
        write_dict_file(from_number)

def send_summary(inbox_mails, from_number):
    score = []
    negative_list = ["rewards" , "offer", "clearence", "sale", "discount"]
    positive_list = ["track order" , "shipped"]
    for email in inbox_mails:        
        try:            
            eScore = calculate_score(email.fr)
            if any(word in email.subject.lower() for word in negative_list):
                if eScore < 50:
                    continue
            if any(word in email.subject.lower() for word in positive_list):
                score.append([eScore, [format_email(email.fr) ,email.subject, format_body(email.body)]])
                email.read()
                continue
            if eScore > 0:
                score.append([eScore, [format_email(email.fr) ,email.subject, format_body(email.body)]])            
            email.read()
        except:
            print "Caught Exception in scoring emails"
            traceback.print_exc()
            continue
    score = sorted(score , key=operator.itemgetter(0), reverse=True)
    message = []
    for entry in score:
        message.append(entry[1])
    message.reverse()
    write_dict_file(from_number)
    return message
        
def get_summary(uName, uPass, from_number, mYear, mMonth, mDate):
    year = mYear
    month = mMonth
    date = mDate
    i = datetime.datetime.now()
    unread_mails = []
    g = login(uName, uPass)
    load_dict(from_number)
    
    if i.year == year and i.day == date and i.month == month:
        unread_mails = g.inbox().mail(unread=True, after = datetime.date(year, month, date))
        print unread_mails
        for email in unread_mails:
            try:
                email.fetch()
                scoring_inbox(email)
            except:
                continue        
        return send_summary(unread_mails, from_number)
        

    if g == None:
        print "Login failed"
        return
    
    inbox_mails = g.inbox().mail(after = datetime.date(year, month, date))    
    for email in inbox_mails:
        try:
            email.fetch()
            if not email.is_read():
                unread_mails.append(email)
            scoring_inbox(email)
        except:
            continue

    sent_mails = g.sent_mail().mail(after = datetime.date(year, month, date))
    for email in sent_mails:
        try:
            email.fetch()
            scoring_sent(email)
        except:
            continue
        
    spam_mails = g.spam().mail(after = datetime.date(year, month, date))
    for email in spam_mails:
        try:            
            email.fetch()
            scoring_spam(email)
        except:
            continue

    return send_summary(unread_mails, from_number)

def send_email(uName, uPass, to_mail, mail_body = "", subject = ""):
    message = MIMEText(mail_body)    
    message['From'] = uName+ "@gmail.com"
    message['To'] = " , ".join(to_mail)
    message['Subject'] = subject
    
    # The actual mail send
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(uName,uPass)
        server.sendmail(uName+ "@gmail.com", to_mail, message.as_string())
        server.quit()
        return True
    except:
        return False
        
def search_user_emails(uName, uPass, from_mail, text_search):
    g = login(uName, uPass)

    if g == None:
        print "Trouble logging in"
        return False

    stop_word = ["is" , "and" , "it" , "for" , "a" , "an" , "the" , "in", "on" , "to" , "or", "by" , "you", "me" , "i" , "then", "am" , "are"]

    for word in text_search:
        if word in stop_word:
            text_search.remove(word)

    inbox_mails = g.inbox().mail(sender=from_mail)    

    message = []
    if len(text_search) == 0:
        flag = False
    else:
        flag = True
            
    for email in inbox_mails:
        try:
            email.fetch()
            print email.subject
            if any(word.lower() in email.subject.lower() for word in text_search) and flag == True:
                message.append([format_email(email.fr), email.subject, format_body(email.body)])
                print "Found in subject"                
            elif any(word.lower() in email.body.lower() for word in text_search) and flag == True:
                message.append([format_email(email.fr), email.subject, format_body(email.body)])
                print "Found in body"
            elif flag == False:
                message.append([format_email(email.fr), email.subject, format_body(email.body)])
        except:        
            print "Caught Exception"
            continue
    ##        traceback.print_exc()
    message.reverse()
    g.logout()
    return message
    

##start_analysis(email_id, password, +6313593010)
##get_summary(email_id, password, +6313593010, 2014, 5, 19)
##send_email(email_id, password, ["aditya841@gmail.com"], "Testing mail feature of python. Looks cool", " ")
##search_user_emails(email_id, password, "online@e.nymag.com", ["Summer Must-Have"]) 
    
