import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score


def pre_process_data_w_target(file_path):
    data = pd.read_csv(file_path)
    df = data.copy()
    df_relevant = df[['Client_Income', 'House_Own', 'Credit_Amount', 'Client_Marital_Status', 'Client_Gender',
                      'Age_Days', 'Employed_Days', 'Client_Family_Members', 'Default']]
    removed_null = df_relevant.dropna()
    removed_null1 = removed_null.astype({'Credit_Amount': float})
    removed_null1 = removed_null1.astype({'Client_Income': float})
    removed_null1 = removed_null1.astype({'House_Own': float})
    removed_null1 = removed_null1.astype({'Age_Days': float})
    removed_null1 = removed_null1.astype({'Employed_Days': float})
    removed_null1 = removed_null1.astype({'Client_Family_Members': float})
    removed_null1 = removed_null1.astype({'Default': float})
    train_data = removed_null1.copy()

    marital_dict = {"M": 0, "W": 1, "S": 2, "D": 3}
    gender_dict = {"Male": 0, "Female": 1}
    train_data['Client_Marital_Status'] = (train_data['Client_Marital_Status'].map(marital_dict))
    train_data['Client_Gender'] = (train_data['Client_Gender'].map(gender_dict))

    x = train_data.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7]]
    y = train_data.iloc[:, 8]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)

    return x_train, x_test, y_train, y_test


def pre_process_data_wo_target(file_path):
    data = pd.read_csv(file_path)
    df = data.copy()
    df_relevant = df[
        ['Client_Income', 'House_Own', 'Credit_Amount', 'Client_Marital_Status', 'Client_Gender',
         'Age_Days', 'Employed_Days', 'Client_Family_Members']]
    removed_null = df_relevant.dropna()
    removed_null1 = removed_null.astype({'Credit_Amount': float})
    removed_null1 = removed_null1.astype({'Client_Income': float})
    removed_null1 = removed_null1.astype({'House_Own': float})
    removed_null1 = removed_null1.astype({'Age_Days': float})
    removed_null1 = removed_null1.astype({'Employed_Days': float})
    removed_null1 = removed_null1.astype({'Client_Family_Members': float})
    testing_data = removed_null1.copy()

    marital_dict = {"M": 0, "W": 1, "S": 2, "D": 3}
    gender_dict = {"Male": 0, "Female": 1}
    testing_data['Client_Marital_Status'] = (testing_data['Client_Marital_Status'].map(marital_dict))
    testing_data['Client_Gender'] = (testing_data['Client_Gender'].map(gender_dict))

    x_unknown_predict = testing_data.iloc[:, 0:9]

    return x_unknown_predict


def create_model(train_data_path):
    x_train, x_test, y_train, y_test = pre_process_data_w_target(train_data_path)

    classifier = LogisticRegression()

    classifier.fit(x_train, y_train)

    return classifier


def test_classifier_accuracy(train_data_path):
    classifier = create_model(train_data_path)

    x_train, x_test, y_train, y_test = pre_process_data_w_target(train_data_path)

    y_predict = classifier.predict(x_test)

    conf_matrix = confusion_matrix(y_test, y_predict)
    print(conf_matrix)

    acc_score = accuracy_score(y_test, y_predict)
    print(acc_score)


def test_classifier_bands(train_data_path):
    classifier = create_model(train_data_path)
    x_train, x_test, y_train, y_test = pre_process_data_w_target(train_data_path)

    y_predict = classifier.predict(x_test)

    probability = classifier.predict_proba(x_test)

    df_prediction_prob = pd.DataFrame(probability, columns=['prob_0', 'prob_1'])
    df_prediction_target = pd.DataFrame(y_predict, columns=['predicted_TARGET'])
    df_test_dataset = pd.DataFrame(y_test, columns=['Actual Outcome'])

    dfx = pd.concat([df_test_dataset, df_prediction_prob, df_prediction_target], axis=1)

    df1 = dfx.sort_values(
        by="prob_0",
        ascending=False)

    decile_pre_divide = len(dfx) - len(dfx) % 40
    decile_pre_divide2 = decile_pre_divide / 40
    splitter = decile_pre_divide2

    band12 = df1.iloc[[1 * splitter], [1]].values
    band13 = df1.iloc[[2 * splitter], [1]].values
    band14 = df1.iloc[[3 * splitter], [1]].values
    band15 = df1.iloc[[4 * splitter], [1]].values
    band16 = df1.iloc[[5 * splitter], [1]].values
    band17 = df1.iloc[[6 * splitter], [1]].values
    band18 = df1.iloc[[7 * splitter], [1]].values
    band19 = df1.iloc[[8 * splitter], [1]].values
    band20 = df1.iloc[[9 * splitter], [1]].values
    bands = [band12, band13, band14, band15, band16, band17, band18, band19, band20]

    print(bands)
    return bands


def predict_from_generated_customer(predict_data_path, train_data_path):
    classifier = create_model(train_data_path)

    bands = test_classifier_bands(train_data_path)
    x_unknown_predict = pre_process_data_wo_target(predict_data_path)
    df = classifier.predict(x_unknown_predict)
    df_proba = classifier.predict_proba(x_unknown_predict)

    x_unknown_predict['prob_0'] = df_proba[:, [0]]
    x_unknown_predict['Band'] = 10

    for i in range(len(x_unknown_predict)):
        locator = int(i)
        predicted_probability = x_unknown_predict.iloc[locator, 8]
        band_to_assign = 10
        if float(predicted_probability) >= float(bands[0]):
            band_to_assign = 1
        elif float(predicted_probability) >= float(bands[1]):
            band_to_assign = 2
        elif float(predicted_probability) >= float(bands[2]):
            band_to_assign = 3
        elif float(predicted_probability) >= float(bands[3]):
            band_to_assign = 4
        elif float(predicted_probability) >= float(bands[4]):
            band_to_assign = 5
        elif float(predicted_probability) >= float(bands[5]):
            band_to_assign = 6
        elif float(predicted_probability) >= float(bands[6]):
            band_to_assign = 7
        elif float(predicted_probability) >= float(bands[7]):
            band_to_assign = 8
        elif float(predicted_probability) >= float(bands[8]):
            band_to_assign = 9
        else:
            continue
        x_unknown_predict.iloc[[locator], [9]] = band_to_assign
    return x_unknown_predict
