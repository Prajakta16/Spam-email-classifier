import pickle
import re
import os
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers


class Index:
    # cloud settings
    INDEX_NAME = 'waterloo_emails'
    TYPE_NAME = 'document'
    USERNAME = 'elastic'
    PASSWORD = 'UnnK1zgP6KaPXNs5qRseEv4E'
    es = Elasticsearch('https://0ef20e31c28647409cb714dc1d649181.us-west1.gcp.cloud.es.io',
                       http_auth=(USERNAME, PASSWORD), scheme='https', port=9243)

    # localhost settings
    # ES_HOST = {"host": "localhost", "port": 9200}
    # INDEX_NAME = 'maritime_accidents'
    # TYPE_NAME = 'document'
    # es = Elasticsearch(hosts=[ES_HOST], timeout=3600)

    def delete_and_create_new_index(self):
        if self.es.indices.exists(self.INDEX_NAME):
            print("index already exists... deleting " + self.INDEX_NAME + " index...")
            res = self.es.indices.delete(index=self.INDEX_NAME, ignore=[400, 404])
            print(" response: '%s'" % res)

        request_body = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "max_result_window": 90000,
                "analysis": {
                    "filter": {
                        "english_stop": {
                            "type": "stop",
                            "stopwords": ["a", "about", "above", "according", "across", "after", "afterwards",
                                          "again", "against", "albeit", "all", "almost", "alone", "along",
                                          "already", "also", "although", "always", "am", "among", "amongst", "an",
                                          "and", "another", "any", "anybody", "anyhow", "anyone", "anything",
                                          "anyway", "anywhere", "apart", "are", "around", "as", "at", "av", "be",
                                          "became", "because", "become", "becomes", "becoming", "been", "before",
                                          "beforehand", "behind", "being", "below", "beside", "besides", "between",
                                          "beyond", "both", "but", "by", "can", "cannot", "canst", "certain", "cf",
                                          "choose", "contrariwise", "cos", "could", "cu", "day", "do", "does",
                                          "doing", "dost", "doth", "double", "down", "dual", "during", "each",
                                          "either", "else", "elsewhere", "enough", "et", "etc", "even", "ever",
                                          "every", "everybody", "everyone", "everything", "everywhere", "except",
                                          "excepted", "excepting", "exception", "exclude", "excluding", "exclusive",
                                          "far", "farther", "farthest", "few", "ff", "first", "for", "formerly",
                                          "forth", "forward", "from", "front", "further", "furthermore", "furthest",
                                          "get", "go", "had", "halves", "hardly", "has", "hast", "hath", "have",
                                          "he", "hence", "henceforth", "her", "here", "hereabouts", "hereafter",
                                          "hereby", "herein", "hereto", "hereupon", "hers", "herself", "him",
                                          "himself", "hindmost", "his", "hither", "hitherto", "how", "however",
                                          "howsoever", "i", "ie", "if", "in", "inasmuch", "inc", "include",
                                          "included", "including", "indeed", "indoors", "inside", "insomuch",
                                          "instead", "into", "inward", "inwards", "is", "it", "its", "itself",
                                          "just", "kind", "kg", "km", "last", "latter", "latterly", "less", "lest",
                                          "let", "like", "little", "ltd", "many", "may", "maybe", "me", "meantime",
                                          "meanwhile", "might", "moreover", "most", "mostly", "more", "mr", "mrs",
                                          "ms", "much", "must", "my", "myself", "namely", "need", "neither",
                                          "never", "nevertheless", "next", "no", "nobody", "none", "nonetheless",
                                          "noone", "nope", "nor", "not", "nothing", "notwithstanding", "now",
                                          "nowadays", "nowhere", "of", "off", "often", "ok", "on", "once", "one",
                                          "only", "onto", "or", "other", "others", "otherwise", "ought", "our",
                                          "ours", "ourselves", "out", "outside", "over", "own", "per", "perhaps",
                                          "plenty", "provide", "quite", "rather", "really", "round", "said", "sake",
                                          "same", "sang", "save", "saw", "see", "seeing", "seem", "seemed",
                                          "seeming", "seems", "seen", "seldom", "selves", "sent", "several",
                                          "shalt", "she", "should", "shown", "sideways", "since", "slept", "slew",
                                          "slung", "slunk", "smote", "so", "some", "somebody", "somehow", "someone",
                                          "something", "sometime", "sometimes", "somewhat", "somewhere", "spake",
                                          "spat", "spoke", "spoken", "sprang", "sprung", "stave", "staves", "still",
                                          "such", "supposing", "than", "that", "the", "thee", "their", "them",
                                          "themselves", "then", "thence", "thenceforth", "there", "thereabout",
                                          "thereabouts", "thereafter", "thereby", "therefore", "therein", "thereof",
                                          "thereon", "thereto", "thereupon", "these", "they", "this", "those",
                                          "thou", "though", "thrice", "through", "throughout", "thru", "thus",
                                          "thy", "thyself", "till", "to", "together", "too", "toward", "towards",
                                          "ugh", "unable", "under", "underneath", "unless", "unlike", "until", "up",
                                          "upon", "upward", "upwards", "us", "use", "used", "using", "very", "via",
                                          "vs", "want", "was", "we", "week", "well", "were", "what", "whatever",
                                          "whatsoever", "when", "whence", "whenever", "whensoever", "where",
                                          "whereabouts", "whereafter", "whereas", "whereat", "whereby", "wherefore",
                                          "wherefrom", "wherein", "whereinto", "whereof", "whereon", "wheresoever",
                                          "whereto", "whereunto", "whereupon", "wherever", "wherewith", "whether",
                                          "whew", "which", "whichever", "whichsoever", "while", "whilst", "whither",
                                          "who", "whoa", "whoever", "whole", "whom", "whomever", "whomsoever",
                                          "whose", "whosoever", "why", "will", "wilt", "with", "within", "without",
                                          "worse", "worst", "would", "wow", "ye", "yet", "year", "yippee", "you",
                                          "your", "yours", "yourself", "yourselves"]
                        }
                    },
                    "analyzer": {
                        "stopped": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "porter_stem",
                                "english_stop"
                            ]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "_size": {
                        "enabled": True
                    },
                    "text": {
                        "type": "text",
                        "fielddata": True,
                        "analyzer": "stopped",
                        "index_options": "positions"
                    },
                    "id": {
                        "type": "keyword",
                        "index": True
                    },
                    "raw_content": {
                        "type": "keyword",
                        "index": True
                    },
                    "label": {
                        "type": "keyword",
                        "index": True
                    },
                    "split": {
                        "type": "keyword",
                        "index": True
                    }
                }
            }
        }

        print("creating " + self.INDEX_NAME + " index...")
        res = self.es.indices.create(index=self.INDEX_NAME, body=request_body)
        print(" response: '%s'" % res)

    def index_data(self, data):
        bulk_data = []  # list of all emails to be indexed

        # data[url] = {"id": url, "text": text, # "inlinks": (set)inlinks[url], "outlinks": (set)outlinks}
        for key in data:
            data_refined = {
                "_index": self.INDEX_NAME,
                "_id": str(key),
                "_source": data[key]
            }
            bulk_data.append(data_refined)

        print(len(bulk_data))
        print("----------------Indexing bulk data--------------------")
        try:
            res = helpers.bulk(self.es, bulk_data)
            print(res)
        except Exception:
            print("Indexing failed")
