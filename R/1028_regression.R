#수학적 관계는 일상생활의 다양한 측면을 이해하는데 도움을 줌.
#패턴들을 숫자로 공식화하면 좀 더 명확해준다.

#회귀
# : 수치 관계의 크기와 강도를 모델링 하는 기법. 
#한 개의 종속(반응,결과) 변수(dependent variable)와
#한 개 이상의 수치 독립 변수(independent variable)(설명,예측변수)
#종속 변수는 독립 변수의 값에 따라 달라짐
#가장 단순한 회귀 형태는 독립 변수와 종속 변수가 직선 관계라고 가정.
#y=ax+b 기울기 절편 형식(slope-intercept form) /y는 종속변수, x는 독립변수
# a:기울기(slope) / b :절편(intercept)
#통계적 가설 검정 ->회귀 / 관측 데이터를 고려해 사실인지 아닌지?
#1986년 1월 29일 미국 우주 왕복선 챌린저(Challenger)가
#로켓 부스터 고장으로 끔찍하게 분해되어서 일곱 명의 승무원이 사망.
#잠재요인->발사 온도에 초점을 맞춤.
#로켓 연결 부분의 밀봉을 담당하는 패킹용 고무오링이 40'F(4도)
#미만에서는 테스트되지 않았었고, 발사 당일의 날씨가
#평소와 달리 매우 춥고 영하인 상태
#이 사고로 데이터 분석과 시각화의 중요성에 대한 사례 연구가 되었다.
launch<-read.csv('challenger.csv')
launch

b<-cov(launch$temperature,launch$distress_ct) / 
  var(launch$temperature)
b

a<-mean(launch$distress_ct) - b*mean(launch$temperature)
a

cor(launch$temperature,launch$distress_ct)
#회귀 분석 가설검정
#귀무가설(Null hypothesis,H_0) : 기울기가 0이다. 
#VS 대립가설(alternative hypothesis,H_1) : 기울기가 0이 아니다

#다중 선형회귀
#장점 :
#수치 데이터를 모델링 하기 위한 가장 일반적인 방법
#어떤 모델링 작업에든 대부분 적용할 수 있다.
#특징과 결과간의 관게에 대한 강도와 크기 추정치를 제공.

#단점 : 
#데이터에 대한 강한 가정을 한다.
#모델 형태가 사용자에 의해 미리 지정돼야만 한다.
# 누락 데이터 처리 하지 않음.
# 수치 특징만 처리하므로, 범주 데이터는 추가적인 준비(ex.encoding)
#모델을 이해하려면 통계학을 알아야 함.

#선형 회귀를 이용한 의료비 예측
#insurance.csv
#미국 환자의 가상 의료비가 들어있는 모의 데이터셋 사용.
#의료보험에 등록된 1,388명의 수익자 예시가 들어있음.
#환자읱 ㅡㄱ성과 해당 연도에 의료보험에 청구된 전체 의료비 특징으로 나타냄.
#age : 주 수익자의 연령, 정수(64세 이상은 일반적으로 정부에서 관리하기 때문에 제외)
#sex : 보험 계약자의 성별, 여성 또는 남성
#bmi : 신체용적지수, 키에 상대적으로 초과하거나 미달되는 몸무게에 대한 이해를 제공.
#이상적인 bmi sms 18.5 ~ 24.9 범위
#children : 의료보이 적용되는 자녀 수/부양가족 수,정수
#smoker : 피보험자의 정기적인 흡연 여부, 예 또는 아니오 범주형
#region : 미국 내 수익자의 거주 지역, 북동(northeast), 남동(souheast),남서(southwest),북서(northwest) 네 개의 지리구로 나눈다.

insurance<-read.csv('insurance.csv',stringsAsFactors = TRUE)
str(insurance)
summary(insurance)
hist(insurance$expenses) #의료비
#오른쪽으로 꼬리가 긴 분포
install.packages("moments")
library(moments)
skewness(insurance$expenses) #왜도(skew)
#skew>0 -> mode<median<mean
#skew<0-> mean<median<mode
kurtosis(insurance$expenses)#첨도
#첨도는 0인 것이 좋다.

table(insurance$region)
cor(insurance[c('age','bmi','children','expenses')])
#상관행렬 cor(x,y) = cor(y,x)
#age,bmi 약한 양의 상관관계가 있어서 나이가 들수록
#체중이 증가함.
#age와 expenses, bmi와 expenses, children과 expenses
#양의 상관관계가 있다.
#연관성 나이,몸무게, 자녀수가 증가하였을 때,
#예상 보험금이 올라간다는 것을 의미.

