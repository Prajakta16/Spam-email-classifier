import re
from email import policy
from email.parser import BytesParser

import mailparser
from nltk import wordpunct_tokenize

from deprecated import email_parser


def get_text_from_html(html_body):
    html_body = html_body.replace("<br>", " ")
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html_body)
    # print(text)
    return text


def clean_text(text):
    text = text.replace("<br>", " ")
    tokens = wordpunct_tokenize(text)
    for i in range(0, len(tokens) - 1):
        if not tokens[i].isalpha():
            tokens[i] = ''
    words = [word.lower() for word in tokens if word.isalpha()]
    cleaned_text = ' '.join(words)
    return cleaned_text


def email_parser(email_file):
        html_flag = 0
        with open(email_file, 'rb') as fp:
            msg = BytesParser(policy=policy.default).parse(fp)
        # print('Subject:', msg['subject'])

        if not msg.is_multipart():
            # print("Singular email")
            if msg.get_content_maintype() == "text":
                if msg.get_content_subtype() == "plain":
                    # print(msg.get_content_type())
                    body = msg.get_body(preferencelist='text/plain')
                    # print(body)
                elif msg.get_content_subtype() == "html":
                    body = msg.get_body(preferencelist='html')
                    html_body = str(body).split("\n")[3:]
                    html_body = '\n'.join(html_body)
                    # print("----Parsed text through beautiful soup-------")
                    body = html_parse(html_body)
                else:
                    print("Don't know if html or text {}".format(msg.get_content_subtype()))
        else:
            print("Email is multipart")
            i = 0
            for part in msg.walk():
                i = i + 1
                print("part " + str(i))
                cdispo = str(part.get('Content-Disposition'))
                print(cdispo)
                print(part.get_content_type())
                print(part.get_content_subtype())
                if part.get_content_type() == 'multipart/alternative' or part.get_content_type() == 'multipart/related':
                    body = part.get_body(preferencelist='html')
                    print("----Body from get_body()-------")
                    print(body)
                    html_body = str(body).split("\n")[3:]
                    html_body = '\n'.join(html_body)
                    print("----Parsed text through beautiful soup-------")
                    body = html_parse(html_body)
                    print(body)
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)  # decode
                    print(body)
                    break
        return body


def html_parse(text):
    try:
        html_body = text.replace("<br>", " ").replace("\n", " ")
        clean = re.compile('.*<HTML>')
        html_body = re.sub(clean, '', html_body)
        text = re.sub('<[^<]+?>', '', html_body)
        return text
    except Exception:
        print("Unable to read web page through Beautiful soup")
        pass


class MailParser(object):

    def __init__(self, email_id, label):
        self.label = label
        self.email_id = email_id
        self.text = ""

    def parse_mail(self, mail_file):
        if mail_file not in ['/Users/prajakta/Downloads/trec07p/data/inmaill.51', '/Users/prajakta/Downloads/trec07p/data/inmaill.22']:
            try:
                # print(mail_file)
                mail = mailparser.parse_from_file(mail_file)
                # print(mail.message)
                # print(mail.headers)

                if mail:
                    if mail.text_html:
                        self.text = get_text_from_html(mail.text_html[0])
                    elif mail.text_plain:
                        self.text = mail.text_plain[0]
                    else:
                        self.text = email_parser(mail_file)
                        # print(mail_file)
                        # print("Trying to read through email_parser")
                        # print(self.text)
                        # exit()
                        # entire_msg_string = mail.message
                        # if self.text == "":
                        #     print(mail_file+"  -----------Nor html or text---------")
                        #     self.text = str(mail)
                        #     if mail.attachments[0]["content_transfer_encoding"] == "base64":
                        #         payload = mail.attachments[0]["payload"]
                        #         # print(payload)
                        #         decodedPayload = base64.urlsafe_b64decode(payload)
                        #         # x = decodedPayload.encode()
                        #         print("DECODED payload: " + str(decodedPayload, 'ISO-8859-1'))
                    if len(self.text.strip()) == 0:
                        self.text = mail.subject
                else:
                    print(mail_file+" ------------Cannot read email---------")

                self.text = clean_text(self.text)
                # print("Text : "+self.text)
                return self.text
            except Exception as e:
                print(e)
                print(mail_file+"  -----------No mail obj returned---------")
                pass