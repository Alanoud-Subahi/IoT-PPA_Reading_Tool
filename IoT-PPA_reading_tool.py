import nltk
import urllib2
from bs4 import BeautifulSoup
from nltk import word_tokenize
import nltk.data
import csv
import codecs
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix, classification_report
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re
from sklearn.cross_validation import KFold, cross_val_score
from time import time
#****************************************************************************************************************#

# Global variables:

Location_KeyWords = ['street address', 'your locations', 'location name', 'location data', 'time zone setting', 'your location',
                     'billing address', 'mailing address', 'location Information', 'your actual location',
                     'location-based', 'locationbased', 'location based', 'enable location-based', 'enable locationbased',
                     'enable location based', 'exact location', 'your address', 'device location', 'location details',
                     'home address', 'the location', 'geo-location', 'geolocation', 'geo location', 'delivery address',
                     'longitude and latitude', 'time zone settings', 'geographic location', 'shipping address', 'location names',
                     'postal address', 'physical address', 'physical location', 'location gps', 'gps location',
                     'geographic location', 'location setting', 'street', 'postal', 'locations', 'location', 'address','geo','gps']

Login_keywords = ['sign-in','login', 'log in', 'sign into','log-in', 'signing into', 'login information', 'log in information',
                  'log in id', 'login id', 'account credentials','log-in credentials','login credentials','log-on credentials','log on credentials',
                  'credentials','credential','sign in', 'signin']

Password_keywords= ['password details', 'your password', 'the password', 'account password', 'account credentials',
                    'login password', 'login credentials', 'log-on credentials', 'log-in credentials', 'log on credentials',
                    'logon credentials', 'password', 'passwords']

Email_KeyWords = ['e-mail address', 'email address', 'your email', 'your e-mail', 'e-mail addresses', 'email addresses',
                  'e-mail', 'email', 'e-mails', 'emails']

UserName_keywords = ['your name', 'user name', 'user id', 'user-id', 'name-id', 'name id', 'last name', 'first name',
                     'full name', 'user names', 'user-name', 'user information', 'users information', 'user details', 'users details',
                    'users information', 'username', 'userid', 'nameid', 'nicknames', 'usernames', 'names', 'name']

Device_keywords = ['ip address', 'ip addresses','your ip address','your full ip address','full ip address','mac address',
                   'device configuration details', 'device name', 'device id', 'id number', 'operating system', 'device model',
                   'serial number', 'software version', 'serial numbers', 'device identifier', 'device number', 'hardware and software version',
                   'internet protocol ip addresses','model name', 'internet protocol ip address', 'firmware version',
                   'device manufacturer details','unique device identifiers', 'device models', 'device type', 'firmware information',
                   'internet protocol address', 'internet protocol', 'device information', 'device details', 'ip', 'mac']

Cookie_keywords = ['third-part cookies', 'third party cookies', 'thirdparty cookies', 'cookies do not', 'cookies will not',
                   'cookie to store','cookies', 'cookie']
IoT_PPA_FeaturesVectors= []
# Open csv file, read it, and save it in a list

