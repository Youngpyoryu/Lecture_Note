#factor()
#범주형 데이터를 표현하기 위한
#데이터 형태
var1<-c('A','O','AB','B','A','O','A')
var1_factor<-factor(var1)
var1_factor
#levels: 그룹으로 지정할 문자형 vector를 지정.
#만약 사용하지 않으면 데이터를
#오름 차순으로 자체적으로 지정.
nlevels(var1_factor) #ex) unique(),value_counts()
levels(var1_factor)
is.factor(var1_factor)
#ordered : TRUE 순서형, FALSE 명목형 데이터를 의미. default=FALSE
ordered(var1)

var1_factor<-factor(var1,
                    levels=c('O','A','B','AB'),
                    ordered=T)
var1_factor
table(var1_factor) #빈도수 구하기.
plot(var1_factor)

# 데이터 핸들링
x<-sample(1:10,15,rep=T) # replace->복원추출 여부.
x
others<-(x>5)
others
x[others]
ind<-which(x>1) #which : 특정 값의 위치를 찾는 함수.
ind
x[ind]
x[!others]
x[-ind] 

#예제 데이터(USArrets)
#This data set contains statistics, 
#in arrests per 100,000 residents 
#for assault, murder, and rape in 
#each of the 50 US states in 1973. 
#Also given is the percent of the population 
#living in urban areas.

#Murder: numeric Murder arrests (per 100,000)
#Assault: numeric Assault arrests (per 100,000)
#UrbanPop: numeric Percent urban population
#Rape: numeric Rape arrests (per 100,000)
head(USArrests,3)
tail(USArrests,3)
#Top 5 states with high murder rate
nidx<-order(USArrests$Murder,decreasing = T)[1:5]
nidx
USArrests[nidx,]
#logical subscripts
lidx<-(USArrests$Murder
       <quantile(USArrests$Murder,0.1))
head(lidx,10)
USArrests[lidx,]
#행과 열을 추출
subset(USArrests, UrbanPop>85)
subset(USArrests, UrbanPop<40 & Murder<10,
       select=c(Assault,Rape))
#merge
authors<-data.frame(
  surname=c('Tukey','Venables','Tierney',
            'Ripley','NcNeil'),
  nationality = c("US",'Australia','US','UK',
                  'Australia'))
books<-data.frame(
  name=c('Tukey','Venables','Tierney',
            'Ripley','Ripley','NcNeil','R core'),
  title = c('Exploratory Data Analysis(EDA)',
            'Modern Applied Statistics...',
            'LISP-STAT',
            'Spatial Statistics','Stoachastic simulation',
            'Interactive Data analysis',
            'An introduction to R'))
authors
books















