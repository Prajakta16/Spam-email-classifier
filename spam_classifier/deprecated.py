import re
from email import policy
from email.parser import BytesParser

CRAWLED_FOLDER = './CRAWLED_FOLDER/'
FORMATTED_DATASET_FILE = "./formatted text file"


def html_parse(text):
    # try:
    #     raw_html = text
    #     # print("Raw html :"+str(raw_html))
    #
    #     soup = BeautifulSoup(raw_html, features="html.parser")
    #     # print("Raw html :"+str(soup.prettify()))
    #     # self.title = subject
    #
    #     page_content = soup.find_all(["table", "p", "div"])  # finds table or paragraph
    #     print(len(page_content))
    #     text = ""
    #     for content in page_content:
    #         if str(content).startswith('<p'):  # page found
    #             text = text + "" + content.text
    #         if str(content).startswith('<div'):  # page found
    #             text = text + "" + content.text
    #         else:  # table found
    #             table_text = ""
    #             headers = content.findAll('th')
    #             head_cells = []
    #             for i in range(0, len(headers)):
    #                 head_cells.append(headers[i].text + "".lstrip().rstrip())
    #             for row in content.findAll('tr'):
    #                 cells = row.findAll('td')
    #                 for i in range(0, len(cells)):
    #                     if len(headers) == len(cells):
    #                         table_text = table_text + head_cells[i] + ":" + (
    #                                 cells[i].text + "".lstrip().rstrip())
    #                     else:
    #                         table_text = table_text + (cells[i].text + "".lstrip().rstrip())
    #             table_text = table_text.replace("\n", " ")
    #             text = text + table_text + "\n "
    #     return text
    try:
        html_body = text.replace("<br>", " ").replace("\n", " ")
        clean = re.compile('.*<HTML>')
        html_body = re.sub(clean, '', html_body)
        text = re.sub('<[^<]+?>', '', html_body)
        return text
    except Exception:
        print("Unable to read web page through Beautiful soup")
        pass


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
                # print(msg.get_content_type())
                body = msg.get_body(preferencelist='html')
                # print("----Body from get_body()-------")
                # print(body)
                html_body = str(body).split("\n")[3:]
                html_body = '\n'.join(html_body)
                # print("----Parsed text through beautiful soup-------")
                body = html_parse(html_body)
                # print(body)
            else:
                print("Don't know if html or text {}".format(msg.get_content_subtype()))
    else:
        print("Email is multipart")
        i = 0
        for part in msg.walk():
            i = i+1
            print("part "+str(i))
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
    # # We can extract the richest alternative in order to display it:
    # richest = msg.get_body()
    # partfiles = {}
    # text = ""
    # try:
    #     if msg.is_multipart():
    #         print("multipart for "+email_file)
    #         html_flag = 0
    #         html = ""
    #         print(len(msg.get_payload()))
    #         for part in msg.get_payload():
    #             print(part)
    #             print(part.get_content_charset())
    #             if part.get_content_charset() is None:
    #                 charset = chardet.detect(str(part))['encoding']
    #             else:
    #                 charset = part.get_content_charset()
    #             print("Charset for "+email_file)
    #             print(charset)
    #             if part.get_content_type() == 'text/plain':
    #                 text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
    #                 print(text)
    #             if part.get_content_type() == 'text/html':
    #                 html_flag = 1
    #                 html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
    #                 print(html)
    #             if part.get_content_type() == 'multipart/alternative':
    #                 for subpart in part.get_payload():
    #                     if subpart.get_content_charset() is None:
    #                         charset = chardet.detect(str(subpart))['encoding']
    #                     else:
    #                         charset = subpart.get_content_charset()
    #                     if subpart.get_content_type() == 'text/plain':
    #                         text = unicode(subpart.get_payload(decode=True), str(charset), "ignore").encode('utf8',
    #                                                                                                         'replace')
    #                     if subpart.get_content_type() == 'text/html':
    #                         html = unicode(subpart.get_payload(decode=True), str(charset), "ignore").encode('utf8',
    #                                                                                                         'replace')
    #             if html_flag == 0:
    #                 return text.strip(), html_flag
    #             else:
    #                 return html.strip(), html_flag
    #     elif msg.get_content_maintype() == 'text':
    #         if richest['content-type'].subtype == 'plain':
    #             for line in richest.get_content().splitlines():
    #                 text += " " + line
    #         elif richest['content-type'].subtype == 'html':
    #             html_flag = 1
    #             text = str(richest)
    #         else:
    #             print("Don't know how to display {}".format(richest.get_content_type()))
    #     else:
    #         print("Don't know how to display {}".format(richest.get_content_type()))
    # except Exception:
    #     print("Unable to get text")
    # return text, html_flag


class emailReader(object):

    def __init__(self, email_id, label):
        self.label = label
        self.email_id = email_id
        self.title = ""
        self.text = ""

    def read_page(self, email_file):
        print("Parsing email file.... " + email_file)
        email_parser(email_file)

        # text, html_flag = email_parser(email_file)
        # if html_flag == 1:
        #     try:
        #         raw_html = text
        #         # print("Raw html :"+str(raw_html))
        #
        #         soup = BeautifulSoup(raw_html, features="html.parser")
        #         # print("Raw html :"+str(soup.prettify()))
        #         # self.title = subject
        #
        #         page_content = soup.find_all(
        #             ["table", "p"])  # finds table or paragraph
        #         text = ""
        #         for content in page_content:
        #             if str(content).startswith('<p'):  # page found
        #                 text = text + "" + content.text
        #             else:  # table found
        #                 table_text = ""
        #                 headers = content.findAll('th')
        #                 head_cells = []
        #                 for i in range(0, len(headers)):
        #                     head_cells.append(headers[i].text + "".lstrip().rstrip())
        #                 for row in content.findAll('tr'):
        #                     cells = row.findAll('td')
        #                     for i in range(0, len(cells)):
        #                         if len(headers) == len(cells):
        #                             table_text = table_text + head_cells[i] + ":" + (
        #                                     cells[i].text + "".lstrip().rstrip())
        #                         else:
        #                             table_text = table_text + (cells[i].text + "".lstrip().rstrip())
        #                 table_text = table_text.replace("\n", " ")
        #                 text = text + table_text + "\n "
        #         self.text = text
        #
        #     except requests.exceptions.RequestException:
        #         print("Unable to read web page through Beautiful soup")
        #         pass
        # else:
        #     self.text = text
        #
        # # for p in ['"', '!', '#', '$', '%', '&', '(', ')', '*', '+', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '`', '{', '|', '}', '~']:
        #
        # info = {"email_id": self.email_id, "text": self.text, "label": self.label}
        # return info
