#packages
#install.packages("dplyr")
#install.packages('descr')
#install.packages('ggplot2')
#install.packages('ISLR')
#install.packages('MASS')
#install.packages('glmnet')
#install.packages('randomForest')
#install.packages('rpart')
#install.packages('ROCR')
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

rm(list=ls()) #선언되어있는 변수 삭제.
setwd('C:/Users/Kims/Documents') #기본경로 설정
getwd() #get 현재 경로 가지고 오세요.

mushrooms<-read.csv('mushrooms.csv',header=T)
mushrooms
head(mushrooms)
tail(mushrooms)
#종속(반응)변수 : class / 22개는 입력변수(설명변수, 예측변수, 독립변수)
CrossTable(mushrooms$class)
#%>%(체인연산자, 줄여서 파이프라인)
#물길을 연결하는 파이프라인처럼 데이터와 데이터를 연결하는
#dplyr 패키지의 핵심 연산자.
mushrooms %>%
  ggplot(aes(class))+
  geom_bar()
#geom_bar() : 범주화.

#결측치 확인
sum(is.na(mushrooms))
CrossTable(mushrooms$stalk.root)

#preprocessing
#veil.type변수는 모두 1 level이라 무의미한 변수를 그냥 제거.
#로지스틱 회귀분석(glm)에서 반응변수(class)가 이진형(binary)
#인 경우 첫번째 레벨에 해당하는 범주가 Failure
#이외의 모든 레벨이 Sucess 로 간주
#class에서 e(식용)가 실패, P(독성)을 성공으로 간주
#class-levels를 재설정.
mushrooms<-mushrooms[,-17]
mushrooms$class<-factor(mushrooms$class,levels=c('p','e'))
summary(mushrooms)

#문제의 복잡도
#mushrooms 데이터의 n,p값을 구해서 문제의 복잡도를 
#확인 해보는 과정
A<-model.matrix(~.-class,mushrooms)
dim(A)

#데이터가 모두 질적 자료(factor data)
#barplot와 모자이크 플롯을 이용하여 시각화를 한다.
#cap.color
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(cap.color, fill=class))+
  geom_bar(position = 'dodge')
#postion : 막대의 위치
#dodge:복수의 데이터를 독립적인 막대 그래프로 나란히 표현.

#gill.color
mushrooms %>%
  group_by(class) %>%
  ggplot(aes(gill.color, fill=class))+
  geom_bar(position = 'dodge')
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
mosaicplot(~cap.color+class,
           data = mushrooms,
           color= T,
           cex=1.2)
##gill.color
mosaicplot(~gill.color+class,
           data = mushrooms,
           color= T,
           cex=1.2)
##odor
mosaicplot(~odor+class,
           data = mushrooms,
           color= T,
           cex=1.2)
##spore.print.color
mosaicplot(~spore.print.color+class,
           data = mushrooms,
           color= T,
           cex=1.2)
#모델 생성
#data set split
#train:validation:test = 6:2:2
#재현 가능성(Reproducible)연구를 위해서 각 모델 생성 전에
#seed 설정
#로지스틱 회귀 error많고, 시간이 오래 걸리기 때문에
#randomforest / lasso model
set.seed(1027)
n<-nrow(mushrooms)
idx<-1:n #총 관측치 개수 인덱싱
training.idx<-sample(idx,n*.60)
#Random하게 전체 데이터에서 60%샘플링
idx<-setdiff(idx,training.idx)
#전체 idx에서 training.idx제외한 나머지 idx를 다시 idx에 저장
#setdiff : 첫 번째 테이블에서 두 번째 테이블 집합의 데이터의 집합을
#뺀 결과를 출력 -> 차집합
validation.idx<-sample(idx,n*.20)
test.idx<-setdiff(idx,validation.idx)
#샘플된 된 데이터 갯수를 확인.
length(training.idx)
length(validation.idx)
length(test.idx)

#순서대로 훈련, 검증, 테스트 데이터 분할
training<-mushrooms[training.idx,]
validation<-mushrooms[validation.idx,]
test<-mushrooms[test.idx,]

#Modeling
mushrooms_rf<-randomForest(class~.,training)
mushrooms_rf
#설명 변수들 중에서 설명력이 높은 변수들 알아보기
#Feature Importance
#평균지니감소량으로 split
importance(mushrooms_rf)
#변수 중요도 확인 plot->XAI(Explainable Artificial Intelligence)
varImpPlot(mushrooms_rf)
#validation set으로 예측
predict(mushrooms_rf,newdata=validation[1:10,])
#확률값을 보고 싶다.
predict(mushrooms_rf,newdata=validation[1:10,],type='prob')

#randomforest 성능평가
y_obs<-ifelse(validation$class =='e',1,0)
#ROC curve,AUROC value
yhat_rf<-predict(mushrooms_rf,
                 newdata = validation,
                 type='prob')[,'e']

#ROC Curve
pred_rf<-prediction(yhat_rf,y_obs)
perf_rf<-performance(pred_rf,measure='tpr',
                     x.measure = 'fpr')
plot(perf_rf,
     col='red',
     main='ROC Curve')
abline(0,1)
#AUC value
performance(pred_rf, "auc")@y.values[[1]] #AUC는 1이다.
#이 모델로 모든 버섯을 분류할 수 있다.


