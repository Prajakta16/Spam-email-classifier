import random
from random import sample

from createIndex import Index
from mailParser import MailParser

LABEL_FILE = "/Users/prajakta/Downloads/trec07p/full/index"
DATA_FOLDER = "/Users/prajakta/Downloads/trec07p/"

if __name__ == "__main__":
    with open(LABEL_FILE, mode='r') as label_file:
        content = label_file.read().split("\n")
    label_file.close()

    email_index = Index()
    email_index.delete_and_create_new_index()

    test_list = random.sample(range(1, 75419), int(0.2*75419))
    print(len(test_list))
    print(test_list)

    count = 0
    msg_dict = dict()
    for line in content:
        if count % 10000 == 0 or count == 75418 or count == 75419:
            email_index.index_data(msg_dict)
            msg_dict = dict()
        # if count == 100:
        #     break
        label = line.split(" ")[0]
        email_file = line.split(" ")[1][3:]

        raw_content = ""
        # try:
        #     with open(DATA_FOLDER+email_file, 'r', encoding='ISO-8859-1') as f:
        #         raw_content = f.read()
        #         if email_file in ['/Users/prajakta/Downloads/trec07p/data/inmaill.95']:
        #             print(raw_content)
        # except Exception:
        #     raw_content = ""

        email_id = email_file.split(".")[1]
        if int(email_id) in test_list:
            split = "test"
            print(email_id+" test")
        else:
            split = "train"

        mail_parser_obj = MailParser(email_id, label)

        try:
            text = mail_parser_obj.parse_mail(DATA_FOLDER+email_file)
        except Exception:
            text = ""

        msg_dict[email_id] = {"text": text, "raw_content": raw_content, "label": label, "split": split}
        count += 1
    print(count)
