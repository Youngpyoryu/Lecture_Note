#K-nn(K-Nearest Neighbor)
#레이블이 없는 예시를 레이블된 유사된 예시의
#클래스로 할당해 분류하는 특징이 있는 알고리즘.
#장점:
#단순하고 효율적이다.
#기저 데이터 분포에 대한 가정을 하지 않는다.
#훈련 단계가 빠르다.
#단점:
#모델을 생성하지 않아 특징과 클래스 간의 관계를
#이해하는 능력을 제약을 받는다.
#적절한 K의 선택이 필요함. /Elbow method ->kmeans
#분류 단계가 느리다.
#명목 특징과 누락 데이터용 추가 처리가 필요하다.


# 거리로 유사도 측정
# 유클리디안 거리(Euclidean distance)
# 맨해튼 거리(Manhatten distance)
#적절한 k를 선택해 -> 일반화된 모델을 선택
#과적합(Overfitting)과 과소적합(underfitting)의 
#균형은 trade-off 관계가 있음.
#정규화?
#최대-최소 정규화(Min-Max normalization)
#z-점수 정규화(Z-score normalization)

#k-nn 알고리즘으로 유방암 진단.
#C:/Users/Kims/Downloads/archive/data.csv
#절대경로를 사용.
wbcd<-read.csv('C:/Users/Kims/Downloads/archive/data.csv')
#상대경로 접근 ->리눅스 ./ 현재  .. : 상위폴더
# .././
#Wbcde<-read.csv('./data.csv')
str(wbcd)
#
#반지름(Redius) / 질감(Texture) / 둘레(Perimeter)
#넓이(Area) /  매끄러움(Smoothness) / 조밀성(Compactness)
#오목함(Concavity) /  오목점(Concave points)
#대칭성(Symmetry) / 프랙탈 차원(Fractal dimension)
#모든 특징이 모양과 크기에 관련된 것으로 보인다.
#종양학자가 아니라면 특징이 양성(Benign)이나 
#악성(Malignant) 종양과 어떻게 관련되어 있는지 알기는 어렵다.
#id 특징->필요 없으니 삭제하자.
# 마이너스 부호 활용시 특정 행 or 열을 제외한 데이터 추출 가능.
wbcd<-wbcd[-1]
table(wbcd$diagnosis)
#R 머신러닝 분류기는 목표 특징이 팩터로 코딩이 되어야함.
wbcd$diagnosis<-factor(wbcd$diagnosis,
                       levels=c('B','M'),
                       labels=c('Benign','Malignant'))
round(prop.table(table(wbcd$diagnosis))*100,digit=1)
summary(wbcd[c('radius_mean','area_mean','smoothness_mean')])
#수치를 통일화 해줘야 하기 때문에 정규화를 실시.
#특징을 정규화하고자 R에서 normlize()함수를 사용.
normalize<-function(x){
  return( ( x - min(x) ) / ( max(x) - min(x) ) ) 
}
#normalization test
normalize(c(1,2,3,4,5))
normalize(c(10,20,30,40,50))
#lapply : 결과값이 list형태로 나옴.->as.data.frame()
wbcd_n<-as.data.frame(lapply(wbcd[2:31],normalize))
wbcd_n
#data split [row,column]문법을 사용하면 된다
#wbcd가 무작위로 레코드가 선언이 되어있음.
wbcd_train<-wbcd_n[1:469,]
wbcd_test<-wbcd_n[470:569,]

#label을 split
wbcd_train_labels<-wbcd[1:469,1]
wbcd_test_labels<-wbcd[470:569,1]

#모델 학습
# install.packages('Class')
library(class)
# p<-KNN(train,test,class,k)
# train : 수치 훈련 데이터를 포함하는 데이터 프레임
# test : 수치 테스트 데이터를 포함하는 데이터 프레임
# class : 훈련 데이터의 각 행에 대한 클래스를 갖는 팩터 벡터
# k : 최근접 이웃의 개수를 가리키는 정수.
wbcd_test_pred<-knn(train=wbcd_train,test=wbcd_test,
                    cl= wbcd_train_labels,k=21)
#모델 성능 평가 ->crosstable
#install.packages('gmodels')
library(gmodels)
CrossTable(x=wbcd_test_labels,y=wbcd_test_pred,
           prop.chisq = FALSE)
#카이제곱(chi-sqaure) : 하나 이상의 범주에서
#관측된 빈도가 기대빈도와 일치하는지를 하는 것.
#모델 성능 개선 시도!
#z-score 표준화
#암 데이터셋에서는 z-점수 표준화가 특징을 재조정하는
#좀 더 적절한 방법이 될 수 도 있다.
#z-점수 표준화 값은 사전에 정의된 최솟값, 최댓값이 
#없기 때문에 극값이 중심 방향으로 축소되지 않는다.
# R에서는 z-점수 ->scale
wbcd
#wbcd_z<-as.data.frame(scale[-1]))
wbcd_z<-as.data.frame(lapply(wbcd[2:31],scale))
wbcd_z
summary(wbcd_z$area_mean)
wbcd_train<-wbcd_z[1:469,]
wbcd_test<-wbcd_z[470:569,]
wbcd_train_labels<-wbcd[1:469,1]
wbcd_test_labels<-wbcd[470:569,1]
wbcd_test_pred<-knn(train=wbcd_train,test=wbcd_test,
                    cl=wbcd_train_labels,k=21)
CrossTable(x=wbcd_test_labels,y=wbcd_test_pred,
           prop.chisq = FALSE)