with open("/root/Downloads/textMining_python_application/collect_keywords.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    Collect_Verbs= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/wrong-email_keywords.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    wrong_email= [e[0].strip() for e in reader if e]

with open("/root/Downloads/textMining_python_application/Wrong_location.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    wrongLocation_keywords= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/wrong_names.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    wrongNames_keywords= [e[0].strip()for e in reader if e]
with open("/root/Downloads/textMining_python_application/wrong_credentials.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    wrongCredentials_keywords= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/negative_keywords.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    negative_keywords= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/wrong-verbs_keywords.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    wrongVerb_keywords= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/share_keywords.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    share_keywords= [e[0].strip()for e in reader if e]

with open("/root/Downloads/textMining_python_application/thirdParty.csv", "r") as f:
    reader = csv.reader(codecs.EncodedFile(f, 'utf8', 'utf_8_sig'))
    thirdParty_keywords= [e[0].strip()for e in reader if e]

#****************************************************************************************************************#

# Star pre process the IoT PPA:

# 1 select which IoT url page we want to extract its page

def extract_HTML(ans):
    html_page = read_url(ans)
    return html_page

    tp_link = 'https://www.tp-link.com/uk/about-us/privacy/'
    belkin_netcam = 'https://www.belkin.com/us/privacypolicy/'
    lifx = 'https://www.lifx.com/pages/privacy-policy/'
    hive = 'https://www.hivehome.com/privacy'
    philips = 'https://www2.meethue.com/en-gb/support/privacy-notice'
    awair = 'https://getawair.com/pages/legal#privacy'
    smartThings = 'http://www.smartthings.com/gb/privacy'
    nest = 'http://nest.com/uk/legal/privacy-statement-for-nest-products-and-services/'
    Elgato = 'https://www.elgato.com/en/data-protection'
    Ikea = ' https://www.ikea.com/gb/en/customer-service/privacy-policy/'
    Eufy = 'https://www.eufylife.com/uk/privacy-policy'
    Nanoleaf = 'https://nanoleaf.me/en/privacy/'
    Osram = 'https://www.osram.com/cb/services/privacy-policy/index.jsp'
    Sengled = 'https://eu.sengled.com/en/about-us/privacy-policy/index.html'
    Xiaomi = 'https://privacy.mi.com/all/en_GB/'
    Lohas = 'https://www.lohas-led.com/art/privacy-policy-a0040.html'
    Devolo = 'https://www.devolo.co.uk/support/data-privacy '
    Arlo = 'https://www.arlo.com/en-us/about/privacy-policy/'
    Ring = 'https://en-uk.ring.com/pages/privacy-notice'
    Swann = 'https://www.swann.com/uk/company/privacy-policy'
    DLink = 'https://eu.dlink.com/uk/en/privacy'
    Neos = 'https://shop.neos.co.uk/pages/privacy-policy'
    Logi = 'https://www.logitech.com/en-gb/legal/web-privacy-policy.html'
    Ezviz = 'https://www.ezvizlife.com/uk/legal/privacy-policy '
    Netatmo = 'https://view.netatmo.com/uk/legals/app?gsc=true&goto=privacy'
    Blink ='https://blinkforhome.co.uk/pages/privacy-policy'
    Canary = 'https://canary.is/legal/privacy-policy/'
    Somfy = 'https://www.somfy.co.uk/privacy-policy '

###################################################################################################################
# 2- read the url page
def read_url(url):
    req = urllib2.Request(url,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
                                                 ' Chrome/41.0.2228.0 Safari/537.36'})
    response = urllib2.urlopen(req)
    the_page = response.read()

    return the_page

# 4- this function is responsible for making the text ready for extract the features.
def data_Preprocessing(PPA_htmlBody):
    PPAtexts = []

    #**** first step: remove all the tags and script and extract only the text **************

    soup = BeautifulSoup(PPA_htmlBody, "lxml")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
        # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    PPAtexts.append(text)
    # convert to string
    PPAtexts_string= ''.join(PPAtexts)
    PPAtexts_string = PPAtexts_string.replace('?"', '? "').replace('!"', '! "').replace('."', '. "')

    #**** second step: split the string into sentences and lowe case them *******************

    extra_abbv = ['inc', 'e.g', 'i.e', 'i.e.', 'e.g.']
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    tokenizer._params.abbrev_types.update(extra_abbv)
    PPA_sents = tokenizer.tokenize(PPAtexts_string)
    lowercase_sents = [w.lower() for w in PPA_sents]

    # remove encode letter e.g. 'u', ex009
    encoded_text = []
    for s in lowercase_sents:
        line = " " + s.encode("ascii", "ignore")
        encoded_text.append(line)

    #**** third step tokenize each sentence in its words
    PPA_wordtokenized= []
    for i in encoded_text:           #PPA_removeStopwords_splitsentence:
        word = word_tokenize(i)
        PPA_wordtokenized.append(word)
    # **** fifth step remove the punctuation
    removePunctuation = remove_punctuation(PPA_wordtokenized)
    return removePunctuation

# 5- remove any punctuations
def remove_punctuation(document):
    punctuation = re.compile(r"[-()\"\'\[\]#/@:<>{}&`+=~0-9|;.!?,]")
    clear_list = []
    post_punctuation = []
    for sent in document:
        temp = []
        for word in sent:
            words =  punctuation.sub("",word)
            if len(words)>0:
                temp.append(words)
        post_punctuation.append(temp)
        # I add this inorder to get rid of the \\n symbole from the text.
        # I convert the list to string then remove the \n then return it back to list again
    for line in post_punctuation:
        string = ''
        string += ','.join(line)
        new_line = string.replace('\\n', '')
        list_text = new_line.split(',')
        clear_list.append(list_text)
        # to remove the empty items
    clearlist = [str for str in clear_list if str]

    return clearlist

# 3- call and combine all the functions through this function
def IoT_PPA_compliance (ans):
    text = []
    try:
        PPA_html = extract_HTML(ans)
    except urllib2.URLError as e:
        print e.reason
        print("Something bad happened")

    else:

        Processed_text = data_Preprocessing(PPA_html)

    for x in Processed_text:
        p = TreebankWordDetokenizer().detokenize(x)
        text.append(p)
    return text  # here the IoT PPA is list of sentences

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# The following functions for feature extraction purposes

# This function check the worng words within the sentence and delete it, then return the new sentence
def check_wrongWords(sent, wrong_words_list): # here i can change to accept sent and check_sensitive (if it's email, location, ...etc)
    new_text = ''
    for rong in wrong_words_list:
        new_text = sent
        if rong in new_text:
            new_text = sent.replace(rong, '')
            sent = ' '.join(new_text.split())
    return new_text

# This function check if the collect list has any type of the 10 conditions
def check_list(collect_location_sent, check_num):
    negativeWordList = []
    case1_list = []  # third + wrong-v + share
    case2_list = []  # cookie + wrong-v + share
    case3_list = []  # share + wrong-v
    case4_list = []  # third + wrong-v
    case5_list = []  # cookie + wrong-v
    thirdParty = []
    shareParty = []
    wrongVerb = []
    cookie = []
    if check_num == '1':
        for sent in collect_location_sent:
            for word in negative_keywords:
                k = re.compile("\\b%s\\b" % word, re.I)
                y = k.search(sent)
                if y != None:
                    negativeWordList.append(sent)

        for key in negativeWordList:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return negativeWordList, collect_location_sent

    elif check_num =='2':

        for sent in collect_location_sent:
            if (any(third in sent for third in thirdParty_keywords) and any(wrong_v in sent for wrong_v in wrongVerb_keywords) and any(share in sent for share in share_keywords)):
                case1_list.append(sent)

        if case1_list > 0:
            for key in case1_list:
                for item in collect_location_sent[:]:
                    if key == item:
                        collect_location_sent.remove(item)
        return case1_list, collect_location_sent

    elif check_num =='3':
        for sent in collect_location_sent:
            if (any(cookie_word in sent for cookie_word in Cookie_keywords) and any(wrong_v in sent for wrong_v in wrongVerb_keywords) and any(share in sent for share in share_keywords)):
                case2_list.append(sent)
        for key in case2_list:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return case2_list, collect_location_sent

    elif check_num =='4':
        for sent in collect_location_sent:
            if (any(wrong_v in sent for wrong_v in wrongVerb_keywords) and any(share in sent for share in share_keywords)):
                case3_list.append(sent)
        for key in case3_list:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return case3_list, collect_location_sent

    elif check_num =='5':
        for sent in collect_location_sent:
            if (any(wrong_v in sent for wrong_v in wrongVerb_keywords) and any(
                    third in sent for third in thirdParty_keywords)):
                case4_list.append(sent)
        for key in case4_list:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return case4_list, collect_location_sent

    elif check_num =='6':
        for sent in collect_location_sent:
            if (any(wrong_v in sent for wrong_v in wrongVerb_keywords) and any(
                    cookie_word in sent for cookie_word in Cookie_keywords)):
                case5_list.append(sent)

        for key in case5_list:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return case5_list, collect_location_sent

    elif check_num =='7':
        for sent in collect_location_sent:
            for word in thirdParty_keywords:
                k = re.compile("\\b%s\\b" % word, re.I)
                y = k.search(sent)
                if y != None:
                    thirdParty.append(sent)

        for key in thirdParty:
            for item in collect_location_sent[:]:
                if key == item:
                   collect_location_sent.remove(item)
        return thirdParty, collect_location_sent

    elif check_num == '8':
        for sent in collect_location_sent:
            for word in share_keywords:
                k = re.compile("\\b%s\\b" % word, re.I)
                y = k.search(sent)
                if y != None:
                    shareParty.append(sent)

        for key in shareParty:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return shareParty, collect_location_sent

    elif check_num == '9':
        for sent in collect_location_sent:
            for word in wrongVerb_keywords:
                k = re.compile("\\b%s\\b" % word, re.I)
                y = k.search(sent)
                if y != None:
                    wrongVerb.append(sent)

        for key in wrongVerb:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return wrongVerb, collect_location_sent

    elif check_num == '10':
        for sent in collect_location_sent:
            for word in Cookie_keywords:
                k = re.compile("\\b%s\\b" % word, re.I)
                y = k.search(sent)
                if y != None:
                    cookie.append(sent)

        for key in cookie:
            for item in collect_location_sent[:]:
                if key == item:
                    collect_location_sent.remove(item)
        return cookie, collect_location_sent

# This function check if the collect list has any features.
def collect_feature(sensitivesentence, feature_list):
    cv_word = ""
    sv_word = ""
    feature = []
    for cv in Collect_Verbs:
        k = re.compile("\\b%s\\b" % cv, re.I)
        y = k.search(sensitivesentence)
        if y != None:
            cv_word = cv
            break
    for sv in feature_list:
        k = re.compile("\\b%s\\b" % sv, re.I)
        y = k.search(sensitivesentence)
        if y != None:
            sv_word = sv
            break
    if (cv_word != ""  and sv_word != ""):
        feature = cv_word + ' ' + sv_word
        return feature

# This function check if any of the specific conditions collect features by apply the rules for each one
def check_features (sent, check_num, feature_list):

    if check_num == '1':
        neg_indices = []
        partitions = []
        for neg_word in negative_keywords:
            # check if the negative keyword is in the sentence.
            k = re.compile("\\b%s\\b" % neg_word, re.I)
            y = k.search(sent)
            if y != None: # this mean we find negative word
                neg_index = 0
                while neg_index < len(sent): # if so get the negative word index
                    neg_index = sent.find(neg_word, neg_index)
                    if neg_index == -1:
                        break
                    neg_indices.append(neg_index)
                    neg_index += 1
 # we stor all the indeices of the negative words and sort it out
        neg_indices.sort()
        y = 0
        for x in range(len(neg_indices)): # we loop though the list of indices to split the sentence in each negative word
            if len(partitions) < 1 and len(neg_indices)- 1 == 0 :       # we add the split sentence in another list called partitions
                                        # <1 mean we are in the first element of the partition list
                partitions.append(sent[:neg_indices[x]])# we store the first index of the list to split the second sentence
                y = neg_indices[x]                      # we are in the second element of the partitions
                part2 = sent[y:]                        # check if the second index could be the last one
                partitions.append(part2)
            elif len(partitions) < 1 and len(neg_indices)-1 > 0:
                partitions.append(sent[:neg_indices[x]])
                y = neg_indices[x]
            # if we in the last index this mean we need to do two splits at the same time
            elif x == len(neg_indices) - 1:
                part = sent[y:neg_indices[x]]
                partitions.append(part)
                y = neg_indices[x] # save the last index to split the sentence untill the end
                part2 = sent[y:]
                partitions.append(part2)
            else: # we are not at the last index
                part = sent[y:neg_indices[x]]
                partitions.append(part)
                y = neg_indices[x]


        feature_selection = []
        # we loop through each partition to check if there is any cv and sw words
        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""

            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if location in partitions[part]:
                    sensitive_word = location
                    break
            # we only check the first partition has cv and sw, that mean we don't care about the orders of the cv and the sw
            if part == 0 :
                if (collect_word != "" and sensitive_word != ""):
                    feature = collect_word + ' ' + sensitive_word
                    feature_selection.append(feature)
            else:
                pass

        return feature_selection

    if check_num =='2':
        wrong_v_indices = []
        thirdParty_indices = []
        shareParty_indices = []
        partitions = []
        # to get all indices of the wrong verb in the sentence
        for rong_word in wrongVerb_keywords:
            k = re.compile("\\b%s\\b" % rong_word, re.I)
            y = k.search(sent)
            if y != None:
            #if rong_word in sent:
                wv_index=0
                while wv_index < len(sent):
                    wv_index = sent.find(rong_word, wv_index)
                    if wv_index == -1:
                        break
                    wrong_v_indices.append(wv_index)
                    wv_index +=1
        # get all the indices of the third party words in the sentence
        for third in thirdParty_keywords:
            k = re.compile("\\b%s\\b" % third, re.I)
            y = k.search(sent)
            if y != None:
            #if third in sent:
                third_index=0
                while third_index < len(sent):
                    third_index = sent.find(third, third_index)
                    if third_index == -1:
                        break
                    thirdParty_indices.append(third_index)
                    third_index +=1
        # get all the indices of the share words
        for share in share_keywords:
            k = re.compile("\\b%s\\b" % share, re.I)
            y = k.search(sent)
            if y != None:
            #if share in sent:
                share_index=0
                while share_index < len(sent):
                    share_index = sent.find(share, share_index)
                    if share_index == -1:
                        break
                    shareParty_indices.append(share_index)
                    share_index +=1
    # combine all the indices together then sort them ascending
        Lists = wrong_v_indices + thirdParty_indices + shareParty_indices
        Lists.sort()
        # start to devide the sentence into parts based on the index
        y = 0
        for x in range(len(Lists)):
            # this means the partition is still empty and we only have one index
            if (len(partitions) < 1 and len(Lists) - 1 == 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)

            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(Lists) - 1 > 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]

            elif x == len(Lists)-1:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]

        # start to search if there is any features in each part
        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break
            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if location in partitions[part]:
                    sensitive_word = location
                    break
            if collect_word !="" and sensitive_word !="":
                feature = collect_word + ' '+ sensitive_word
                feature_selection.append(feature)
        return feature_selection

    if check_num =='3':
        wrong_v_indices = []
        cookie_indices = []
        shareParty_indices = []
        partitions = []

        # to get all indices of the wrong verb in the sentence
        for rong_word in wrongVerb_keywords:
            k = re.compile("\\b%s\\b" % rong_word, re.I)
            y = k.search(sent)
            if y != None:
            #if rong_word in sent:
                wv_index =0
                while wv_index < len(sent):
                    wv_index = sent.find(rong_word, wv_index)
                    if wv_index == -1:
                        break
                    wrong_v_indices.append(wv_index)
                    wv_index +=1
        # get all the indices of the cookie words in the sentence
        for cookie in Cookie_keywords:
            k = re.compile("\\b%s\\b" % cookie, re.I)
            y = k.search(sent)
            if y != None:
            #if cookie in sent:
                cookie_index =0
                while cookie_index < len(sent):
                    cookie_index = sent.find(cookie, cookie_index)
                    if cookie_index == -1:
                        break
                    cookie_indices.append(cookie_index)
                    cookie_index +=1
        # get all the indices of the share words
        for share in share_keywords:
            k = re.compile("\\b%s\\b" % share, re.I)
            y = k.search(sent)
            if y != None:
            #if share in sent:
                share_index =0
                while share_index < len(sent):
                    share_index = sent.find(share, share_index)
                    if share_index == -1:
                        break
                    shareParty_indices.append(share_index)
                    share_index +=1
    # combine all the indices together then sort them ascending
        Lists = wrong_v_indices + cookie_indices + shareParty_indices
        Lists.sort()
        # start to devide the sentence into parts based on the index
        y = 0
        for x in range(len(Lists)):
            # this means the partition is still empty and we only have one index
            if (len(partitions) < 1 and len(Lists) - 1 == 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)

            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(Lists) - 1 > 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
                # we reach the last index of the list
            elif x == len(Lists) - 1:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)
            # we still not finish all the lists
            else:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]


        # start to search if there is any features in each part
        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if location in partitions[part]:
                    sensitive_word = location
                    break
            if collect_word !="" and sensitive_word !="":
                feature = collect_word + ' '+ sensitive_word
                feature_selection.append(feature)
        return feature_selection
    # share + wrong-v
    if check_num =='4':
        wrong_v_indices = []
        shareParty_indices = []
        partitions = []

        # to get all indices of the wrong verb in the sentence
        for rong_word in wrongVerb_keywords:
            k = re.compile("\\b%s\\b" % rong_word, re.I)
            y = k.search(sent)
            if y != None:
            #if rong_word in sent:
                wv_index = 0
                while wv_index < len(sent):
                    wv_index = sent.find(rong_word, wv_index)
                    if wv_index == -1:
                        break
                    wrong_v_indices.append(wv_index)
                    wv_index +=1

        # get all the indices of the share words
        for share in share_keywords:
            k = re.compile("\\b%s\\b" % share, re.I)
            y = k.search(sent)
            if y != None:
            #if share in sent:
                share_index = 0
                while share_index < len(sent):
                    share_index = sent.find(share, share_index)
                    if share_index == -1:
                        break
                    shareParty_indices.append(share_index)
                    share_index +=1
    # combine all the indices together then sort them ascending
        combined_lists = wrong_v_indices + shareParty_indices
        combined_lists.sort()
        # start to devide the sentence into parts based on the index
        y = 0
        for x in range(len(combined_lists)):
            # this means the partition is still empty and we only have one index
            if (len(partitions) < 1 and len(combined_lists) - 1 == 0):
                partitions.append(sent[:combined_lists[x]])
                y = combined_lists[x]
                part2 = sent[y:]
                partitions.append(part2)

            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(combined_lists) - 1 > 0):
                partitions.append(sent[:combined_lists[x]])
                y = combined_lists[x]

            elif x == len(combined_lists)-1:
                part = sent[y:combined_lists[x]]
                partitions.append(part)
                y = combined_lists[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:combined_lists[x]]
                partitions.append(part)
                y = combined_lists[x]

        # start to search if there is any features in each part
        feature_selection = []
        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if location in partitions[part]:
                    sensitive_word = location
                    break
            if collect_word !="" and sensitive_word !="":
                feature = collect_word + ' '+sensitive_word
                feature_selection.append(feature)
        return feature_selection
    # third + wrong-v
    if check_num == '5':
        wrong_v_indices = []
        thirdParty_indices = []
        partitions = []
        # to get all indices of the wrong verb in the sentence
        for rong_word in wrongVerb_keywords:
            k = re.compile("\\b%s\\b" % rong_word, re.I)
            y = k.search(sent)
            if y != None:
            #if rong_word in sent:
                wv_index =0
                while wv_index < len(sent):
                    wv_index = sent.find(rong_word, wv_index)
                    if wv_index == -1:
                        break
                    wrong_v_indices.append(wv_index)
                    wv_index += 1

        # get all the indices of the share words
        for third in thirdParty_keywords:
            k = re.compile("\\b%s\\b" % third, re.I)
            y = k.search(sent)
            if y != None:
            #if third in sent:
                third_index =0
                while third_index < len(sent):
                    third_index = sent.find(third, third_index)
                    if third_index == -1:
                        break
                    thirdParty_indices.append(third_index)
                    third_index += 1
        # combine all the indices together then sort them ascending
        Lists = wrong_v_indices + thirdParty_indices
        Lists.sort()
        # start to devide the sentence into parts based on the index
        y = 0
        for x in range(len(Lists)):
            # this means the partition is still empty and we only have one index
            if (len(partitions) < 1 and len(Lists) - 1 == 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)

            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(Lists) - 1 > 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]

            elif x == len(Lists) - 1:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]

        # start to search if there is any features in each part
        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if location in partitions[part]:
                    sensitive_word = location
                    break
            if collect_word != "" and sensitive_word != "":
                feature = collect_word + ' ' + sensitive_word
                feature_selection.append(feature)
        return feature_selection
    # cookie + wrong-v
    if check_num == '6':
        wrong_v_indices = []
        cookie_indices = []
        partitions = []
        # to get all indices of the wrong verb in the sentence
        for rong_word in wrongVerb_keywords:

            k = re.compile("\\b%s\\b" % rong_word, re.I)
            y = k.search(sent)
            if y != None:
                wv_index = 0
                while wv_index < len(sent):
                    wv_index = sent.find(rong_word, wv_index)
                    if wv_index == -1:
                        break
                    wrong_v_indices.append(wv_index)
                    wv_index += 1

        # get all the indices of the share words
        for cookie in Cookie_keywords:
            k = re.compile("\\b%s\\b" % cookie, re.I)
            y = k.search(sent)
            if y != None:
                cookie_index = 0
                while cookie_index < len(sent):
                    cookie_index = sent.find(cookie, cookie_index)
                    if cookie_index == -1:
                        break
                    cookie_indices.append(cookie_index)
                    cookie_index += 1
        # combine all the indices together then sort them ascending
        Lists = wrong_v_indices + cookie_indices
        Lists.sort()
        # start to devide the sentence into parts based on the index
        y = 0
        for x in range(len(Lists)):
            # this means the partition is still empty and we only have one index
            if (len(partitions) < 1 and len(Lists) - 1 == 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)

            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(Lists) - 1 > 0):
                partitions.append(sent[:Lists[x]])
                y = Lists[x]
            # we reach the last index of the list
            elif x == len(Lists) - 1:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]
                part2 = sent[y:]
                partitions.append(part2)
            # we still not finish all the lists
            else:
                part = sent[y:Lists[x]]
                partitions.append(part)
                y = Lists[x]
        # start to search if there is any features in each part
        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                #if cv in partitions[part]:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
               # if location in partitions[part]:
                    sensitive_word = location
                    break
            if collect_word != "" and sensitive_word != "":
                feature = collect_word + ' ' + sensitive_word
                feature_selection.append(feature)
        return feature_selection
    # check third words
    if check_num == '7':
        thirdParty_indices = []
        partitions = []
        for third in thirdParty_keywords:
            k = re.compile("\\b%s\\b" % third, re.I)
            y = k.search(sent)
            if y != None:
                third_index = 0
                while third_index < len(sent):
                    third_index = sent.find(third, third_index)
                    if third_index == -1:
                        break
                    thirdParty_indices.append(third_index)
                    third_index += 1

        thirdParty_indices.sort()
        y = 0
        for x in range(len(thirdParty_indices)):
            if len(partitions) < 1 and len(thirdParty_indices)-1 == 0:
                partitions.append(sent[:thirdParty_indices[x]])
                y = thirdParty_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            elif len(partitions) < 1 and len(thirdParty_indices)-1 > 0:
                partitions.append(sent[:thirdParty_indices[x]])
                y = thirdParty_indices[x]
            elif x == len(thirdParty_indices)- 1:
                part = sent[y:thirdParty_indices[x]]
                partitions.append(part)
                y = thirdParty_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:thirdParty_indices[x]]
                partitions.append(part)
                y = thirdParty_indices[x]

        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                    sensitive_word = location
                    break
            if part ==0 :

                if (collect_word != "" and sensitive_word != ""):
                    feature = collect_word + ' ' + sensitive_word
                    feature_selection.append(feature)

        return feature_selection
    # check share verbs
    if check_num == '8':
        shareParty_indices = []
        partitions = []
        for share in share_keywords:
            k = re.compile("\\b%s\\b" % share, re.I)
            y = k.search(sent)
            if y != None:
            #if share in sent:
                share_index = 0
                while share_index < len(sent):
                    share_index = sent.find(share, share_index)
                    if share_index == -1:
                        break
                    shareParty_indices.append(share_index)
                    share_index += 1

        shareParty_indices.sort()
        y = 0
        for x in range(len(shareParty_indices)):
            if len(partitions) < 1 and len(shareParty_indices)-1 ==0:
                partitions.append(sent[:shareParty_indices[x]])
                y = shareParty_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            elif len(partitions) < 1 and len(shareParty_indices) - 1 > 0:
                partitions.append(sent[:shareParty_indices[x]])
                y = shareParty_indices[x]

            elif x == len(shareParty_indices) - 1:
                part = sent[y:shareParty_indices[x]]
                partitions.append(part)
                y = shareParty_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:shareParty_indices[x]]
                partitions.append(part)
                y = shareParty_indices[x]
        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""

            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                    sensitive_word = location
                    break

            if part == 0:
                if (collect_word != "" and sensitive_word != ""):
                    feature = collect_word + ' ' + sensitive_word
                    feature_selection.append(feature)

        return feature_selection
    # check wrong words
    if check_num == '9':
        wrong_v_indices = []
        partitions = []
        for wrong_v in wrongVerb_keywords:
            k = re.compile("\\b%s\\b" % wrong_v, re.I)
            y = k.search(sent)
            if y != None:
            #if wrong_v in sent:
                wrong_v_index = 0
                # to collect all the wrong verb indices
                while wrong_v_index < len(sent):
                    wrong_v_index = sent.find(wrong_v, wrong_v_index)
                    if wrong_v_index == -1:
                        break
                    wrong_v_indices.append(wrong_v_index)
                    wrong_v_index += 1
        # we sort the indices of the wv
        wrong_v_indices.sort()
        y = 0
        # to split the sentence in parts based on the index of the wrong verb
        for x in range(len(wrong_v_indices)):
            # this mean we don't have any item yet and we only have one index hence we need to add two partitions; one from the start until the index; and one from the indes untill the end
            if (len(partitions) < 1 and len(wrong_v_indices)-1 == 0):
                partitions.append(sent[:wrong_v_indices[x]])
                y = wrong_v_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            # this mean we don't have any item yet but we have more than one index
            elif (len(partitions) < 1 and len(wrong_v_indices)-1 > 0):
                partitions.append(sent[:wrong_v_indices[x]])
                y = wrong_v_indices[x]
            # this mean we reach the last index, hence we need to append two parts as well
            elif x == len(wrong_v_indices) - 1:
                part = sent[y:wrong_v_indices[x]]
                partitions.append(part)
                y = wrong_v_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:wrong_v_indices[x]]
                partitions.append(part)
                y = wrong_v_indices[x]

        feature_selection = []
        # we loop through each partition to check if there is any cv and sw words
        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            cv_index = 0
            sw_index = 0
            # loop through all the collect keyword
            for cv in Collect_Verbs:
                # if we find one
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                    collect_word = cv       # we want to get the cv word and the cv index
                    while cv_index < len(partitions[part]):
                        cv_index = partitions[part].find(cv, cv_index)
                        if cv_index ==-1: # we did not find the word
                            break
                        if cv_index >= 0:
                            break
                        cv_index += 1
                    break # break from the for loop
            # do the same thing with the location
            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                    sensitive_word = location
                    while sw_index < len(partitions[part]):
                        sw_index = partitions[part].find(location, sw_index)
                        if sw_index == -1:
                            break
                        if sw_index >= 0:
                            break
                        sw_index += 1
                    break
            # check if we in the first partition that mean we don't care about the orders of the cv and the sw
            if part == 0:
                if (collect_word != "" and sensitive_word != ""): # check that the valuse are not empty
                    location_feature = collect_word + ' ' + sensitive_word
                    feature_selection.append(location_feature)
            # if we in the second partition befor the last one
            elif  part > 0 :
                # this means that the cv word comes before the sw word cv + sw --> we collect the data otherwise no collect
                if cv_index < sw_index:
                    if (collect_word != "" and sensitive_word != ""):
                        feature = collect_word + ' ' + sensitive_word
                        feature_selection.append(feature)

        return feature_selection
    # check cookie words
    if check_num == '10':
        cookie_indices = []
        partitions = []
        for cookie in Cookie_keywords:
            k = re.compile("\\b%s\\b" % cookie, re.I)
            y = k.search(sent)
            if y != None:
                cookie_index = 0
                while cookie_index < len(sent):
                    cookie_index = sent.find(cookie, cookie_index)
                    if cookie_index == -1:
                        break
                    cookie_indices.append(cookie_index)
                    cookie_index += 1

        cookie_indices.sort()
        y = 0
        for x in range(len(cookie_indices)):
            if len(partitions) < 1 and len(cookie_indices)-1 == 0 :
                partitions.append(sent[:cookie_indices[x]])
                y = cookie_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            elif len(partitions) < 1 and len(cookie_indices)-1 >0 :
                partitions.append(sent[:cookie_indices[x]])
                y = cookie_indices[x]
            elif x == len(cookie_indices) - 1:
                part = sent[y:cookie_indices[x]]
                partitions.append(part)
                y = cookie_indices[x]
                part2 = sent[y:]
                partitions.append(part2)
            else:
                part = sent[y:cookie_indices[x]]
                partitions.append(part)
                y = cookie_indices[x]

        feature_selection = []

        for part in range(len(partitions)):
            collect_word = ""
            sensitive_word = ""
            for cv in Collect_Verbs:
                k = re.compile("\\b%s\\b" % cv, re.I)
                y = k.search(partitions[part])
                if y != None:
                    collect_word = cv
                    break

            for location in feature_list:
                k = re.compile("\\b%s\\b" % location, re.I)
                y = k.search(partitions[part])
                if y != None:
                    sensitive_word = location
                    break
            if part == 0 :
                if (collect_word != "" and sensitive_word != ""):
                    feature = collect_word + ' ' + sensitive_word
                    feature_selection.append(feature)

        return feature_selection
