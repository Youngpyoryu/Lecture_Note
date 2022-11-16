#package

#install.packages("dplyr")
#install.packages('descr')
#install.packages('ggplot2')
#install.packages('ISLR')
#install.packages('MASS')
#install.packages('glmnet')
#install.packages('randomforest')
#install.packages('rpart')
#install.packages('ROCR')"
library(dplyr) #데이터 전처리 패키지
library(descr) # ex) 빈도계산 ex)frq...
library(ggplot2) #그림
library(ISLR) #least squared linear regression
library(MASS) #toy examples
library(glmnet) #패널티 최대 우도(penalized maximum likelihood)를 통해서 
#일반화 선형 모델(generalized linear model)을 적합하는 패키지
library(randomForest) #Randomforest 패키지
library(rpart) #의사결정 나무 패키지
library(ROCR)#AUC(AUROC) curve 패키지
library(hacktoolkit)

rm(list=ls())
setwd('C:/Users/user/Documents')
getwd()

mushrooms<-read.csv('mushrooms.csv',header=T)
#총 23개의 변수가 사용
#종속 변수(반응변수) : class / 22개는 입력변수(설명변수,
#예측변수, 독립변수)
head(mushrooms)
str(mushrooms)

#반응변수 빈도수와 비율
CrossTable(mushrooms$class)

mushrooms %>%
  ggplot(aes(class))+
  geom_bar()

#결측치 확인
sum(is.na(mushrooms))

CrossTable(mushrooms$stalk.root)

#pre-Processing
#veil.type 변수는 모두 1 level이라 무의미한 변수이므로 제거
#로지스틱 회귀분석(glm)에서 반응변수(class)가 이진형(binary)
#인 경우 첫번째 레벨에 해당하는 범주가 Failure
#이외의 모든 레벨이 Success로 간주.
#class에서 e(식용)가 실패, p(독성)가 성공으로 간주.
#class ->levels를 재설정.
mushrooms<-mushrooms[,-17]
mushrooms$class<-factor(mushrooms$class, levels=c("p","e"))
summary(mushrooms)

#문제의 복잡도 구하기.
#mushrooms 데이터의 n,p값을 구해서 문제의 복잡도를 확인 해보는 과정.
A<-model.matrix(~ . -class,mushrooms)

dim(A)
#n=8124,p=96

#데이터가 모두 질적 자료(factor data)
#bplot와 모자이크 플롯을 이용하여 시각화를 한다.
#barplot

#cap.color
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(cap.color, fill=class))+
  geom_bar(position='dodge')
#postion : 막대의 위치
#dodge : 복수의 데이터를 독립적인 막대 그래프로 나란히 표현. 

#gill.color
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(gill.color, fill=class))+
  geom_bar(position='dodge')
#odor
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(odor, fill=class))+
  geom_bar(position='dodge')

#spore.print.color
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(spore.print.color, fill=class))+
  geom_bar(position='dodge')



#Mosaicplot
##cap.color
mosaicplot( ~ cap.color +class,
            data = mushrooms,
            color=T,
            cex=1.2
            )

# gill.color
mosaicplot( ~ gill.color + class,
            data = mushrooms,
            color=T,
            cex=1.2)
# odor
mosaicplot( ~ odor + class,
            data = mushrooms,
            color=T,
            cex=1.2)
# spore.print.color
mosaicplot( ~ spore.print.color + class,
            data = mushrooms,
            color=T,
            cex=1.2)

#모델 생성.
#data set split
# Training:Validation:Test = 6:2:2
#재현 가능성(Reproducible)연구를 위해서 각 모델 생성 전에
#seed 설정
#로지스틱 회귀 Error많고, 시간이 많이 걸림
#Randomforest / Lasso model
set.seed(0503)
n<-nrow(mushrooms)
idx <- 1:n #총 관측치 개수 인덱싱

training.idx <-sample(idx,n*.60)
#Random하게 전체 데이터에서 60% 샘플링
idx <-setdiff(idx,training.idx)
#전체 idx에서 training_idx 제외한 나머지 idx를
#다시 idx변수에 저장.
#setdiff : 첫 번째 테이블에서 두 번째 테이블 집합의
#데이터 집합을 뺀 결과를 출력. / 차집합
validation.idx<-sample(idx,n*.20)
test.idx<-setdiff(idx,validation.idx)

#샘플링 된 데이터 갯수들 확인.
length(training.idx)
length(validation.idx)
length(test.idx)

#순서대로 훈련,검증, 테스트 데이터
training <-mushrooms[training.idx,]
validation <-mushrooms[validation.idx,]
test<-mushrooms[test.idx,]
#Random Forest / Bagging
#seed setting
set.seed(0503)
#modeling
mushrooms_rf<-randomForest(class ~.,training)
mushrooms_rf

#설명 변수들 중에서 설명력이 높은 변수들 알아보기
#Feature importance
#평균지니지수감소량으로 split
importance(mushrooms_rf)

