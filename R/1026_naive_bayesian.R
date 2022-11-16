#나이브 베이즈
#조건부 확률
#확률 : 0에서 1사이의 숫자로 가용한 증거를 고려해
#사건이 발생할 가능성을 표현한 것.
#장점:
#간단하고 빠르고 매우 효율적
#노이즈와 누락 데이터를 잘 처리한다.
#훈련에는 상대적으로 적은 예시가 필요하지만,
#대용량의 예시에도 매우 잘 작동이 됨.
#예측용 추정 확률을 쉽게 알 수 있다.
#단점 : 
#모든 특징이 동등하게 중요하고 독립이라는 가정이 잘못된 
#경우가 자주 있다.
#수치 특징이 많은 데이터셋에는 이상적이지 않다.
#추정된 확률이 예측된 클래스보다 덜 신뢰할 만하다.
sms_raw<-read.csv('C:/Users/Kims/Downloads/sms_spam.csv',
                  stringsAsFactors=FALSE)
#stringsAsFactors
#데이터의 유형이 문자형인 경우는 데이터 프레임을 생성할때 
#argument를 주지 않아도 기본적으로 TRUE값을 가지며 
#요인(factor)으로 변경
str(sms_raw)
sms_raw$type<-factor(sms_raw$type)
str(sms_raw$type)
table(sms_raw$type)

#SMS 메시지 ->문자 
#숫자와 구두점 제거 방법, and, but,or같은 관심 없는 단어의
#처리 방법과 문장을 개별 단어로 나누는 방법
# R에서 tm을 지원해줌.
install.packages('tm')
#아직도 개발중이므로 주기적으로 설치해주는게 좋다.
library(tm)
#텍스트 데이터 처리의 첫 단계는 텍스트 문서의 모음(코퍼스(Corpus))

#코퍼스를 생성하려면, 휘발성(volatile)코퍼스를 참조하는
#tm 패키지의 Vcorpus()
sms_corpus<-VCorpus(VectorSource((sms_raw$text)))
#VCorpus()함수에 readerControl 파라미터를 지정하면 PDF 파일이나
#MS 워드 파일과 같은 출처에서 텍스트 가져오기를 할 수 있음.
#자세한 건 vignette('tm')명령으로 tm 패키지를 살펴볼 수 있다.
#vignette('tm')
print(sms_corpus)#5559개의 문서가 포함되어 있다.
#tm코퍼스->복합 리스트 ->리스트 연산을 사용가능.
#inspect() : 결과의 요약을 보여줌.
inspect(sms_corpus[1:2])
#metadata : 일반적으로 데이터에 관한 구조화된 데이터
#metadata : 데이터에 관한 구조화된 데이터로써,
#다른 데이터를 설명해주는 데이터.

#문자를 봐보자!
as.character(sms_corpus[[1]])
lapply(sms_corpus[1:2], as.character)
#tm_map() : tm 코퍼스에 변환을 적용할 수 있는 함수.
#일련의 변환을 통해, 코퍼스를 정리하고 corpus_clearn함수에 저장.
sms_corpus_clean<-tm_map(sms_corpus,
                          content_transformer(tolower))
#tolower : 대문자인 경우 소문자로 바꾸는 함수.
as.character(sms_corpus_clean[[1]])
lapply(sms_corpus_clean[1:2], as.character)
#content_transformer()함수가 
#grep(->지정한 문자열을 포함하는 인덱스 포함)패턴 매칭과 대체처럼
#더 정교한 텍스트 처리와 정리 과정을 적용하려고 할 때 쓰임.
sms_corpus_clean<-tm_map(sms_corpus_clean,removeNumbers)
#stopwords(불용어 ex) and,or,but,to....))
sms_corpus_clean<-tm_map(sms_corpus_clean,removeWords,
                         stopwords())
#불용어 목록에 있는것을 removeword로 삭제해주세요.
sms_corpus_clean<-tm_map(sms_corpus_clean,removePunctuation)
#구두점 제거 . 을 제거해주세요.
removePunctuation('hello...world')
#형태소 분석기 설치
#install.packages('SnowballC')
library(SnowballC)
wordStem((c('learn','learned','learning','learns'))) #어원 찾기.
sms_corpus_clean<-tm_map(sms_corpus_clean,
                         stemDocument)
sms_corpus_clean<-tm_map(sms_corpus_clean,
                         stripWhitespace)
