청주 2기 : 하이퍼 파라미터 최적화 : https://colab.research.google.com/drive/1LdepmBnDPV3SWC4mRuGv9ca4_CRbYy2U?usp=sharing
청주 2기 : xgboost : https://colab.research.google.com/drive/1u61-s_zhbp4WPE9SObThqHAUs3GqHB-z?usp=sharing

## 강의안 목록입니다.

강의안은 pdf로 구성되어 있거나 실습파일은 .ipynb입니다. 원본 강의안은 공개가 불가능합니다.


## 00.빅데이터 기초
 - 빅데이터/인공지능 기초에 대해 강의안이 구성되어 있습니다.

## 01.머신러닝 소개

## 02. 빅데이터를 위한 수학
1) 선형대수학
2) 다변수 미적분학과 최적화
3) 확률과 통계

## 03.파이썬 (초급부터 고급 / 약간의 자료구조)
 1) 소개
 2) 기본
 3) 자료형
 4) 조건문
 5) 반복문
 6) 파일 읽기/쓰기
 7) 함수
 8) 클래스 모듈
 9) 예외처리

- 중간중간에 연습문제가 들어있습니다. 수업시간에만 답안을 공개합니다.

## 04. Numpy(선형대수학)
1) list VS numpy
2) Numpy의 장점
3) 선형대수학 개념 강의 및 실습

## 05. Pandas(CSV 포맷 처리)

## 06. Matplotlib(그림 그리기)  / seaborn / plotly 

============================Machine Learning============================
## 07. 사이킷런으로 배우는 머신러닝

## 08. 회귀 분석
1) 회귀 분석이란?
2) 경사하강법 소개 및 증명
3) 회귀의 평가(R^2, adjusted R^2, AIC,BIC)
4) P-value
5) Ordinary Least Square 증명 및 Ridge,Lasso,Elastics 증명
6) Bais VS Variance
7) 데이터 변환
8) Logistic Regression(증명 및 오즈비 소개)
9) Possion Regression 소개

Mixture Model 소개

#### 실습 : 
1) Sklearn tutorial with Boston House Dataset -> Kfold도 소개
2) sklearn tutorial with load_diabetes
3) sklearn tutorial Wisconsin (diagnostic) dataset
4) kaggle Titanic dataset

HW : House advanced regression problem

## 09. 분류
1) k-nearest neighbors
2) Naive Bayes
3) Decison Tree
4) Random Forest
5) AdaBoosting
6) Gradient Boosting
7) XGboost
8) LightGBM
9) Catboost
Hyperparamter 자동 : optnua /  Imblanced data
11) Ensemble learning(bagging,boosting,voting,Stacking)

### 실습 : 
1) Mushroom Classification (https://www.kaggle.com/uciml/mushroom-classification)
2) Otto Group Product Classification Challenge (https://www.kaggle.com/c/otto-group-product-classification-challenge)
3) Cardiovascular Disease(https://www.kaggle.com/sulianova/cardiovascular-disease-dataset)
4) Prudential Life Insurance Assessment(https://www.kaggle.com/c/prudential-life-insurance-assessment)
5) Imbalanced Data(Credit Card Fraud Detection(https://www.kaggle.com/mlg-ulb/creditcardfraud))

## 분류-2
1) Support Vector Machine
2) Kernel Method

## 비지도학습
### Dimensionality Rediction
1) Principal component analysis (PCA)
2) Linear Discriminant Analysis(LDA)
3) singular value decomposition (SVD)
4) Non-negative matrix factorization (NMF)

## 비지도학습
###Clustering
1) K-nearest neighbors
2) K-means,K-mediean,k-medoids
3) Elbow method with k means
4) Mean Shift
5) Hierarchical Clustering
6) Gaussian Mixture Model
7) DBSCAN(Density Based Spatial Clustering of Applications with Noise)

## Text mining
1) 토큰화
2) Clearning and Normalization
3) 어간 추출(Stemming) and 표제어 추출(Lemmatization)
4) 불용어(StopWord)
5) 정규 표현식(Regular Expression)
6) 정수 인코딩(integer Encoding)
7) 패딩(Padding)
8) 원-핫 인코딩(One-hot encdoing)
9) 데이터의 분리(data split)
10) 한국어 전처리 패키지(Text Proprcessing Tools for Korean Text)
11) 확률론적 언어 모형 / 언어 모델 평가(Perplexity)
12) BOW(bag of words) / CounterVecorizer
13) Document-Term Matrix
14) Sparse matrix(COO,CSR format)
15) Term Frequenct-Inverse Document Frequency) / 실습 : 20 Newsgroup 분류하기
16) 감성 인식(Sentriment Analysis) / SentiWordNet, VADER / 실습 : IMDB  영황 Review에 대한 긍정/부정 예측 / beautifulSoup / 워드 클라우드 이용
17) 토픽 모델링(LSA(SVD, Truncated SVD)),LSA
18) 문서 군집화
19) 벡터의 유사도 
20) 네이버 영화리뷰 감성인식 / kaggle Mercari Price Suggestion Challenge

# Hackton : new york city taxi trip duration

## 추천시스템
1) 개요
2) 연관분석(Apriori, FP-Growth)
3) 컨텐츠 기반 추천시스템(유사도(유클리디안, 코사인, 피어슨, 자카드), 평가함수(Accuracy, F1-score,RMSE,MAP,NDCG,NDCG), TF-IDF,Word2Vec))
4) 협업필터링(KNN, SGD,ALS를 이용한 추천시스템)
5) 딥러닝을 이용한 추천시스템

## git/github ->source Tree / VS code

## R로 하는 데이터 분석 / 텍스트 마이닝

## 시계열 분석 - 수정중(22.09)
1) 통계량,가설검정
2) 확률과정, 시계열 데이터 처리
3) Autocorrleation, Deterministic/Probabilistic model
4) t/f 검정, Kullback-Leibeler Divergerence, AIC(Akaike Information Criterion), BIC(Bayesain Information Criterion)
5) python statsmodels package

============================Deep Learning============================
1. peceptron
2. mulit layer perceptron
3. Convoluiontal Neural Networks
4. Recurrent Neural Networks
5. Speech Recongition ->기초적인 것.
6. Convolutiaonl Neural Neworks advanced (시각인지) -> RCNN/Faster RCNN
7. Recurrent Neural Networks advanced (언어인지) -> transformer

Deep learning advanced


### linux programming 
### Docker
### web programming

국비과정 프로젝트 결과 : https://github.com/SD-academy
