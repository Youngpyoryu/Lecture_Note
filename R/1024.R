WorldPhones51<-WorldPhones
WorldPhones51
summary(WorldPhones51)
barplot(WorldPhones51)
#2e+05 -> 2*10^5
barplot(WorldPhones51,cex.names=0.75,
        cex.axis=0.75,
        main = 'Numbers of Telephones in 1951')
#cex.names : 범주형,  x축 이름인 라벨의 문자 크기
#cex.axis: 좌표축, y축에 출력되는 수치형 라벨의 문자
#크기"
dotchart(WorldPhones51,xlab="Number of Phones('000s')")

VADeaths
#1940년 Virginia주의 다양한 부분 모집단에 대한 사망률
barplot(VADeaths,
        beside=TRUE,
        legend = TRUE,
        ylim = c(0,90),
        ylab = 'Deaths per 1000',
        main = 'Death rates in virginia')
#beside : 우측 상단 범례를 추가.
dotchart(VADeaths,xlim=c(0,75),xlab='Deaths per 1000',
         main='Death rates in Virginia',cex=0.8)
#cex : 그래프 문자의 크기 조절.

#P.921 QQplot 
#정규성 검정 / ex) log, box-cox transformation
#두 집단의 분포 또는 표본과 기준 분포를 비교하기 위하여
#사용. / 가설검정 : H_0 VS H_1 VS H_2(X)
#R^2 ->회귀 정확도? ->두집단->공분산(피어슨)->연속형
#분류 ->스피어만 상관계수->연속형+범주형
#단일 표본을 기준분포에 대해 표현할 때,
#이론 변위치는 하나의 좌표 대해 사용된다.
par(mfrow=c(1,4))
#par : 그래프의 모양을 다양하게 조절할 수 있는
#그래픽 인수들을 설정하고 조회하는 함수.
# -> 그래프를 그릴 때, 파라미터를 조절해주는 함수.
X<-rnorm(1000) #Normal distribution
A<-rnorm(1000)
qqplot(X,A,main='main A and X are same')

B<-rnorm(1000,mean=3,sd=2)
qqplot(X,B,main='B is rescaled X')

C<-rt(1000,df=2) #rt: The Student t distribution.
#t분포 : 모집단 표준편차를 알 수없을 때,
#표본평균과 평균 사이 표준화된 거리를 설명.
# 표본이 증가하면 중심극한정리를 따름
# 중심극한정리 : 표본이 증가하면 정규분포분포로
#수렴.
qqplot(X,C,main='C has heavier tails')

D<-rexp(1000) #The Exponential Distribution
#지수분포 : 특정한 사건이 일어나고,
#그 다음에 같은 사건이 다시 일어날 때까지
#걸리는 시간에 대한 분포.
#무기억성 : 어떤 시점부터 소요되는 시간은
#과거 시간에 영향을 받지 않는다.
#EX)어떤 전구를 한달간 사용했을 때,
#남은 전구 수명은 한달간 사용했던 것에 영향을
#받지 않고, 그냥 새 전구의 수명과 같다는 것.
#ex) 핸드폰을 5년 썼는데 고장나기까지 걸리는 
#시간은 처음 산 뒤 고장나기까지 걸리는 시간과 같다.
#어떤 사건의 발생 횟수가 포아송 분포를 따른다면,
#사건 사이의 대기 시간은 지수분포를 따름.
#포아송 분포 : 어떤 사건이 몇번 발생할 것 인가를표현.
qqplot(X,D,main='D is skewed to the right')

##고급 그래프 선택 시 고려사항
#1. 데이터의 유형(범주형, 연속형)
#2. 독자(여러분 자신 또는 충분히 교육받은 독자
#를 위한 것이라면 보다 정교하게 이해시키려고
#생각하면 된다.)
#ex) qqplot
#RcolorBrewer패키지는 다수의 팔레트(Palettes) 또는
#색상을 선택할 수 있는 사양을 포함한다.
#저급 그래픽 함수 : barplot(), dotchart(), plot()
#abline() -> seaborn-> regplot()
plot(circumference~age,pch=as.numeric(
  as.character(Tree)),data = Orange)
#pch : 점의 종류(숫자나 문자를 지정할 수 있음)
#0~18은 S언어가 사용하던 특수문자
# 19~25는 R이 확장하여 사용하는 특수 문자
#26~31은 사용되지 않은 값
#23~127은 아스키 코드에 해당.
#example(points)를 실행하면 각 Pch값이 어떤 기호를
#의미하는지 볼 수 있다. 
#문자로 지정하면 지정한 문자로 그래프를 그린다.
#install.packages("ggpubr")
#library(ggpubr)
#ggpubr::show_point_shapes()
abline(lm(circumference~age,data=Orange,
       subset=Tree=='1'),lty=1)
abline(lm(circumference~age,data=Orange,
          subset=Tree=='2'),lty=2)
abline(lm(circumference~age,data=Orange,
          subset=Tree=='3'),lty=3,lwd=2)
abline(lm(circumference~age,data=Orange,
          subset=Tree=='4'),lty=4)
abline(lm(circumference~age,data=Orange,
          subset=Tree=='5'),lty=5)
legend('topleft',legend=paste('Tree',1:5),
       lty=1:5,pch=1:5,
       lwd=c(1,1,2,1,1))

#4장. 프로그래밍
#프로그래밍 : 단순한 명령보다
#상대적으로 복잡한 명령 체계를 작성하는 것을 포함
#for (name in vector) {commands}
#ex) n factorial
n<-100
result<-1
for (i in 1:n)
  result<-result*i
result


#피보나치 수열
Fibonacci<-numeric(12)
Fibonacci[1]<-Fibonacci[2]<-1
for (i in 3:12)
  Fibonacci[i]<-Fibonacci[i-2]+Fibonacci[i-1]
Fibonacci
#install.packages("" '')
#pip install pakages ->python
library(grid)
for (i in 1:100){
  vp<-viewport(x=.46,h=.9,w=.9,angle = i)
  pushViewport(vp)
  grid.circle()
}
#if (condition) {command when TRUE}
#if (condition) {command when TRUE} else {command when TRUE}
#.Indent(들여쓰기)
#if conidition(){
  # do TRUE
#else {
#  }
#}
#ex)
x<-3
if (x>2) y<-2*x else y<-3*x
y
#x>2 조건은 TRUE이므로 y는 2*3=6으로 할당된다.
#참이 아니였다면 y는 3*x로 할당되었을 것이다.
corplot<-function(x,y,plotit){
  if (plotit==TRUE) plot(x,y)
  cor(x,y)
}
corplot(c(2,5,7),c(5,6,8),FALSE)

Eratosthenes<-function(n){
  #(에라토스테네스의 체에 근거해서)
  #n까지 모든 소수를 반환하라.
  if (n>=2){
    sieve<-seq(2,n) #2,3,4,5,6,7,
    prime<-c()
    for (i in seq(2,n)){
      if (any(sieve==i)){
        prime<-c(prime,i)
        sieve<-c(sieve[(sieve%%i)!=0],i)
      }
    }
    return(prime)
  }else{
    stop('Input value of n should be at least 2')
  }
}
Eratosthenes(50)
Eratosthenes(-50)