########################################
#lasso는 로지스틱 회귀 보다는 현대적인 방법
#로짓과는 다르게 입력변수에 범주형 변수가 있을 경우 
#모형 행렬을 직접 만들어줘야 한다.
#패키지와 glmnet을 사용함.
#glmnet 패키지로 적합할 수 있는 모형은 라쏘와 릿지회귀(ridge regression)
#ElasticNet 3개가 있다.
#Lasso의 경우 랜덤 포레스트와 다르게 설정값이 alpha와 lambda로 2개이다.

#모형 행ㄹ려 생성 : 절편항이 필요없으므로 모형식에-1을 설정.
xx<-model.matrix(class~.-1,mushrooms)

#입력변수
x<-xx[training.idx,]

#반응변수
y<-ifelse(training$class=='e',1,0)

dim(x)
#가변(더미변수) 포함한 훈련 데이터 갯수 / 관측기 4874개, 변수 96개

#모형 적합(생성)
#alpha=1이 디폴트(default)로 설정되어 있어서 LASSO 모형으로 적합된다.
#alpha=0인 경우 Ridge regression 모형이 되며
#alpha를 0과 1사이에 지정해줄 경우 해당 알파값을 갖는 Elasticnet모형이 된다.

#위에서 생성한 입력변수와 반응변수를 이용해 LASSO 모형 적합을 실행한다.
mushrooms_glmnet_fit<-glmnet(x,y)
#다음은 coefficient profile plot 혹은 모수 패스를 나타내는 그래프이다.
plot(mushrooms_glmnet_fit)

#lasso의 경우 모형의 복잡도로 L1-norm을 사용한다.
#하단 숫자 = lambda가 변함에 따라서 전체 모수 벡터의 L1-norm의 값
#상단 숫자 = 주어진 L1-nrom에 해당하는 0이 아닌 모수의 갯수 즉 모형의 자유도를 뜻함.
#관측치 4874개,변수 96개 중에서 선택된 변수들이 얼마나 되는지 시각적으로 확인할 수 있다.

mushrooms_glmnet_fit

#변해가는 lambda(복잡도 벌점)의 변화에 따른 DF와 %Dev 값이 나온다.
#DF : Degree of Freedom 자유도
#% Dev : 현재 모형으로 설명되는 변이의 부분이 어느 정도인가
#연구자가 원하는 lambda 값에 해당하는(혹은 자유도) 모수 추정값들을 보고 싶은 경우
#만약 원하는 lambda = 0.2236 인 경우 (다른 말로 자유도가 2인 경우)
coef(mushrooms_glmnet_fit, s = .2236)

#모형식은 다음과 같다.
#eta = (Intercept) + coef1 * Var1 + coef2 * Var2 + ….
#eta = 0.377051938 - 0.003160735 * odorf + 0.335355511 * odorn
#mushrooms 데이터에 로지스틱 glmnet 모형을 적합하고 거기에 교차검증(Cross Validation)을 시행한 결과
mushrooms_cvfit <- cv.glmnet(x, y,
                             family = "binomial")
plot(mushrooms_cvfit)
#x 축 : lambda의 로그값 => 좌측일수록 복잡한 모형(자유도 높음), 우측일수록 단순한 모형
#y 축 : 주어진 lambda 에서 k-fold 교차검증 오차 범위
#빨간 점 : 주어진 lambda 에서의 k개의 교차검증의 평균값.
# 최적의 예측력을 갖는 모형 : 예측력이 가장 좋을 때는 lamda가 가장 작은 경우 
log(mushrooms_cvfit$lambda.min) 
# 해석력이 좋은 모형에서의 lambda의 로그값
log(mushrooms_cvfit$lambda.1se) 
#각 변수들의 모수 출력
# lambda.1se 일 때 각 변수들의 계수들(모수) 출력 
coef(mushrooms_cvfit,
     s = mushrooms_cvfit$lambda.1se)
#데이터의 모든 변수들 중에 영향력이 있다고 판별된 변수들의 갯수 출력
length(which(coef(mushrooms_cvfit,
                  s="lambda.1se")!=0))
#LASSO 모형을 이용한 예측
#labda = lambda.1se 일 때 관측치 1 - 5에 대한 확률 예측값을 보자.
predict(mushrooms_cvfit,
        s = "lambda.1se",
        newx = x[1:5, ],
        type = "response")
#Lasso 모형 평가
y_obs <- ifelse(validation$class == "e", 1, 0)
yhat_glmnet <- predict(mushrooms_cvfit, s = "lambda.1se",
                       newx = xx[validation.idx, ],
                       type = "response")

yhat_glmnet <- yhat_glmnet[, 1]

#ROC CUrve
pred_glmnet <- prediction(yhat_glmnet, y_obs)
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
#AUC Value
performance(pred_rf, "auc")@y.values[[1]]

#test set을 이용한 분류분석
# RF
pre1 <- predict(mushrooms_rf,
                newdata = test,
                type = "prob")[, 'e']

# LASSO
pre2 <- predict(mushrooms_cvfit,
                s = "lambda.1se",
                newx = xx[test.idx, ],
                type = "response")

head(pre1, 10)