# to remove list of lists and flatten the list
def flatten(A):
    rt = []
    for i in A:
        if isinstance(i,list): rt.extend(flatten(i))
        else: rt.append(i)
    return rt

#///////////////////////////////////////////////////////////////////////#
# we start call each feature
# Extract location Feature
def Extract_location (document):
    location_sent = []
    wrong_locationList = []
    collect_location_sent = []
    Location_featuer_list = []

# 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        for word in wrongLocation_keywords:
        # we use the word boundary techninque from regular expression to find if the exact phrase of the wrong location is in the sentence
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y!= None:
                wrong_locationList.append(sent)
        for word in Location_KeyWords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                location_sent.append(sent)
# 2- loop through the wrong location list to delete the wrong words and check again if it is has correct location key word, then add it back to the location_sent list
    for sent in wrong_locationList:
        new_text = check_wrongWords(sent, wrongLocation_keywords)
        # check the new sentence again. If it has correct location word
        for word in Location_KeyWords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(new_text)
            if y != None:
                location_sent.append(new_text)

# 3- To limit the sentences to the one that collect location
    for sent in location_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_location_sent.append(sent)

# 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
# cookie words, and wrong verbs. each of which has its own list to ckeck it later
# we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_location_sent = check_list(collect_location_sent, '1')
# case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_location_sent = check_list(collect_location_sent, '2')
# case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_location_sent = check_list(collect_location_sent, '3')
# case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_location_sent = check_list(collect_location_sent, '4')
# case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_location_sent = check_list(collect_location_sent, '5')
# case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_location_sent = check_list(collect_location_sent, '6')
    thirdParty, collect_location_sent = check_list(collect_location_sent, '7')
    shareParty, collect_location_sent = check_list(collect_location_sent, '8')
    wrongVerb, collect_location_sent = check_list(collect_location_sent, '9')
    cookie, collect_location_sent = check_list(collect_location_sent, '10')