#특징 간 관계 시각화 : 산포도 행렬
#산포도 행렬(scatterplot matrix) : 세 개 이상의 변수에서 패턴을
#찾을 때 사용. 한번에 두 개의 특징만을 관찰하기 때문에
#진정한 다차원 시각화가 아님.
pairs(insurance[c("age", "bmi", "children", "expenses")])
#age와 expenses의 관계는 상대적으로 여러 직선으로 보이고,
#bmi와 expenses 그림은 두 개의 구분되는 점 그룹을 갖는다.
#다른 그림에서는 추세를 감지하기 어렵다.

#scatter plot
#more informative scatter plot matrix
install.packages("psych") 
library(psych)
pairs.panels(insurance[c("age", "bmi", "children", "expenses")])
#산포도에 있는 타원 모양의 객체는 상관관계 타원형으로
#상관관계의 강도를 시각화한다.
#타원이 늘어질수록 상관관계가 강해진다.
#bmi와 children처럼 거의 완벽하게 둥근 타원 모양은 아주 약한 상관관계가 나타남.
#타원 안의 점은 x축과 y축 변수의 평균을 나타냄.

#산포도에 그려진 곡선을 뢰스 곡선(Loess curve)라고 함.
#이 곡선은 x와 y축 변수 사이에 일반적인 관계를 나타냄.
#ex) age와 children의 곡선은 U를 뒤집은 모양으로 중년 무렵에 최고점이 된다.
#이것이 의미하는 것은 샘플에서 고령과 젊은이는 중년보다 의료보험에서 보장하는 자녀수가 적다는 것이다.
#추세가 비선형적이기 때문에 이런 결론은 상관관계 하나로는 추론되지 않는다.
#한편 age와 bmi에 대한 뢰스 곡선은 점차 올라가는 곡선으로 몸무게 연령에 따라 증가한다는 것을 의미하지만,
#이는 이미 상관 행렬에서 추론되었다.



#lm : linear regression  /  ~ : 틸드 문자  / 종속변수 ~ 독립변수 
#이 함수는  stats 패키지에 포함되며, R을 설치할 때, 기본으로 포함하고 로드된다.

#분류기 구축
#M<-LM(dv ~ iv, data = mydata)
# dv : 모델링될 mydata 데이터 프레임 내의 종속 변수
# iv는 모델에서 사용할 mydata 데이터 프레임 내의 독립 변수를 명시하는 R구문
# data는 dv와 iv 변수를 찾을 수 있는 데이터 프레임
#이 함수는 예측에 사용될 수 있는 회귀 분석 모델 객체를 반환한다.
#독립 변수 간에 상호작용은 *연산자로 명시할 수 있다.

#예측
#P<-predict(m,test)
#m : lm() 함수에 의해 훈련된 모델
# test : 분류기를 구축하는데, 사용된 훈련 데이터와 같은 특징을 갖는 테스트
# 데이터를 퐇마하는 데이터 프레임
# 이 함수는 예측 값의 벡터를 반환한다.

#ins_model <-lm(expenses ~ age+children+bmi+sex+smoker+region,data=insurance)
ins_model <-lm(expenses ~ . , data=insurance)


#모델 성능 평가
summary(ins_model)

#모델 성능 개선
#비선형 관계 추가
insurance$age2<- insurance$age^2
#bmi>30 이면 1, 아니면 0 #이진화
insurance$bmi30<-ifelse(insurance$bmi>=30,1,0)
#ex) 흡연과 비만은 각자 유해한 영향을 미치지만, 이들의 결합된 영향이
#각각의 합보다 나쁘다고 가정하다는 것은 합리적이다.
#두 특징이 결합된 영향을 가질 때 이것을 상호작용(interaction)이라고 함.
ins_model2<-lm(expenses~age+age2+children+bmi+sex+bmi30*smoker+region,
               data = insurance)
summary(ins_model2)

#회귀 모델로 예측
insurance$pred<-predict(ins_model2,insurance)
cor(insurance$pred,insurance$expenses)
plot(insurance$pred,insurance$expenses)
abline(a=0,b=1,col='red',lwd=3,lty=2)
#lwd : 선 두께를 조절하는 그래프 모수
#lty : 선 유형을 선택하는 것.
#lty=0 : 그리지 않음 / =1:실선(기본값)
#=2(대시(-)) / =3(점) / =4(점과 대시) / =5(긴 대시) / =6(두 개의 대시)

