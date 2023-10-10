import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from joblib import dump

def compute_model_score(model, X, y):
    # computing cross val
    cross_validation = cross_val_score(
        model,
        X,
        y,
        cv=3,
        scoring='neg_mean_squared_error')

    model_score = cross_validation.mean()

    return model_score


def train_and_save_model(model, X, y, path_to_model='/app/model.pckl'):
    # training the model
    model.fit(X, y)
    # saving model
    print(str(model), 'saved at ', path_to_model)
    dump(model, path_to_model)


def prepare_data(path_to_data='/app/clean_data/fulldata.csv'):
    # reading data
    df = pd.read_csv(path_to_data)
    # ordering data according to city and date
    df = df.sort_values(['city', 'date'], ascending=True)

    dfs = []

    for c in df['city'].unique():
        df_temp = df[df['city'] == c].copy()

        # creating target
        df_temp.loc[:, 'target'] = df_temp['temperature'].shift(1)

        # creating features
        for i in range(1, 10):
            df_temp.loc[:, 'temp_m-{}'.format(i)
                        ] = df_temp['temperature'].shift(-i)

        # deleting null values
        df_temp = df_temp.dropna()

        dfs.append(df_temp)

    # concatenating datasets
    df_final = pd.concat(
        dfs,
        axis=0,
        ignore_index=False
    )

    # deleting date variable
    df_final = df_final.drop(['date'], axis=1)

    # creating dummies for city variable
    df_final = pd.get_dummies(df_final)

    features = df_final.drop(['target'], axis=1)
    target = df_final['target']

    return features, target


def compute_lr_score(task_instance):
    X, y = prepare_data()
    task_instance.xcom_push(
        key="lr_score",
        value=compute_model_score(LinearRegression(), X, y)
    )

def compute_dt_score(task_instance):
    X, y = prepare_data()
    task_instance.xcom_push(
        key="dt_score",
        value=compute_model_score(DecisionTreeRegressor(), X, y)
    )

def compute_rf_score(task_instance):
    X, y = prepare_data()
    task_instance.xcom_push(
        key="rf_score",
        value=compute_model_score(RandomForestRegressor(), X, y)
    )


def save_best_model(task_instance):
    scores = {
        'lr': task_instance.xcom_pull(key = "lr_score",task_ids = "compute_lr_score"),
        'dt': task_instance.xcom_pull(key = "dt_score",task_ids = "compute_dt_score"),
        'rf': task_instance.xcom_pull(key = "rf_score",task_ids = "compute_rf_score")
         }
    best_model=max(scores, key=scores.get)

    models = {
        'lr': LinearRegression(),
        'dt': DecisionTreeRegressor(),
        'rf': RandomForestRegressor()
    }
    X, y = prepare_data()
    train_and_save_model(
        models[best_model],
        X,
        y,
        '/app/clean_data/best_model.pickle')

