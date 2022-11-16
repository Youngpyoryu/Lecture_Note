#의사결정 나무 ->트리 구조.
#탐욕스럽게(Greedily) 분할하는 방법.
#CART(Classification and Regression Tree)알고리즘에서 작동
#CART : 통계적 이진분류,  Gini index(지니 지수)로 작동됨.
#재귀 분할(Recursive partitioning)을 사용함.
#분할 정복(Divide and conquer) : 데이터 부분집합으로 나누며,
#알고리즘 집합의 데이터가 충분히 동질적이라고 판단하거나
#다른 종료 조건에 만나 과정이 종료될 때까지 계속됨.
#최고의 분할 선택->엔트로피가 낮아지는 방향.
curve(-x*log2(x)-(1-x)*log2(1-x),
      col='red',xlab='x',ylab='Entropy',lwd=4)
#x->베르누이 확률분포
#(결과가 두 가지 중 하나로만 나오는 실험이나 시행 ex)동전던지기)

#데이터셋 : 독일의 한 신용기관에서 얻은 대출 정보가 들어있음.
#1000개의 대출 예시 및 대출 신청자의 특성을 나타내는 일련의
#수치 특징과 명목 특징을 포함하고 있다.
#클래스 변수는 채무 불이행으로 갔는지 여부를 나타냄.
credit<-read.csv('C:/Users/Kims/Downloads/credit.csv')
str(credit)
#채무 불이행을 예측할 것 같은 일부 대출 특징에 대해 알아보자.
table(credit$checking_balance)
table(credit$savings_balance)
#DM->독일 마르크로 기록됨(화폐)
#독일 마르크는 유로가 채택되기 전에 독일에서 통용됐던 화폐이다.

#대출의 일부 특징->요청된 대출 기간과 금액과 같은 수치이다.
summary(credit$months_loan_duration)
summary(credit$amount)
#기간이 4개월부터 72개월의 기한에 걸쳐 250(DM)~ 18,420(DM)
#기간의 중앙값은 18개월, 대출금의 중앙값은 2320(DM)
#DM의 환율을 약 650 ~ 750원이다. / 1990 ~ 2002까지 사용함.

#default->대출 신청자가 합의된 금액을 상환했는지 아니면
#지불 조건을 맞출 수 없어 채무 불이행 됐는지를 나타냄.
table(credit$default)
#부도율이 높으면 은행이 투자를 완전히 회수하지 못할 가능성이 있다는
#의미이기 때문에 은행에는 바람직하지 않다.

#데이터 준비 : 랜덤한 훈련 및 테스트 데이터셋 생성.
set.seed(123)
train_sample<-sample(1000,900)
str(train_sample)
credit_train<-credit[train_sample,]
credit_test<-credit[-train_sample,]
#ex)iris 데이터 샘플링
#set.seed(1234)#난수 발생을 동일하게
#index<-sample(2 ,nrow(iris),replace=TRUE)
#난수 1,2를 만드는데 iris 관측치(150) 만큼
#train_iris<-iris[index==1,]
#난수(index)가 1인 경우, iris 데이터 추출하여 train을 만듦.
#test_iris<-iris[index==2,]
#난수(index)가 2인 경우, iris 데이터 추출하여 test을 만듦.

#index<-sample(2,nrow(iris),replace=TRUE,prop=c(0.7,0.3))
#prop 옵션을 이용하여 비율 지정
#table(index) #index의 분포를 확인하기 위함.
#train_iris<-iris[index==1,]
#test_iris<-iris[index==2,]

prop.table(table(credit_train$default))
prop.table(table(credit_test$default))
#훈련 및 테스트 데이터셋에서 대출 디폴트와 유사한 분포를
#보이므로 결정트리를 사용할 수 있다.
#install.packages("party")
#ctree(formula, data)
#의사결정나무의 C5.0알고리즘을 사용해보자!
#install.packages('C50')
library(C50)
credit_train$default<-as.factor(credit_train$default)
#You have given the outcome as credit_train$default, 
#which is a 1/2 outcome, 
#but R has read it as numeric, rather than a factor:
#table(credit_train[17])

#C5.0 사용법
# 분류기 구축
#m<-C5.0(train,class,trials=1,costs=NULL)
# train : 훈련 데이터를 포함하는 데이터 프레임 또는 행렬
# class : 훈련 데이터의 각 행에 대한 클래스를 갖는 팩터 벡터
# trials:부스팅 반복 횟수를 제어하는 숫자 옵션(디폴트 값은 1)
# costs : 다양한 종류의 오류 관련된 비용을 지정하는 행렬 옵션
# 이 함수는 예측에 사용될 수 있는 C5.0 객체를 반환한다.