lapply(sms_corpus[1:2], as.character)
lapply(sms_corpus_clean[1:2], as.character)
#문자를 숫자로 변경해줌. DTM(Document Term matrix)
sms_dtm<-DocumentTermMatrix(sms_corpus_clean)
sms_dtm2<-DocumentTermMatrix(sms_corpus, control=list(
  tolower=TRUE,
  removeNumbers=TRUE,
  stopwords=TRUE,
  removePunctuation = TRUE,
  stemming = TRUE
))
#불일치의 원인: 사전 처리 단계 순서에 따라 다르다.
sms_dtm_train<-sms_dtm[1:4169,]
sms_dtm_test<-sms_dtm[4170:5559,]
sms_train_lables<-sms_raw[1:4169,]$type
sms_test_lables<-sms_raw[4170:5559,]$type

#train과 test label의 비율을 봐보자!
prop.table(table(sms_train_lables))
prop.table(table(sms_test_lables))
#install.packages("wordcloud")
library(wordcloud)
wordcloud(sms_corpus_clean,min.freq =50,random.order=FALSE)
#random.order를 명시하지 않았다면 구름을 디폴트로 랜덤하게
#정렬.

#자주 사용하는 단어의 지시자 특성 생성
sms_freq_words<-findFreqTerms(sms_dtm_train,5)
str(sms_freq_words)
sms_dtm_freq_train<-sms_dtm_train[,sms_freq_words]
sms_dtm_freq_test<-sms_dtm_test[,sms_freq_words]

#나이브 베이즈 분류->대개 범주형 특징으로 데이터로 훈련
#단어의 출현 여부에 따라 예/아니오 나타내는 범주형 변수가 필요
convert_counts<-function(x){
  x<-ifelse(x>0,'Yes','No')
}
#값이 0보다 크면 Yes, 아니면 0
#fuction은 앞에서 배운 lapply함수와 비슷하다.
sms_train<-apply(sms_dtm_freq_train,MARGIN=2,
                 convert_counts)
sms_test<-apply(sms_dtm_freq_test,MARGIN=2,
                 convert_counts)
#MARGIN=2(열), MARGIN=1(행)
#install.packages('e1071')
library(e1071) #머신러닝 패키지가 많다.
#m<-naiveBayes(train,class,laplce=0)
#train : 훈련 데이터를 포함하는 데이터 프레임 또는 행렬
#class : 훈련 데이터의 각 행에 대한 클래스를 갖는 팩터 벡터
#laplace : 라플라스 추정기를 제어하는 숫자(default=0)
#이 함수는 예측에 사용될 수 있는 나이브 베이즈 객체를 반환.

#predict
#p<-predict(m,test, type='class')
#m : naiveBayes()함수에 의해 훈련된 모델
#test : 분류기를 구축하는데 사용된 훈련 데이터와 같은 특징을 갖는 
#테스트 데이터를 포함하는 데이터 프레임 또는 행렬
#type : 'Class'나 'raw', 예측 결과가 가장 확률이 높은 클래스인지
#원시 예측 확률인지를 지정
# 이 함수는 type 파라미터의 값에 따라 예측 클래스 값이나
#원시 예측 확률의 벡터를 반환.
#ex) sms_classifier<-naiveBayes(sms_train,sms_type)
#ex) sms_prediction<-predict(sms_classifier,sms_test)


sms_classifier<-naiveBayes(sms_train,sms_train_lables)
sms_test_pred<-predict(sms_classifier,sms_test)
library(gmodels)
CrossTable(sms_test_pred,
           sms_test_lables,
           prop.chisq=FALSE, prop.c=FALSE,
           prop.r=FALSE,dnn=c('predicted','actual'))
#prop.r : TRUE->행 비율(Proportion row)을 포함
#prop.t : TRUE->테이블 비율(Porportion table)을 포함.
#dnn : Dimnames names을 사용자 정의 형식으로 부여할 때 사용.

## 라플라스 추정량
#나이브 베이즈 공식에서 확률은 조건부 확률로 이루어졌기 때문에, 우도가 0%라면 해당 사후확률을 0으로 만들어, 다른 증거를 실질적으로 무효화하고 기각하게 만든다. 
#이에 대한 해결책으로 '라플라스 추정량'을 사용하게 된다. 
#* A 예시가 다른 예시들이 갖고 있는 특징들을 갖고 있지 않으면, A 예시에 대한 확률은 0이 된다. 

#라플라스 추정량은 빈도표의 각 합계에 작은 숫자를 더하는데, 특징이 각 클래스에 대해 발생할 확률이 0이 되지 않게 보장한다. 
#보통 라플라스 추정량은 1로 설정해서 데이터에 각 클래스 특징 조합이 최소 한번은 나타나게 보장한다. 

#R 에서 라플라스 추정량의 디폴트 값은 0이다.