predict(ins_model2,
        data.frame(age=30, age2=30^2, children=2,
                   bmi=30, sex='male',bmi30=1,
                   smoker='no', region='northeast'))
#6000$로 예상.
predict(ins_model2,
        data.frame(age=30, age2=30^2, children=2,
                   bmi=30, sex='female',bmi30=1,
                   smoker='no', region='northeast'))
#6470$로 예상.
predict(ins_model2,
        data.frame(age=30, age2=30^2, children=0,
                   bmi=30, sex='female',bmi30=1,
                   smoker='no', region='northeast'))
#5113$로 예상.

#######################################################
#회귀 트리와 모델 트리의 이해
#CART(classification and regression tree)
#장점 : 
#의사 결정 트리의 장점과 수치 데이터를 모델링 하는 능력을 결합했다.
#사용자가 모델을 미리 명시하지 않아도 된다.
#자동 특징 선택을 사용하기 때문에 아주 많은 개수의 특징이 이 방식에 사용될 수 있다.
#선형 회귀보다 일부 데이터 타입에 아주 잘 맞는다.
#모델을 해석하는데 통계 지식은 필요 없다.

#단점 : 
#선형 회귀만큼 잘 알려져 있지 않다.
#많은 양의 훈련 데이터가 필요하다.
#결과에 대한 개별 특징의 전체적인 순영향을 알아내기가 어렵다.
#큰 트리는 회귀 모델보다 해석하기가 좀 더 어려워질 수 있다.

#classification에서는 혼잡도를 평가할 수 있지만
#수치형에서는 혼잡도를 평가하기가 어려움.

#수치 예측형 트리는 분류용 트리와 거의 같은 방식으로 구축됨.
#루트 노드에서 시작해서 분할 정복 전략으로 데이터를 분할하며,
#이 때 분할 후 결과의 동질성을 가장 크게 증가하는 특징으로 분할 조건으로 한다.
#분류 트리의 경우 동질성이 엔트로피로 측정되지만,
#수치 데이터에는 엔트로피가 정의되지 않으므로, 
#수치 의사 결정 트리는 분산, 표준 편차, 평균과의 절대 편차 같은 통계량으로 동질성을 측정함.
#분할 이전의 표준 편차의 분할 이후의 가중 표준편차를 비교해
#표준 편차의 축소를 측정을 함.
tee<-c(1,1,1,2,2,3,4,5,5,6,6,7,7,7,7)
at1<-c(1,1,1,2,2,3,4,5,5)
at2<-c(6,6,7,7,7,7)
bt1<-c(1,1,1,2,2,3,4)
bt2<-c(5,5,6,6,7,7,7,7)
# SDR = sd(T) - (summation) (|T_i| / |T| ) *sd(T_i)
#sd(T) : 집합 T의 표준편차
#T_1,T_2,..T_n은 특징에 대해 분할된 집합들.
sdr_a <-sd(tee) - (length(at1) / length(tee) * sd(at1)+
                     length(at2)/ length(tee) * sd(at2))
sdr_b <-sd(tee) - (length(bt1) / length(tee) * sd(bt1)+
                     length(bt2)/ length(tee) * sd(bt2))
sdr_a
sdr_b
#특징 A로 분할할 경우 SDR(standard deviation reduction)은 1.2정도이고,
#특징 B로 분할할 경우는 SDR은 1.4정도이다.
#B로 분할할 때 표준 편차는 좀 더 감소됐으므로 의사 결정 트리는
#B를 먼저 사용하자!

#와인데이터 -> 품질 평가가 굉장히 어렵다. whitewine.csv
#4898개의 와인 샘플과 11가의 화학 속성에 대한 정보가 들어있음.
#산도(acidity), 당 함유량(sugar content),염화물(Chlorides)
#황(sulfur) , 알코올(alcohol), pH, 밀도(density)와 같은 특성으로 측정
#그런 다음 3명 이상의 심사 위원단이 블라인드 테이스팅으로 샘플을 평가함.
#평가된 품질 척도가 0(매우 나쁨)~10*매우 우수)
#평가에 동의하지 않은 심사 위원의 경우는 중앙값(median)으로 사용되었다.
wine<-read.csv('whitewines.csv')
str(wine)

#트리의 장점 ->사전 처리 없이 돌려도 됨.
#특징에 대한 정규화(min-max)와 표준화(0~1)는 필요 없다.
hist(wine$quality)
summary(wine)

