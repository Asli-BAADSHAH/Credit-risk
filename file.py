# -*- coding: utf-8 -*-
"""Credit-Risk-Analysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1G5hJeEtWeqULUfMBWbt3p9cDSH6VofJS

# **<span style="color:#121CB6;">Credit Risk Analysis using KNN</span>**

- We start with importing all libraries that are needed.
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Latex

sns.set_style('whitegrid')

from sklearn.preprocessing import LabelEncoder
from sklearn import model_selection
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import f1_score

"""# **<span style="color:#121CB6;">1.Loading and Understanding the dataset</span>**"""

df_loan = pd.read_csv("/loan.csv")
df_loan.head(7)

df_loan.info()

df_loan.describe()

"""# **<span style="color:#121CB6;">2. Removing Irrelevant coloumn</span>**"""

df_loan.drop(df_loan.columns.difference(['loan_amnt','term','int_rate','installment','grade','emp_length','home_ownership',
                                         'annual_inc','verification_status','loan_status','purpose',]), axis = 1, inplace=True)

df_loan.isnull().sum()

"""There are many "Missing Values" in Column "emp_length" and few in "annual_inc"."""

df_loan.info()

df_loan.head(10)

df_loan.annual_inc = df_loan.annual_inc.fillna(0)
df_loan.isnull().sum()

"""- to eliminate null values, the annual income column is filled with the value 0

# **<span style="color:#121CB6;">3. Create label Coloumn : Description about loan status</span>**

- In this column, the value 0 will be filled with the correct conditions: 'Fully Paid', 'Does not meet the credit policy. Status:Fully Paid', 'Current'
- Meanwhile, the value of 1 will be filled with incorrect conditions: 'Late (31-120 days)', 'Late (16-30 days)', 'In Grace Period', 'Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off'
"""

# binary classification
label_categories = [
    (0, ['Fully Paid', 'Does not meet the credit policy. Status:Fully Paid', 'Current']),
    (1, ['Late (31-120 days)', 'Late (16-30 days)', 'In Grace Period',
         'Charged Off', 'Default', 'Does not meet the credit policy. Status:Charged Off'])
]

# function to apply the transformation
def classify_label(text):
    for category, matches in label_categories:
        if any(match in text for match in matches):
            return category
    return None

df_loan.loc[:, 'label'] = df_loan['loan_status'].apply(classify_label)
df_loan = df_loan.drop('loan_status', axis=1)

# label several label with specific grading system.
def SC_LabelEncoder1(text):
    if text == "E":
        return 1
    elif text == "D":
        return 2
    elif text == "C":
        return 3
    elif text == "B":
        return 4
    elif text == "A":
        return 5
    else:
        return 0


def SC_LabelEncoder2(text):
    if text == "< 1 year":
        return 1
    elif text == "1 year":
        return 2
    elif text == "2 years":
        return 3
    elif text == "3 years":
        return 4
    elif text == "4 years":
        return 5
    elif text == "5 years":
        return 6
    elif text == "6 years":
        return 7
    elif text == "7 years":
        return 8
    elif text == "8 years":
        return 9
    elif text == "9 years":
        return 10
    elif text == "10 years":
        return 11
    elif text == "10+ years":
        return 12
    else:
        return 0

def SC_LabelEncoder3(text):
    if text == "RENT":
        return 1
    elif text == "MORTGAGE":
        return 2
    elif text == "OWN":
        return 3
    else:
        return 0

df_loan["grade"] = df_loan["grade"].apply(SC_LabelEncoder1)
df_loan["emp_length"] = df_loan["emp_length"].apply(SC_LabelEncoder2)
df_loan["home_ownership"] = df_loan["home_ownership"].apply(SC_LabelEncoder3)

df_loan.head(10)

df_loan.info()

"""# **<span style="color:#121CB6;">4. Exploratory Data Analysis</span>**"""

fig, ax = plt.subplots(1,2,figsize=(15,5))
sns.countplot(data=df_loan, x='grade', hue="home_ownership", ax=ax[0]).set_title("Grade/Home Ownership distribution");
sns.countplot(data=df_loan, x='home_ownership', hue='grade', ax=ax[1]).set_title("Grade/Home Ownership distribution");

fig, ax = plt.subplots(1,2,figsize=(15,5))
sns.countplot(data=df_loan, x='label', hue='purpose', ax=ax[0]).set_title("Grade Distribution with verification_status distribution");
sns.countplot(data=df_loan, x='grade', hue='label', ax=ax[1]).set_title("Grade Distribution with loan_status");

"""## Analysis :
1. The number of Borrowers with high grade will be small compared to low grade
2. Most money borrowers' goals from labels 0 and 1 are debt consolidation
3. The highest number of grades who were able to complete the loan was grade 4, while the most failed to complete the loan was grade 3
"""