# 5- to remove any duplicate sentences
    collect_location_sent = list(set(collect_location_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))

# We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_location_sent) > 0:
        for x in collect_location_sent:
            feature = collect_feature(x, Location_KeyWords)
            if feature != None:
                Location_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                Location_feature = check_features(neg, '1', Location_KeyWords)
                if Location_feature != []:
                    Location_featuer_list.append(Location_feature)

        if len(case1_list) > 0:
            for item in case1_list:
                Location_feature = check_features(item, '2', Location_KeyWords)
                if Location_feature != []:
                    Location_feature = ' '.join([str(x) for x in Location_feature])
                    Location_featuer_list.append(Location_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                Location_feature = check_features(item, '3', Location_KeyWords)
                if Location_feature != []:
                    Location_feature = ' '.join([str(x) for x in Location_feature])
                    Location_featuer_list.append(Location_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                Location_feature = check_features(item, '4', Location_KeyWords)
                if Location_feature != []:
                    Location_feature = ' '.join([str(x) for x in Location_feature])
                    Location_featuer_list.append(Location_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                Location_feature = check_features(item, '5', Location_KeyWords)
                if Location_feature != []:
                    Location_feature = ' '.join([str(x) for x in Location_feature])
                    Location_featuer_list.append(Location_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                Location_feature = check_features(item, '6', Location_KeyWords)
                if Location_feature != []:
                    Location_feature = ' '.join([str(x) for x in Location_feature])
                    Location_featuer_list.append(Location_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                Location_feature = check_features(third, '7', Location_KeyWords)
                if Location_feature != []:
                    Location_featuer_list.append(Location_feature)

        if len(shareParty) > 0:
            for share in shareParty:
                Location_feature = check_features(share, '8',Location_KeyWords )
                if Location_feature != []:
                    Location_featuer_list.append(Location_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                Location_feature = check_features(wrong_v, '9',Location_KeyWords )
                if Location_feature != []:
                    Location_featuer_list.append(Location_feature)

        if len(cookie) > 0:
            for cookie_w in cookie:
                Location_feature = check_features(cookie_w, '10', Location_KeyWords)
                if Location_feature != []:
                    Location_featuer_list.append(Location_feature)

    for feature in Location_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Location_featuer_list
# Extract login Feature
def Extract_login (document):
    login_sent = []
    wrong_loginList = []
    collect_login_sent = []
    Login_featuer_list = []

    # 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        # check if the sentence has wrong email keyword
        for word in wrongCredentials_keywords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                wrong_loginList.append(sent)

        for word in Login_keywords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                login_sent.append(sent)

    # 2- loop through the wrong Email list to delete the wrong words and check again if it is has correct email key word, then add it back to the location_sent list
    for sent in wrong_loginList:
        new_text = check_wrongWords(sent, wrongCredentials_keywords)
        # check the new sentence again. If it has correct location word
        for word in Login_keywords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(new_text)
            if y != None:
                login_sent.append(new_text)

    # 3- To limit the sentences to the one that collect email
    for sent in login_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_login_sent.append(sent)

    # 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
    # cookie words, and wrong verbs. each of which has its own list to ckeck it later
    # we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_login_sent = check_list(collect_login_sent, '1')
    # case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_login_sent = check_list(collect_login_sent, '2')
    # case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_login_sent = check_list(collect_login_sent, '3')
    # case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_login_sent = check_list(collect_login_sent, '4')
    # case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_login_sent = check_list(collect_login_sent, '5')
    # case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_login_sent = check_list(collect_login_sent, '6')
    thirdParty, collect_login_sent = check_list(collect_login_sent, '7')
    shareParty, collect_login_sent = check_list(collect_login_sent, '8')
    wrongVerb, collect_login_sent = check_list(collect_login_sent, '9')
    cookie, collect_login_sent = check_list(collect_login_sent, '10')

    # 5- to remove any duplicate sentences
    collect_login_sent = list(set(collect_login_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))

    # We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_login_sent) > 0:
        for x in collect_login_sent:
            feature = collect_feature(x, Login_keywords)
            if feature != None:
                Login_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                Login_feature = check_features(neg, '1', Login_keywords)
                if Login_feature != []:
                    Login_featuer_list.append(Login_feature)

        if len(case1_list) > 0:
            for item in case1_list:
                Login_feature = check_features(item, '2', Login_keywords)
                if Login_feature != []:
                    Login_feature = ' '.join([str(x) for x in Login_feature])
                    Login_featuer_list.append(Login_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                login_feature = check_features(item, '3', Login_keywords)
                if login_feature != []:
                    login_feature = ' '.join([str(x) for x in login_feature])
                    Login_featuer_list.append(login_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                login_feature = check_features(item, '4', Login_keywords)
                if login_feature != []:
                    login_feature = ' '.join([str(x) for x in login_feature])
                    Login_featuer_list.append(login_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                login_feature = check_features(item, '5', Login_keywords)
                if login_feature != []:
                    login_feature = ' '.join([str(x) for x in login_feature])
                    Login_featuer_list.append(login_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                login_feature = check_features(item, '6', Login_keywords)
                if login_feature != []:
                    login_feature = ' '.join([str(x) for x in login_feature])
                    Login_featuer_list.append(login_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                login_feature = check_features(third, '7',Login_keywords )
                if login_feature != []:
                    Login_featuer_list.append(login_feature)


        if len(shareParty) > 0:
            for share in shareParty:
                login_feature = check_features(share, '8', Login_keywords)
                if login_feature != []:
                    Login_featuer_list.append(login_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                login_feature = check_features(wrong_v, '9', Login_keywords)
                if login_feature != []:
                    Login_featuer_list.append(login_feature)

        if len(cookie) > 0:
            for cookie_w in cookie:
                login_feature = check_features(cookie_w, '10', Login_keywords)
                if login_feature != []:
                    Login_featuer_list.append(login_feature)

    for feature in Login_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Login_featuer_list
# Extract password Feature
def Extract_password (document):
    password_sent = []
    wrong_passwordList = []
    collect_password_sent = []
    Password_featuer_list = []

    # 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        for word in wrongCredentials_keywords:# check if the sentence has wrong email keyword
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                wrong_passwordList.append(sent)
        for word in Password_keywords:        # check if the sentence have the Email keyword
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                password_sent.append(sent)



    # 2- loop through the wrong Email list to delete the wrong words and check again if it is has correct email key word, then add it back to the location_sent list
    for sent in wrong_passwordList:
        new_text = check_wrongWords(sent, wrongCredentials_keywords)
        # check the new sentence again. If it has correct location word
        for word in Password_keywords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(new_text)
            if y != None:
                password_sent.append(new_text)

    # 3- To limit the sentences to the one that collect email
    for sent in password_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_password_sent.append(sent)

    # 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
    # cookie words, and wrong verbs. each of which has its own list to ckeck it later
    # we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_password_sent = check_list(collect_password_sent, '1')
    # case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_password_sent = check_list(collect_password_sent, '2')
    # case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_password_sent = check_list(collect_password_sent, '3')
    # case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_password_sent = check_list(collect_password_sent, '4')
    # case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_password_sent = check_list(collect_password_sent, '5')
    # case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_password_sent = check_list(collect_password_sent, '6')
    thirdParty, collect_password_sent = check_list(collect_password_sent, '7')
    shareParty, collect_password_sent = check_list(collect_password_sent, '8')
    wrongVerb, collect_password_sent = check_list(collect_password_sent, '9')
    cookie, collect_password_sent = check_list(collect_password_sent, '10')

    # 5- to remove any duplicate sentences
    collect_password_sent = list(set(collect_password_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))
    # We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_password_sent) > 0:
        for x in collect_password_sent:
            feature = collect_feature(x, Password_keywords)
            if feature != None:
                Password_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                password_feature = check_features(neg, '1', Password_keywords)
                if password_feature != []:
                    Password_featuer_list.append(password_feature)

        if len(case1_list) > 0:
            for item in case1_list:
                password_feature = check_features(item, '2', Password_keywords)
                if password_feature != []:
                    password_feature = ' '.join([str(x) for x in password_feature])
                    Password_featuer_list.append(password_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                password_feature = check_features(item, '3', Password_keywords)
                if password_feature != []:
                    password_feature = ' '.join([str(x) for x in password_feature])
                    Password_featuer_list.append(password_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                password_feature = check_features(item, '4', Password_keywords)
                if password_feature != []:
                    password_feature = ' '.join([str(x) for x in password_feature])
                    Password_featuer_list.append(password_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                password_feature = check_features(item, '5', Password_keywords)
                if password_feature != []:
                    password_feature = ' '.join([str(x) for x in password_feature])
                    Password_featuer_list.append(password_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                password_feature = check_features(item, '6', Password_keywords)
                if password_feature != []:
                    password_feature = ' '.join([str(x) for x in password_feature])
                    Password_featuer_list.append(password_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                password_feature = check_features(third, '7', Password_keywords)
                if password_feature != []:
                    Password_featuer_list.append(password_feature)
                    #print 'The login feature from thirdparty sent is:', login_feature

        if len(shareParty) > 0:
            for share in shareParty:
                password_feature = check_features(share, '8', Password_keywords)
                if password_feature != []:
                    Password_featuer_list.append(password_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                password_feature = check_features(wrong_v, '9', Password_keywords)
                if password_feature != []:
                    Password_featuer_list.append(password_feature)


        if len(cookie) > 0:
            for cookie_w in cookie:
                password_feature = check_features(cookie_w, '10', Password_keywords)
                if password_feature != []:
                    Password_featuer_list.append(password_feature)
    for feature in Password_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Password_featuer_list
# Extract email Feature
def Extract_email (document):
    email_sent = []
    wrong_emailList = []
    collect_email_sent = []
    Email_featuer_list = []

    # 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        for word in wrong_email:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                wrong_emailList.append(sent)
        for word in Email_KeyWords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                email_sent.append(sent)


    # 2- loop through the wrong Email list to delete the wrong words and check again if it is has correct email key word, then add it back to the location_sent list
    for sent in wrong_emailList:
        new_text = check_wrongWords(sent, wrong_email)
        # check the new sentence again. If it has correct location word
        for word in Email_KeyWords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(new_text)
            if y != None:
                email_sent.append(new_text)



    # 3- To limit the sentences to the one that collect email
    for sent in email_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_email_sent.append(sent)

        #if any(collect_word in sent for collect_word in Collect_Verbs):
        #    collect_email_sent.append(sent)

    # 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
    # cookie words, and wrong verbs. each of which has its own list to ckeck it later
    # we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_email_sent = check_list(collect_email_sent, '1')
    # case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_email_sent = check_list(collect_email_sent, '2')
    # case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_email_sent = check_list(collect_email_sent, '3')
    # case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_email_sent = check_list(collect_email_sent, '4')
    # case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_email_sent = check_list(collect_email_sent, '5')
    # case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_email_sent = check_list(collect_email_sent, '6')
    thirdParty, collect_email_sent = check_list(collect_email_sent, '7')
    shareParty, collect_email_sent = check_list(collect_email_sent, '8')
    wrongVerb, collect_email_sent = check_list(collect_email_sent, '9')
    cookie, collect_email_sent = check_list(collect_email_sent, '10')

    # 5- to remove any duplicate sentences
    collect_email_sent = list(set(collect_email_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))

    # We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_email_sent) > 0:
        for x in collect_email_sent:
            feature = collect_feature(x, Email_KeyWords)
            if feature != None:
                Email_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                email_feature = check_features(neg, '1', Email_KeyWords)
                if email_feature != []:
                    Email_featuer_list.append(email_feature)

        if len(case1_list) > 0:
            for item in case1_list:
                email_feature = check_features(item, '2', Email_KeyWords)
                if email_feature != []:
                    email_feature = ' '.join([str(x) for x in email_feature])
                    Email_featuer_list.append(email_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                email_feature = check_features(item, '3', Email_KeyWords)
                if email_feature != []:
                    email_feature = ' '.join([str(x) for x in email_feature])
                    Email_featuer_list.append(email_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                email_feature = check_features(item, '4', Email_KeyWords)
                if email_feature != []:
                    email_feature = ' '.join([str(x) for x in email_feature])
                    Email_featuer_list.append(email_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                email_feature = check_features(item, '5', Email_KeyWords)
                if email_feature != []:
                    email_feature = ' '.join([str(x) for x in email_feature])
                    Email_featuer_list.append(email_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                email_feature = check_features(item, '6', Email_KeyWords)
                if email_feature != []:
                    email_feature = ' '.join([str(x) for x in email_feature])
                    Email_featuer_list.append(email_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                email_feature = check_features(third, '7', Email_KeyWords)
                if email_feature != []:
                    Email_featuer_list.append(email_feature)


        if len(shareParty) > 0:
            for share in shareParty:
                email_feature = check_features(share, '8', Email_KeyWords)
                if email_feature != []:
                    Email_featuer_list.append(email_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                email_feature = check_features(wrong_v, '9', Email_KeyWords )
                if email_feature != []:
                    Email_featuer_list.append(email_feature)

        if len(cookie) > 0:
            for cookie_w in cookie:
                email_feature = check_features(cookie_w, '10', Email_KeyWords)
                if email_feature != []:
                    Email_featuer_list.append(email_feature)
    for feature in Email_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Email_featuer_list
# Extract username Feature
def Extract_username(document):
    username_sent = []
    wrong_usenameList = []
    collect_username_sent = []
    Username_featuer_list = []

    # 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        for word in wrongNames_keywords :# check if the sentence has wrong email keyword
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                wrong_usenameList.append(sent)
        for word in UserName_keywords:# check if the sentence have the Email keyword
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                username_sent.append(sent)

    # 2- loop through the wrong Email list to delete the wrong words and check again if it is has correct email key word, then add it back to the location_sent list
    for sent in wrong_usenameList:
        new_text = check_wrongWords(sent, wrongNames_keywords)
        # check the new sentence again. If it has correct location word
        for word in UserName_keywords:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(new_text)
            if y != None:
                username_sent.append(new_text)

    # 3- To limit the sentences to the one that collect email
    for sent in username_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_username_sent.append(sent)

    # 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
    # cookie words, and wrong verbs. each of which has its own list to ckeck it later
    # we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_username_sent = check_list(collect_username_sent, '1')
    # case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_username_sent = check_list(collect_username_sent, '2')
    # case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_username_sent = check_list(collect_username_sent, '3')
    # case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_username_sent = check_list(collect_username_sent, '4')
    # case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_username_sent = check_list(collect_username_sent, '5')
    # case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_username_sent = check_list(collect_username_sent, '6')
    thirdParty, collect_username_sent = check_list(collect_username_sent, '7')
    shareParty, collect_username_sent = check_list(collect_username_sent, '8')
    wrongVerb, collect_username_sent = check_list(collect_username_sent, '9')
    cookie, collect_username_sent = check_list(collect_username_sent, '10')

    # 5- to remove any duplicate sentences
    collect_username_sent = list(set(collect_username_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))

    # We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_username_sent) > 0:
        for x in collect_username_sent:
            feature = collect_feature(x, UserName_keywords)
            if feature != None:
                Username_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                username_feature = check_features(neg, '1', UserName_keywords)
                if username_feature != []:
                    Username_featuer_list.append(username_feature)
        if len(case1_list) > 0:
            for item in case1_list:
                username_feature = check_features(item, '2',UserName_keywords )
                if username_feature != []:
                    username_feature = ' '.join([str(x) for x in username_feature])
                    Username_featuer_list.append(username_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                username_feature = check_features(item, '3', UserName_keywords)
                if username_feature != []:
                    username_feature = ' '.join([str(x) for x in username_feature])
                    Username_featuer_list.append(username_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                username_feature = check_features(item, '4', UserName_keywords)
                if username_feature != []:
                    username_feature = ' '.join([str(x) for x in username_feature])
                    Username_featuer_list.append(username_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                username_feature = check_features(item, '5', UserName_keywords)
                if username_feature != []:
                    username_feature = ' '.join([str(x) for x in username_feature])
                    Username_featuer_list.append(username_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                username_feature = check_features(item, '6', UserName_keywords)
                if username_feature != []:
                    username_feature = ' '.join([str(x) for x in username_feature])
                    Username_featuer_list.append(username_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                username_feature = check_features(third, '7', UserName_keywords)
                if username_feature != []:
                    Username_featuer_list.append(username_feature)

        if len(shareParty) > 0:
            for share in shareParty:
                username_feature = check_features(share, '8', UserName_keywords)
                if username_feature != []:
                    Username_featuer_list.append(username_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                username_feature = check_features(wrong_v, '9', UserName_keywords)
                if username_feature != []:
                    Username_featuer_list.append(username_feature)

        if len(cookie) > 0:
            for cookie_w in cookie:
                username_feature = check_features(cookie_w, '10', UserName_keywords)
                if username_feature != []:
                    Username_featuer_list.append(username_feature)
    for feature in Username_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Username_featuer_list
# Extract device Feature
def Extract_device(document):
    device_sent = []
    collect_device_sent = []
    Device_featuer_list = []

    # 1- read the document and separate into two lists Location or wrong_location
    for sent in document:
        for word in Device_keywords:# check if the sentence have the Email keyword
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                device_sent.append(sent)

    # 3- To limit the sentences to the one that collect email
    for sent in device_sent:
        for word in Collect_Verbs:
            k = re.compile("\\b%s\\b" % word, re.I)
            y = k.search(sent)
            if y != None:
                collect_device_sent.append(sent)

    # 4- separate the sentence based on specific conditions such as if the sentence contain negative words, share verbs, third party
    # cookie words, and wrong verbs. each of which has its own list to ckeck it later
    # we refer to each condition with number e.g. negative word is condition 1, case1 is condition 2 ...etc
    negativeWordList, collect_device_sent = check_list(collect_device_sent, '1')
    # case 1 is for the sentence that contain third, share, and  wrong verbs
    case1_list, collect_device_sent = check_list(collect_device_sent, '2')
    # case 2 is for the sentence that contain cookie, share, and  wrong verbs
    case2_list, collect_device_sent = check_list(collect_device_sent, '3')
    # case 3 is for the sentence that contain share + wrong-v
    case3_list, collect_device_sent = check_list(collect_device_sent, '4')
    # case 4 is for the sentence that contain third + wrong-v
    case4_list, collect_device_sent = check_list(collect_device_sent, '5')
    # case 5 is for the sentence that contain cookie + wrong-v
    case5_list, collect_device_sent = check_list(collect_device_sent, '6')
    thirdParty, collect_device_sent = check_list(collect_device_sent, '7')
    shareParty, collect_device_sent = check_list(collect_device_sent, '8')
    wrongVerb, collect_device_sent = check_list(collect_device_sent, '9')
    cookie, collect_device_sent = check_list(collect_device_sent, '10')

    # 5- to remove any duplicate sentences
    collect_device_sent = list(set(collect_device_sent))
    negativeWordList = list(set(negativeWordList))
    case1_list = list(set(case1_list))
    case2_list = list(set(case2_list))
    case3_list = list(set(case3_list))
    case4_list = list(set(case4_list))
    case5_list = list(set(case5_list))
    thirdParty = list(set(thirdParty))
    shareParty = list(set(shareParty))
    wrongVerb = list(set(wrongVerb))
    cookie = list(set(cookie))
    print 'negative', negativeWordList
    print 'cas1', case1_list
    print 'cas2', case2_list
    print 'cas3', case3_list
    print 'cas4', case4_list
    print 'cas5', case5_list
    print 'third', thirdParty
    print 'share', shareParty
    print 'wrong', wrongVerb
    print 'cookie', cookie

    # We care about the main collect list. If it is has any features then no need to check the other conditions
    if len(collect_device_sent) > 0:
        for x in collect_device_sent:
            feature = collect_feature(x, Device_keywords)
            if feature != None:
                Device_featuer_list.append(feature)
    else:
        if len(negativeWordList) > 0:
            for neg in negativeWordList:
                device_feature = check_features(neg, '1', Device_keywords)
                if device_feature != []:
                    Device_featuer_list.append(device_feature)
        if len(case1_list) > 0:
            for item in case1_list:
                device_feature = check_features(item, '2', Device_keywords)
                if device_feature != []:
                    device_feature = ' '.join([str(x) for x in device_feature])
                    Device_featuer_list.append(device_feature)

        if len(case2_list) > 0:
            for item in case2_list:
                device_feature = check_features(item, '3', Device_keywords)
                if device_feature != []:
                    device_feature = ' '.join([str(x) for x in device_feature])
                    Device_featuer_list.append(device_feature)

        if len(case3_list) > 0:
            for item in case3_list:
                device_feature = check_features(item, '4', Device_keywords)
                if device_feature != []:
                    device_feature = ' '.join([str(x) for x in device_feature])
                    Device_featuer_list.append(device_feature)

        if len(case4_list) > 0:
            for item in case4_list:
                device_feature = check_features(item, '5', Device_keywords)
                if device_feature != []:
                    device_feature = ' '.join([str(x) for x in device_feature])
                    Device_featuer_list.append(device_feature)

        if len(case5_list) > 0:
            for item in case5_list:
                device_feature = check_features(item, '6', Device_keywords)
                if device_feature != []:
                    device_feature = ' '.join([str(x) for x in device_feature])
                    Device_featuer_list.append(device_feature)

        if len(thirdParty) > 0:
            for third in thirdParty:
                device_feature = check_features(third, '7', Device_keywords)
                if device_feature != []:
                    Device_featuer_list.append(device_feature)

        if len(shareParty) > 0:
            for share in shareParty:
                device_feature = check_features(share, '8',Device_keywords)
                if device_feature != []:
                    Device_featuer_list.append(device_feature)

        if len(wrongVerb) > 0:
            for wrong_v in wrongVerb:
                device_feature = check_features(wrong_v, '9',Device_keywords)
                if device_feature != []:
                    Device_featuer_list.append(device_feature)

        if len(cookie) > 0:
            for cookie_w in cookie:
                device_feature = check_features(cookie_w, '10', Device_keywords)
                if device_feature != []:
                    Device_featuer_list.append(device_feature)
    for feature in Device_featuer_list:
        IoT_PPA_FeaturesVectors.append(feature)

    return Device_featuer_list

def train_PPA_ML():
    df = pd.read_csv('~/Downloads/textMining_python_application/PPA_textLabeling.csv')
    df_predict_features = pd.read_csv('~/Downloads/textMining_python_application/IoT_PPA_try.csv')

    # features all the columns except the labels
    X = df["collect_sensitive_keywords"]
    # label_1 for predection
    y = df["label_1"]

    cv = TfidfVectorizer(use_idf= True)
# predict the first label
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    x_traincv = cv.fit_transform(x_train)
    x_testcv = cv.transform(x_test)
    t0 = time()
    mnb = MultinomialNB()
    mnb.fit(x_traincv, y_train)
    predictions = mnb.predict(x_testcv)
    print'The accuracy of (test) predicting collecting sensitive data is :', accuracy_score(y_test, predictions) * 100
    train_accuracy = mnb.score(x_traincv, y_train)
    print '\n The accuracy of (trainig) data is: ', train_accuracy * 100
    print'\n clasification report:\n', classification_report(y_test, predictions)
    labels = mnb.classes_
    print 'Labels = ', labels
    print'confusion matrix for test is:', confusion_matrix(y_test, predictions, labels =labels)
    print 'F1 score', f1_score(predictions, y_test, average='weighted')
    print 'Recall:', recall_score(predictions, y_test, average='weighted')
    print 'Precision:', precision_score(predictions, y_test, average='weighted')

    # predict for unseen data #
    P_feature = df_predict_features["Features"]
    features_prediction = cv.transform(P_feature)
    featurePrediction = mnb.predict(features_prediction)
    featurePrediction = list(set(featurePrediction))
    print 'The prediction of whether the IoT PPA collects sensitive data is:'
    print(featurePrediction)
    t1 = time()
    print 'function takes %f' % (t1 - t0)
    print('Apply cross validation \n')
    k_fold = KFold(len(y_train), n_folds=10, shuffle=True, random_state=0)
    print cross_val_score(mnb, x_traincv, y_train, cv=k_fold, n_jobs=1)

#**********************************************************************************************************************#

## main program start her ##############

ans = raw_input("Please Enter the IoT privacy policy website: ")
IoT_PPA_processedText = IoT_PPA_compliance(ans)
print (len(IoT_PPA_processedText))
print 'The IoT PPA is:', IoT_PPA_processedText
print 'The location vector is: ', Extract_location(IoT_PPA_processedText)
print 'The login vector is: ', Extract_login(IoT_PPA_processedText)
print 'The password vector is:', Extract_password(IoT_PPA_processedText)
print 'The email vector is:', Extract_email(IoT_PPA_processedText)
print 'The usename vector is:', Extract_username(IoT_PPA_processedText)
print 'The device vector is:', Extract_device(IoT_PPA_processedText)
final_features= flatten(IoT_PPA_FeaturesVectors)
print 'The final vectors are: ', final_features
df = pd.DataFrame(columns=['Features'], data= final_features)
df.to_csv('IoT_PPA_try.csv', index=False)
train_PPA_ML()