wine_train<-wine[1:3750,] #75%
wine_test<-wine[3751:4898,] #25%
#트리회귀 ->rpart(recursive partitioning)패키지에 있음.
install.packages('rpart')
library(rpart)
#regression tree using rpart

#분류기 구축
#M<-rpart(dv ~ iv, data = mydata)
# dv : 모델링될 mydata 데이터 프레임 내의 종속 변수
# iv는 모델에서 사용할 mydata 데이터 프레임 내의 독립 변수를 명시하는 R구문
# data는 dv와 iv 변수를 찾을 수 있는 데이터 프레임
#이 함수는 예측에 사용될 수 있는 회귀 트리 객체를 반환한다.

#예측
#P<-predict(m,test,type = 'vector')
#m : rpart() 함수에 의해 훈련된 모델
# test : 분류기를 구축하는데, 사용된 훈련 데이터와 같은 특징을 갖는 테스트
# 데이터를 포함하는 데이터 프레임
# type은 반환될 예측의 종류를 명시, 'vector'(예측 수치값) / 'class'(예측 클래스), 'prob'(예측 클래스 확률)
#이 함수 type 파라미터에 따라 예측 벡터를 반환한다.
m.rpart<-rpart(quality ~., data = wine_train)
summary(m.rpart)
#트리의 시각화
install.packages('rpart.plot')
library(rpart.plot)
rpart.plot(m.rpart,digits=3)
#digits:숫자 자리수 조정.
rpart.plot(m.rpart,digits=4,fallen.leaves=TRUE,
           type=3,extra=101)
#fallen.leaves:잎 노드가 도형의 바닥에 정렬하게 만듦.
#type과 extra파라미터는 결정과 노드가 레이블되는 방식에 영햐을 줌
#숫자 3과 101은 특정 형식을 참조하고, 이는 명령어의 설명문 또는
#다양한 숫자로 실험해보면 알 수 있다.
p.rpart<-predict(m.rpart,wine_test)
summary(p.rpart)
summary(wine_test,quality)

#예측된 품질 값과 실제 품질 값 사이에 상관관계 측정
cor(p.rpart,wine_test$quality)

#평균 절대 오차(MAE,mean absolute Error)
MAE<-function(actual,predicted){
  mean(abs(actual-predicted))
}
MAE(p.rpart,wine_test$quality)
mean(wine_train$quality)
MAE(5.87,wine_test$quality)

##모델 성능 개선
#모델 트리는 잎 노드를 회귀 노드에서 대체함으로써 회귀 트리를 확장한다.
#모델 트리는 잎 노드에서 예측에 하나의 값만 사용하는 회귀 트리보다 더 정확한 결과를 낸다.

#참고 : https://cran.r-project.org/web/packages/Cubist/vignettes/cubist.html
#큐비스트 알고리즘으로, M5 트리 알고리즘이 강화된것이다.
#cubist : Regression modeling using rules with added instance-based corrections.


#cubist 패키지의 cubist()함수 이용
#모델 구축
#m<-cubist(train,class)
#train : 훈련 데이터를 가진 데이터 프레임이나 행렬
#class : 훈련 데이터에서 각 열의 부류에 해당하는 팩터 벡터
#함수 예측에 사용할 수 있는 큐비스트 모델 트리 객체를 반환.
#예측
p<-predict(m,test)
#m : cubist()함수로 훈련한 모델
# train은 모델을 구축할 때, 사용한 훈련 데이터와 동일한 특징을 가진
#테스트 데이터의 데이터 프레임
#함수는 예측 수치 값의 벡터를 반환한다.


#큐비스트 모델 트리는 회귀 트리에 사용된 것과 살짝 다른 구문을 사용해 적합화한다.
#cubist()함수 R 공식 구문을 받아들이지 않기 때문이다.
#그 대신 x 독립 변수와 y 종속 변수에 사용된 데이터 프레임 열을 명시해야 한다.
install.packages('lattice')
library(Cubist)
m.cubist<-cubist(x=wine_train[-12],y=wine_train$quality)
summary(m.cubist)
#이 모델 트리 결과와 이전 회귀 트리 결과의 핵심차이는
#여기서의 노드는 수치 예측으로 끝나지 않고 선형 모델로 끝난다는 점.
p.cubist<-predict(m.cubist,wine_test)
summary(p.cubist)
cor(p.cubist,wine_test$quality)
MAE(wine_test$quality,p.cubist)


#Non-Linear Regeression in R with Decisiton Tree
#https://machinelearningmastery.com/non-linear-regression-in-r-with-decision-trees/