#예측 구축
# p<-predict(m, test,type='class')
#m:C5.0() 함수에 의해 훈련된 모델
#test : 분류기를 구축하는데 사용된 훈련 데이터와 같은 특징을 갖는
#테스트 데이터를 포함하는 데이터 프레임 또는 행렬
#type : 'class'나 'prob', 예측 결과가 가장 확률이 높은 클래스인지
# 원시 예측 확률인지를 지정
#이 함수는 type 파라미터의 값에 따라 예측 클래스 값이나
#원시 예측 확률의 벡터를 반환한다.





credit_model<-C5.0(credit_train[-17],credit_train$default)
#트리 크기:69개
summary(credit_model)
#1.수표계좌를 모르거나, >200DM이상이면 채무 불이행 가능성이 없음.
#2.그렇지 않으면, 계좌잔고가 0보다 작거나 1에서 200DM이하인 경우다.
#3.대출 이력이 완벽이나 매우 좋음이면 '채무 불이행 가능성 있음'으로 분류

#모델 성능 평가
credit_test$default<-as.factor(credit_test$default)
credit_pred<-predict(credit_model,credit_test)
library(gmodels)
CrossTable(credit_test$default,credit_pred,
           prop.chisq = FALSE,prop.c = FALSE,
           prop.r = FALSE,dnn=c('actual default','predicted default'))
#prop.r : TRUE->행 비율(Proportion row)을 포함
#prop.t : TRUE->테이블 비율(Porportion table)을 포함.
#dnn : Dimnames names을 사용자 정의 형식으로 부여할 때 사용.

#모델 성능 개선.
#C5.0 ->C4.5_+adaptive boosting
#여러 개의 의사결정 트리를 만들어서 각 예시에 대해
#최고 클래스를 투표하는 방식.
#부스팅->trials-> 몇번 시도를 하겠습니까?
credit_boost10<-C5.0(credit_train[-17],credit_train$default,trials=30)
summary(credit_boost10)
credit_boost_pred10<-predict(credit_boost10,credit_test)
CrossTable(credit_test$default,credit_boost_pred10,
           prop.chisq = FALSE,prop.c = FALSE,
           prop.r = FALSE,dnn=c('actual default','predicted default'))
#데이터셋의 적은 영향 / 관계가 더 복잡한 경우

----------------------------------------------------------------------
#mushroom
#리퍼 알고리즘(RIPPER Algorithm)
#규칙 학습 알고리즘 여러 회반복하는 방식에서 진화
#1.기르기 : 규칙에 조건을 탐욕스럽게 추가하기 위해 분할 정복 기법
#데이터의 부분집합을 완벽하게 분류하거나 분할을 위한 속성이 없어 질
#때 까지 진행, 의사 결정 트리와 비슷하게 다음 분할을 위한
#속성을 식별하는데 정보 획득량 기준이 사용.
#2.가지치기
#: 규칙의 구체성이 증가되어도 더 이상 엔트로피가 줄지 않을때 가지치기함.
#3.최적화하기.
#종료 조건은 규칙의 전체집합이 다양한 휴리스틱으로 최적화 되는 지점.
#사전 가지치기와 사후 가지치기 방법을 조합해 사용한다.
#이 방법은 아주 복잡한 규칙을 기르고, 전체 데이터셋에서 인스턴스를 
#분리하기 전에 규칙을 가지치기한다.
# 이 전략이 규칙 학습자의 성능에 도움이 되었지만,
#여전히 의사 결정 트리가 더 잘 수행이 되었다.
#장점: 
#이해하기 쉽고 사람이 읽을 수 있는 규칙을 생성함.
#크고 노이즈가 있는 데이터셋에 효율적
#일반적으로 비교 가능한 의사 결정 트리보다 좀 더 간단한 모델을 생성.
#단점 : 
#상식이나 전문가 지식에 위배되는 것처럼 보이는 규칙이 보임.
#수치 데이터 작업에 적합하지 않음.
#좀 더 복잡한 모델만큼 잘 수행되지 않을 수 있다.


#Rweka 패키지의 OneR() 함수 사용
#분류기 구축
#m<-OneR(class ~ predictors, data = mydata)
#class : 예측될 mydata 데이터 프레임의 열
#predictors:예측에 사용되는 mydata 데이터 프레임의 특징을 지정하는 R구문
#data : class와 predictors를 찾을 수 있는 데이터 프레임
#이 함수는 예측에 사용될 수 있는 1R 모델 객체를 반환한다.

# 예측
# p<-predict(m,test)
# m :OneR()함수에 의해 훈련된 모델
# test : 분류기를 구축하는데 사용된 훈련 데이터와 같은 특징을 갖는
#테스트 데이터를 포하ㅓㅁ하는 예측 클래스 값의 벡터로 변환한다.
#ex)
#mushroom_classifier<-OneR(type~odor+cap_color,data=mushroom_train)
#mushroom_prediction<-predict(mushroom_classifier,data=mushroom_test)