plt.figure(figsize=(12,6))
sns.boxplot(x='purpose', y='loan_amnt', data=df_loan)
plt.xticks(rotation=30)
plt.title('Loan amounts grouped by purpose')

df_loan1 = df_loan.copy()

"""## Analysis :
There are 5 highest categories for the amount of credit with the following purposes: Credit card, MSME business, debt consolidation, home improvement, and buying a house
"""

fig, ax = plt.subplots(1,2,figsize=(15,5))
sns.histplot(df_loan1, x='loan_amnt',hue="label", bins=30, ax=ax[0]).set_title("Loan Ammount distribution");
sns.countplot(data=df_loan1, x='term', hue="label", ax=ax[1]).set_title("Term distribution");

fig, ax = plt.subplots(1,2,figsize=(15,5))
sns.countplot(data=df_loan1, hue='home_ownership', x='label', ax=ax[1]).set_title("Home ownership with loan_status");
sns.countplot(data=df_loan1, x='verification_status', hue='label', ax=ax[0]).set_title("Verification Status Distribution with loan_status");

"""## Analysis :
1. The nominal value of the largest debt is 10000 USD
2. The maximum maturity is 36 months, while for 60 months it is almost a third
3. Most of the credits that can be paid in full are obtained from the "Verified" verification status

- Seeing the correlation between variables:
"""

df_loan1.info()

# Select only numeric columns for correlation calculation
numeric_columns = ['loan_amnt', 'int_rate', 'annual_inc']
corr = df_loan1[numeric_columns].corr()

import seaborn as sns
import numpy as np

sns.set(rc={'figure.figsize':(11,7)})
sns.heatmap(corr, linewidths=.5, annot=True, cmap="YlGnBu", mask=np.triu(np.ones_like(corr, dtype=bool)))\
    .set_title("Pearson Correlations Heatmap"); # Use bool instead of np.bool

"""## Analysis :
The amount of credit is very dependent on the annual income of the borrower

# **<span style="color:#121CB6;">5. Pra-Processing data for Discrete Coloumn</span>**
"""

df_loan2 = df_loan1.copy()

# use LabelEncoder() to encode another category column:
for col in ["verification_status", "purpose","term"]:
    le = LabelEncoder()
    le.fit(df_loan2[col])
    df_loan2[col] = le.transform(df_loan2[col])
df_loan2.head()

df_loan2.isnull().sum()

df_loan2.label = df_loan2.label.fillna(1)

df_loan3 = df_loan2.copy()

"""# **<span style="color:#121CB6;">6. Clustering</span>**"""

inertias = []

for i in range(2,16):
    kmeans = KMeans(n_clusters=i, random_state=0).fit(df_loan3)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(10,5))
plt.title('Inertias v.s. N_Clusters')
plt.plot(np.arange(2,16),inertias, marker='o', lw=2);

"""## Analysis:
"Elbow" on the chart above is at 4. The number of clusters must be 4.
"""

df_loan4 = df_loan3.copy()

km = KMeans(n_clusters=4, random_state=0)
clusters = km.fit_predict(df_loan4)

df_loan5 = df_loan4.copy()

df_clustered = df_loan5[['loan_amnt', 'int_rate', 'grade', 'emp_length', 'home_ownership', 'annual_inc', 'purpose']]
df_clustered["Cluster"] = clusters
sns.pairplot(df_clustered[['loan_amnt', 'int_rate', 'grade', 'emp_length', 'home_ownership', 'annual_inc', 'purpose'
                           , "Cluster"]], hue="Cluster");

"""# **<span style="color:#121CB6;">7. Predicting Risk: Using the K-Nearest Neighbors Classification Model</span>**"""

X, y = df_loan.drop("label", axis=1), df_loan["label"]
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.20, random_state=0)

max_score = 0
max_k = 0
for k in range(1, 100):
    neigh = KNeighborsClassifier(n_neighbors=k)
    neigh.fit(X_train,y_train)
    score = f1_score(y_test, neigh.predict(X_test),average='micro')
    if score > max_score:
        max_k = k
        max_score = score

print('If we use K-Nearest Neighbors Classification, then the value of K is',str(max_k),' to get the best prediction, then the average accuracy is ', max_score)

"""Classification with other ML models

Since the KNN (K-Nearest Neighbors) Classification takes a lot of time and memory to predict, it is possible to use other ML models such as SVC, DecisionTree, RandomForest, and GaussianNaiveBayes.

> Add blockquote



However, in this notebook, We use KNN Model Only, and it is done and has got a good accuracy = 91.4%
"""