x<-1:10
mean(x)
sum(x)
var(x)
sum (x-mean(x)^2) / 10

#날짜와 시간
some.evens<- NULL #요소가 없는 벡터를 생성.
some.evens[(seq(2,20,2))]<-seq(2,20,2)
some.evens

is.na(some.evens)
x<-c(0,1,2)
x/x
1/x
!is.na(some.evens)
#짝수만 보여줄수 있는것
some.evens[!is.na(some.evens)]

# 패키지, 라이브러리,저장소
#install.packages('knitr')
#Provides a general-purpose tool for dynamic report generation in R using Literate Programming techniques.
library(knitr)
#search(): 어떤 패키지가 로딩되어 있는지.
search()
#강제로 특정 패키지로부터 해당 함수를 선택하려면,
#함수 이름 앞에 패키지 이름과 ::을 붙인다.
stats::median(x)
#수행하는 함수를 찾으려면 ??
# help.search()

??median
hist(islands)
x<-seq(1:10)
y<-x^2-10*x
plot(x,y)
#단변량 수학 함수(Univariate mathematical function)
#<-> 다변량 수학함수(multivariate mathemtical function)
#curve()
curve(expr=sin,from=0,to=6*pi)

#기본 내장 함수
median(x) # x데이터의 50번째 백분위수 또는
#중앙값 Q2 quantile(50%)
var(x) # x데이터의 분산 계산
summary(x) #x데이터의 일부 요약 통계량 계산
length(x)
min(x)
max(x)
pmin(x,y)
#x-y 데이터의 쌍별 최솟값 계산.
pmax(x,y)
#x-y 데이터의 쌍별 최댓값 계산.
range(x) #x 데이터의 최댓값과 최솟값 차이 계산.
quantile(x) #x데이터의 사분위수 계산.

#Boolean 대수
a<-c(TRUE,FALSE,FALSE,TRUE)

b<-c(13,7,8,2)
b[a]
sum(a)
!a
a & (b-2)

##관계연산자
threeM<-c(3,6,9)
threeM>4 #어떤 요소가 4보다 큰가요?
threeM==4 #어떤 요소가 4인가요?
threeM>=4 #어떤 요소가 4보다 크거나 같나요?
threeM!=4 #어떤 요소가 4와 같지 않나요?
threeM[threeM>4] #threeM중 어떤 요소가 4보다 큰가요?
four68<-c(4,6,8)
four68>threeM #four68 요소가 해당 threeM요소보다
#큰가요?
foure68[threeM<four68] #출력

#P.68 리스트 구축하기
x<-c(3,2,3)
y<-c(7,7)
z<-list(x=x,y=y)
z
#lapply():벡터,리스트 또는 표현식에 함수를 적용하여
#그 결과를 리스트로 반환 / 결과가 리스트
w<-lapply(z,mean)
class(w)
#vapply():결과가 벡터
vapply(z,mean,1)
vapply(z,summary,numeric(6))

#apply예제
d<-matrix(1:9,ncol=3)
apply(d,MARGIN = 1,sum)
rowSums(d)
#MARGIN: 행과 열을 선택
d<-matrix(1:9,ncol=3)
apply(d,MARGIN = 2,sum)
colSums(d)

#lapply(): list로 반환됨.
d<-c(1,2,3)
result<-lapply(d,function(x) {x*2})
#결과를 vector로 바꾸고 싶다면,
unlist(result)

x<-list(a=1:3, b=4:6)
lapply(x,mean)
#sapply():결과를 matrix,vector등의 데이터 타입으로 
#변환
lapply(iris[,1:4],mean)
sapply(iris[,1:4],mean)
class(sapply(iris[,1:4],mean))
x<-sapply(iris[,1:4],mean)
as.data.frame(x)

#tapply():그룹별로 function을 적용하기 위해 사용.
tapply(X=iris$Sepal.Length,INDEX=iris$Species,
       mean)



















