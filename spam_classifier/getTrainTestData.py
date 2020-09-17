from scipy.sparse import csr_matrix

from createIndex import Index
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.datasets import dump_svmlight_file
import pandas

TRAIN_DATA_FILE = './dumpTrainingData'
TEST_DATA_FILE = './dumpTestingData'
GIVEN_FEATURE_FILE = "./features"
MY_FEATURE_FILE = "./my_features"
my_feature_flag = True


def read_data_from_ES(split_value):
    query_body = {
        "query": {
            "term": {
                "split": {
                    "value": split_value}
            }
        },
        "size": 80000,
        "_source": ["id", "text", "label", "split"]
    }
    waterloo_index = Index()
    res = waterloo_index.es.search(index=waterloo_index.INDEX_NAME, body=query_body)
    print(len(res["hits"]["hits"]))

    email_data = dict()
    for i in range(0, len(res["hits"]["hits"])):
        if res["hits"]["hits"][i]["_source"]["text"] in [" - ", " - \n"] or res["hits"]["hits"][i]["_source"][
            "text"] is None:
            res["hits"]["hits"][i]["_source"]["text"] = ""
        email_data[res["hits"]["hits"][i]["_id"]] = {"text": res["hits"]["hits"][i]["_source"]["text"],
                                                     "label": res["hits"]["hits"][i]["_source"]["label"]}
    return email_data


def read_features_from_ES(custom_features):
    print("Querying es for all features")
    feature_data = dict()
    for feature in custom_features:
        query_body = {
            "query": {
                "intervals": {
                    "text": {
                        "match": {
                            "query": feature,
                            "max_gaps": 5
                        }
                    }
                }
            },
            "size": 70000,
            "_source": ["id"]
        }
        waterloo_index = Index()
        res = waterloo_index.es.search(index=waterloo_index.INDEX_NAME, body=query_body)

        for i in range(0, len(res["hits"]["hits"])):
            if res["hits"]["hits"][i]["_id"] not in feature_data:
                feature_data[res["hits"]["hits"][i]["_id"]] = list()
            feature_data[res["hits"]["hits"][i]["_id"]].append(feature)
    return feature_data


def refine_data(train_dat, test_dat):
    training_df = pandas.DataFrame.from_dict(train_dat, orient='index')
    testing_df = pandas.DataFrame.from_dict(test_dat, orient='index')

    x_train = training_df["text"]
    y_train = training_df["label"]
    training_index = list(training_df.index)

    x_test = testing_df["text"]
    y_test = testing_df["label"]
    testing_index = testing_df.index

    for index, v in y_train.items():
        if y_train[index] == "spam":
            y_train[index] = '1'
        else:
            y_train[index] = '0'

    for index, v in y_test.items():
        if y_test[index] == "spam":
            y_test[index] = '1'
        else:
            y_test[index] = '0'

    return x_train, y_train, x_test, y_test, training_index, testing_index