#변수 중요도 확인 plot->XAI(Explainable Artificial Intelligence)
varImpPlot(mushrooms_rf)

#validation set으로 예측.
predict(mushrooms_rf,newdata=validation[1:10,])

#확률값으로 보고 싶은 경우.
predict(mushrooms_rf,newdata=validation[1:10,],type='prob')

#Random forest 모델 평가
#ROC curve, AUC value
yhat_rf <- predict(mushrooms_rf,
                   newdata = validation,
                   type = "prob")[, 'e']

#ROC curve
pred_rf <- prediction(yhat_rf, y_obs)

perf_rf <- performance(pred_rf, measure = "tpr",
                       x.measure = "fpr")

plot(perf_rf,
     col = "red",
     main = "ROC Curve")

abline(0,1)

performance(pred_rf,'auc')@y.values[[1]]


#lasso regression
#로지스틱 회귀보다는 현대적인 방법.
#로짓과 다르게 입력변수에 범주형 변수가 있을 경우
#모형 행렬을 직접 만들어줘야 함.
#패키지 glmnet(lasso,ridge,elasticent regression)
#lasso alpha(learning_rate),lambda(lasso coff)를 정해야 함.
xx<-model.matrix(class ~.-1,mushrooms)

#입력변수
x<-xx[training.idx,]
#반응변수
y<-ifelse(training$class =='e',1,0)

dim(x) #관측치:4874, 변수:96개
#모형 생성
#alpha=1 defualt ->lasso
#alpha=0 ->Ridge
# 0<=alpha<=1 ->elasticnet
mushrooms_glment_fit<-glmnet(x,y)
plot(mushrooms_glment_fit)

#lassod의 경우는 모형의 복잡도
#l1-norm으로 나타냄
#하단 숫자=lambda가 변함에 따라서
#전체 모수 벡터의 l1norm값
#상단 숫자=주어진 l1-norm,에 해당하는 
#0이 아님 모수의 갯수, 즉 모형의 자유도.
#관측ㅊ기 4874개,변수 96개 중에서
#선택된 변수들이 얼마나 되는지 시각화
mushrooms_glment_fit
#DF :degree of freedom(자유도)
#%dev : 현재 모형으로 설명되는 변이의 부분이
#어느 정도인가?
#lambda:연구자가 원하는 lambda값에 해당하는
#(혹은 자유도) 모수 추정값들을 보고 싶은 경우.

#ex)lambda=0.2236(다른 말로 자유도가 2인 경우.)
coef(mushrooms_glment_fit,s=.2236)

#cross validation
mushrooms_cvfit<-cv.glmnet(x,y,family='binomial')
plot(mushrooms_cvfit)

#x축 : lambda의 로그값
#좌측일수록 복잡한 모형(자유도가 높음)
#우측일수록 단순한 모형
#y축 : 주어진 labmda에서의 k-fold 교차검증 오차 범위
#빨간 점 : 주어진 lambda에서의 k개의 교차검증의 평균값.

#최적의 예측력을 갖는 모형 : 예측력이 가장 좋을 때는
#lambda가 가장 작은 경우.
log(mushrooms_cvfit$lambda.min)

#해석력이 좋은 모형에서의 lambda의 로그값
log(mushrooms_cvfit$lambda.1se)

#각 변수들의 모수 출력
#lambda.1se일 때 각 변수들의 계수들(모수) 출력
coef(mushrooms_cvfit,
     s=mushrooms_cvfit$lambda.1se)
#데이터의 모든 변수들 중에 영향력이 있다고 판별된 변수들의
#갯수 출력
length(which(coef(mushrooms_cvfit,s='lambda.1se')!=0))

#lambda=lambda.1se일때 관측치 1-5에 대한 확률 예측값
predict(mushrooms_cvfit,
        s = "lambda.1se",
        newx = x[1:5,],
        type = "response")
#newx : 새로운 입력 matrix을 위함.
# type = "response" ->정확도를 확률로 구하기 위한 인자.
yhat_glment<-predict(mushrooms_cvfit,
                     s='lambda.1se',
                     newx=xx[validation.idx,],
                     type = "response")

yhat_glment <-yhat_glment[,1]

y_obs<-ifelse(validation$class=='e',1,0)
pred_glmnet <- prediction(yhat_glment, y_obs)
perf_glmnet <- performance(pred_glmnet,
                           measure = "tpr",
                           x.mesure = "fpr")

plot(perf_rf,
     col = "red",
     main = "ROC Curve")

plot(perf_glmnet,
     add = T,
     col = "blue")

abline(0, 1)

legend("bottomright",
       inset = .1,
       legend = c("Random Forest", "LASSO"),
       col = c("red", "blue"),
       lty = 1, lwd = 2)
performance(pred_rf, "auc")@y.values[[1]]



