# 고급 Streamlit 앱 예제 (머신러닝 모델을 활용한 데이터 분석 앱)

import streamlit as st
import pandas as pd
import numpy as np

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

# 앱 타이틀
st.title("고급 Streamlit 앱: 머신러닝 데이터 분석")

# 데이터 로딩
@st.cache_data
def load_data():
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
    return df

df = load_data()
st.write("아이리스 데이터셋:", df.head())

# 사용자 입력 위젯
st.sidebar.header("모델 파라미터 설정")
n_estimators = st.sidebar.slider("나무의 개수 (n_estimators):", min_value=10, max_value=200, value=50)
max_depth = st.sidebar.slider("나무의 최대 깊이 (max_depth):", min_value=1, max_value=20, value=5)
test_size = st.sidebar.slider("테스트 데이터 비율:", min_value=0.1, max_value=0.5, value=0.2)

# 데이터 분리
X = df.iloc[:, :-1]
y = df["species"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=42, stratify=y
)

# 모델 학습
model = RandomForestClassifier(
    n_estimators=n_estimators,
    max_depth=max_depth,
    random_state=42
)
model.fit(X_train, y_train)

# 예측 및 성능 평가
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

st.subheader("모델 성능")
st.write(f"정확도(Accuracy): **{acc:.4f}**")

# 혼동 행렬
st.subheader("혼동 행렬(Confusion Matrix)")
cm = confusion_matrix(y_test, y_pred, labels=model.classes_)

fig, ax = plt.subplots()
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=model.classes_,
    yticklabels=model.classes_,
    ax=ax
)
ax.set_xlabel("Predicted")
ax.set_ylabel("True")
st.pyplot(fig)

# (옵션) 특성 중요도
st.subheader("특성 중요도(Feature Importance)")
fi = pd.DataFrame(
    {"feature": X.columns, "importance": model.feature_importances_}
).sort_values("importance", ascending=False)

st.dataframe(fi, use_container_width=True)

fig2, ax2 = plt.subplots()
ax2.bar(fi["feature"], fi["importance"])
ax2.set_xticklabels(fi["feature"], rotation=45, ha="right")
ax2.set_ylabel("Importance")
st.pyplot(fig2)
