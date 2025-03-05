import shap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.datasets import fetch_california_housing #캘리포이나 주택 데이터
import ssl
ssl._create_default_https_context = ssl._create_stdlib_context

import warnings #경고 무시
warnings.filterwarnings('ignore')

data = fetch_california_housing()
df = pd.DataFrame(data.data, columns = data.feature_names)
df['target'] = data.target

X = df.drop(columns=['target'])
y = df['target']
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,
                                                 random_state=42)
model = DecisionTreeRegressor(max_depth=4,random_state=42)
model.fit(X_train,y_train)

#shap 값 계산
explaniner = shap.Explainer(model,X_train)
shap_value = explaniner(X_test)

#shap 시각화.
# 1.Feature_importance 시각화(summary plot)
shap.summary_plot(shap_value, X_test)

# 2. Feature importance 시각화(bar plot)
shap.summary_plot(shap_value, X_test, plot_type='bar')

#3. 특징 피쳐에 대한 shap 분포 시각화.
shap.dependence_plot('MedInc',shap_value.values,X_test)
plt.show()