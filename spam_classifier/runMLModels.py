from pandas import np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB

from getTrainTestData import prepareTrainingDataPart1, read_data_from_ES
from getTrainTestData import prepareTrainingDataPart2

part1Flag = True


def rank_docs(predicted_probability_nb, testing_index):
    test_spam_score_dict = dict()
    print(predicted_probability_nb)
    for i in range(0, len(predicted_probability_nb)):
        test_spam_score_dict[testing_index[i]] = predicted_probability_nb[i]

    top_spam_docs = sorted(test_spam_score_dict.items(), key=lambda x: x[1], reverse=True)[:100]
    print("Top spam docs are: ")
    print(top_spam_docs)

    with open('./top100SpamDocs', mode='w') as file:
        for tup in top_spam_docs:
            file.write(tup[0] + "\n")
    file.close()
    pass


if __name__ == "__main__":
    if part1Flag:
        fitted_x_train, y_train, transformed_x_test, y_test, testing_index = prepareTrainingDataPart1()
    else:
        fitted_x_train, y_train, transformed_x_test, y_test, testing_index = prepareTrainingDataPart2()

    print("Training for linear regression.........")
    lr = LogisticRegression(penalty='l1', solver="liblinear")
    lr.fit(fitted_x_train, y_train)
    predicted_probability = lr.predict_proba(transformed_x_test)
    print(predicted_probability)

    predicted_probability_lr = lr.predict_proba(transformed_x_test)[:, 1]
    score = roc_auc_score(np.array(y_test), predicted_probability_lr)
    print("Roc auc score for linear regression " + str(score))

    print("Training for decision tree........")
    dt = DecisionTreeClassifier()
    dt.fit(fitted_x_train, y_train)
    predicted_probability_dt = dt.predict_proba(transformed_x_test)[:, 1]
    score = roc_auc_score(np.array(y_test), predicted_probability_dt)
    print("Roc auc score for decision tree " + str(score))

    print("Training for naive bayes........")
    nb = MultinomialNB()
    nb.fit(fitted_x_train, y_train)
    predicted_probability_nb = nb.predict_proba(transformed_x_test)[:, 1]
    score = roc_auc_score(np.array(y_test), predicted_probability_nb)
    print("Roc auc score for naive bayes "+str(score))

    rank_docs(predicted_probability_lr, testing_index)