def get_top_spam_words(fitted_x_train, vocab):
    print("Get top spam words")
    freq = pandas.np.ravel(fitted_x_train.sum(axis=0))

    freq_dict = dict()
    term_freq_dict = dict()
    for i in range(0, len(freq)):
        freq_dict[i] = {"freq": freq[i], "word": ""}

    for v in vocab.keys():
        id = vocab[v]
        freq_dict[id]["word"] = v
        term_freq_dict[v] = freq_dict[id]["freq"]

    stopwords = ["html", "font", "http", "com", "color", "www", "org", "style", "sans", "href",
                 "text", "arial", "serif", "border", "span", "helvetica", "src", "https", "margin",
                 "height", "width", "align", "br", "bold", "verdana", "nbsp", "img",
                 "a", "about", "above", "according", "across", "after", "afterwards",
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
    for sw in stopwords:
        if sw in term_freq_dict:
            del term_freq_dict[sw]

    top_spam_terms = sorted(term_freq_dict.items(), key=lambda x: x[1], reverse=True)[:500]

    print("Writing top 500 spam words")
    with open('./top500SpamTerms', mode='w') as file:
        for tup in top_spam_terms:
            file.write(str(tup[0]) + " " + str(tup[1]) + "\n")
    file.close()


def get_ngram_doc_matches_from_ES(docs, custom_features):
    feature_dict = read_features_from_ES(custom_features)
    print("Docs with features present = "+str(len(feature_dict)))

    row = [0]
    col = []
    data = []
    vocabulary = {}

    for d in docs:
        for feature in custom_features:
            index = vocabulary.setdefault(feature, len(vocabulary))
            col.append(index)
            if str(d) in feature_dict:
                if feature in feature_dict[str(d)]:
                    data.append(1)
                else:
                    data.append(0)
            else:
                data.append(0)
        row.append(len(col))

    # print(vocabulary)
    print(len(col))
    print(len(row))
    print("-----------------------------------")
    sparse_feature_matrix = csr_matrix((data, col, row), dtype=int)
    # print(sparse_feature_matrix)
    # print(sparse_feature_matrix.toarray())
    # exit()
    return sparse_feature_matrix


def prepareTrainingDataPart2():
    train_data = read_data_from_ES("train")
    test_data = read_data_from_ES("test")

    x_train, y_train, x_test, y_test, training_index, testing_index = refine_data(train_data, test_data)

    stop_list = ["html", "font", "http", "com", "color", "www", "org", "style", "sans", "href",
                 "text", "arial", "serif", "border", "span", "helvetica", "src", "https", "margin",
                 "height", "width", "align", "br", "bold", "verdana", "nbsp", "img"]

    print("Getting the vectorizer for part 2")
    vectorizer = CountVectorizer(analyzer='word', min_df=0.001, max_df=0.995, stop_words=stop_list)

    fitted_x_train = vectorizer.fit_transform(x_train)
    print(vectorizer.vocabulary_)

    get_top_spam_words(fitted_x_train, vectorizer.vocabulary_)

    transformed_x_test = vectorizer.transform(x_test)

    # get_most_popular_spam_words(vectorizer.vocabulary_, fitted_x_train)
    print("-----Fitted x train--------")
    print(fitted_x_train)
    print(type(fitted_x_train))
    print(type(fitted_x_train.toarray()))

    for line in fitted_x_train:
        print(line)
        break
    for line in fitted_x_train.toarray():
        print(line)
        break

    print("-----Fitted x test--------")
    print(transformed_x_test)
    print(type(transformed_x_test))
    print(type(transformed_x_test.toarray()))

    for line in transformed_x_test:
        print(line)
        break

    dump_svmlight_file(fitted_x_train, y_train, TRAIN_DATA_FILE)

    return fitted_x_train, y_train, transformed_x_test, y_test, testing_index


def prepareTrainingDataPart1():
    train_data = read_data_from_ES("train")
    test_data = read_data_from_ES("test")
    x_train, y_train, x_test, y_test, training_index, testing_index = refine_data(train_data, test_data)

    print(x_train)
    print(y_train)
    print("Getting the feature for part 1")
    if my_feature_flag:
        with open(MY_FEATURE_FILE, mode='r') as feature_file:
            custom_features = list(set(feature_file.read().split("\n")))
        feature_file.close()
    else:
        with open(GIVEN_FEATURE_FILE, mode='r') as feature_file:
            custom_features = list(set(feature_file.read().split()))
        feature_file.close()

    new_list = list()
    for i in range(0, len(custom_features)):
        custom_features[i] = custom_features[i].strip()
        if len(custom_features[i].split()) > 1:
            for x in custom_features[i].split():
                new_list.append(x)

    custom_features = list(set(custom_features + new_list))
    # print(custom_features)
    # print(len(custom_features))
    # print(training_index)
    # print(testing_index)

    # for all docs for all features

    fitted_x_train = get_ngram_doc_matches_from_ES(training_index, custom_features)
    transformed_x_test = get_ngram_doc_matches_from_ES(testing_index, custom_features)

    print("-----Fitted x train--------")
    print(fitted_x_train)
    print("-----Fitted x test--------")
    print(transformed_x_test)

    dump_svmlight_file(fitted_x_train, y_train, TRAIN_DATA_FILE)

    return fitted_x_train, y_train, transformed_x_test, y_test, testing_index
