#vector : 한가지 타입의 데이터를 한 개 이상
#저장할 수 있는 1차원 배열 형태의 데이터 타입
x<-1 #원소의 갯수가 1개인 vector
x<-1:10 #1씩 증가하는 연속적인 숫자

#숫자들을 저장하는 벡터
num_vector<-c(1,3,4,10,15) #c():combine 함수
#매개변수들로 이루어진 벡터를 생성
num_vector[1]
num_vector[3] #R에서 인덱스는 1부터 시작.
num_vector[4]

#논리값(boolean)들을 저장하는 벡터
bool_vector<-c(TRUE,FALSE,FALSE,TRUE)
bool_vector[4]
text_vector<-c('One','two','three')
text_vector

v1<-c(1,2,TRUE,TRUE)
v1[2]
v1[4]

#vector 생성 - c()
var1<-c(10,30,77,100)
var1

var2<-c(89,56,33)
var2

var3<-c(TRUE,FALSE,FALSE,TRUE)
var3

var4<-c('홍길동','강감찬','유관순')
var4

var5<-c('홍길동',100, TRUE, 3.141592)
var5

var6<-c(var1,var2)
var6

var7<-c(var1,var4)
var7

#vector생성 - :
var1 = 1:5
var1

var2 = 5:0
var2

var3=3.3:10
var3

#vector 생성-seq()
var1 = seq(from=1, to=5, by=1)
var1

var2 = seq(from=0.5, to=10, by=1.5)
var2

var3 = seq(from=10, to=5, by=-2)
var3

#vector생성-rep() #replicate 함수
var1 = rep(1:3,times=3) #times 생략 가능
var1 #1 2 3 1 2 3 1 2 3

var2 = rep(1:3, each=3) # each ; 각 원소가 반복할 횟수 지정
var2

#vector의 Data Type

help(mode)
var1 = c(10,20,50,100)
var1
mode(var1) #numeric
is.character(var1) #FALSE
is.numeric(var1) #TRUE
is.integer(var1) #FALSE
is.double(var1) #TRUE

#vector의 갯수확인 - length()

var1 = seq(1,100,2)
var1

var2 = c(10,20,30)
var2

length(var1) #var1의 개수-50
length(var2) #var2의 갯수 3

var3 = seq(1,100,length=4) #length를 이용한 vector 생성
var3

#vector 데이터 추출

var1 = c(67,90,80,50,100)
var1

var1[1] #67
var1[length(var1)] #100
var1[2:4] #90 80 50
var1[c(1,2,5)] # 67,90,100
var1[seq(2,4)] # 90 80 50
var1[6] # NA
var1[-1] #1번째를 제외한 나머지
var1[-(2:5)] #67
var1[-c(1,2,4,5)]

#vector의 원소 이름
var1 = c(10,20,30)
var1

names(var1) #NULL

names(var1) = c('국어','영어','수학')

names(var1) #"국어", "영어", "수학

var1 #이름과 데이터 함께 출력

var1[1] #index를 이용한 vector 원소 접근

var1["국어"] #name을 이용한 vector 원소 접근

#seq과 rep연습

v1<-c(1,2,TRUE, FALSE)
v1[2]
v1[4]
v1

v2<-c(123,'two',FALSE) #문자열로 자동 형변환
v2
#R에서의 자동 형변환
#유연성이 더 높은 타입으로 자동 형변환
# 유연성 : 논리타입<정수타입<실수타입<문자열

v3<-c(TRUE,1, 1.1)
v3

v4<- seq(1,5) #v4 <-1:5
v4
v5 <-seq(1,10,2)
v5

v6<-seq(10, 0, -2)
v6

v7<-rep(1,10)
v7

v8<- rep('*8',5)
v8

v9<-sep(1,20)
v9[c(1,2)] #v9[1],v9[2]
v9[seq(2,10,2)] #v9[2], v9[4], v9[6], v9[8], v9[10]

#vector간의 연산
var1 = 1:3
var2 = 4:6

var1
var2

var1*2
var1+10

var1+var2

var3 = 1:6
var3

var1+var3

var4 = 1:5
var4

var1+var4

#vector의 집합연산
var1 = c(1,2,3,4,5)
var2 = seq(3,7)

union(var1,var2) #합집합
intersect(var1,var2) #교집합
setdiff(var1,var2) #차집합

#vector간의 비교연산
var1 = c('홍길동',' 김길동','최길동')
var2 = c('HONG','KIM','CHOI')
var3 = c('김길동','홍길동','김길동','최길동')
#The safe and reliable way to test two objects for being exactly equal. 
#It returns TRUE in this case, FALSE in every other case.
identical(var1,var3) #FALSe

setequal(var1,var3) #True

var1 = 1:3
var2 = c(1:3)
var3 = c(1,2,3)

class(var1); class(var2) ; class(var3)
identical(var1,var2)
idnetical(var1,var3)


#행렬 구조
m1<-matrix(c(1:6), nrow=3, ncol=2)
m1
m2<-matrix(c(1:6),nrow=3,ncol=2,byrow=TRUE)
m2
rnames<-c('행1','행2','행3')
cnames<-c('col1','col2')
r_c_names<-list(rnames,cnames)

m3<-matrix(c(1:6),nrow=3,ncol=2,byrow=FALSE,dimnames=r_c_names)
m3
m3[2,1]
m3[1,]
m3[[2,1]][1]
m3[1,][1]


#행렬
#matrix 생성

var1 = matrix(c(1:5)) #열을 기준으로 matrix 생성
var1 #5행 1열 matrix

#nrow 속성을 이용하여 지저오딘 행을 가지는 matrix 생성
#열 기준으로 데이터가 채워짐

var2 = matrix(c(1:10), nrow=2)
var2 #2행 5열의 matrix

var3 = matrix(c(1:13),nrow = 3)
var3

#matrix 생성 시 행 우선으로 데이터를 생성하는 경우
var4 = matrix(c(1:10), nrow=2, byrow=T)

var4 = matrix(c(1:10), nrow=2, byrow=T)
var4                      

# vector를 대상으로 rbind()는 행 묶음으로 matrix를 생성
# vector를 대상으로 cbind()는 열 묶음으로 matrix를 생성

var5 = c(1,2,3,4)
var6 = c(5,6,7,8)

mat1 = rbind(var5, var6)
mat1         

mat2 = cbind(var5, var6)
mat2

# 데이터 타입과 데이터 구조 확인
mode(mat1)             # numeric
class(mat1)            # matrix

matrix의 원소 접근

var1 = matrix(1:21, nrow=3, ncol=7)
var1

var1[2,2]             # 2행 2열 : 5

var1[2,]              # 2행

var1[,3]              # 3열

var1[c(1,3), c(5:7)]     # 1,3행 & 5~7열

length(var1)             # 모든 원소 개수 : 21
nrow(var1)               # 행 개수 : 3
ncol(var1)               # 열 개수 : 7

# matrix적용 함수 : apply()
# X : matrix, MARGIN : 1이면 행, 2면 열
# FUN : 행렬 자료구조에 적용할 함수

apply(X=var1, MARGIN=1, FUN=max)    # 행단위 최대값

apply(X=var1, MARGIN=2, FUN=min)    # 열단위 최소값

#matrix 연산

# matrix 연산

var1 = matrix(c(1:6), ncol=3)
var1

var2 = matrix(c(1,-1,2,-2,1,-1), ncol=3)
var2

var1*var2   # elementwise product(element단위의 곱연산)

t(var1)     # transpose matrix (전치행렬)

var3 = matrix(c(1,-1,2,-2,1,-1), ncol=2)
var3

var1 %*% var3   # matrix product (행렬곱)

# 역행렬 : matrix A가 nxn matrix일 때, 
# 아래를 만족하는 nxn matrix B가 존재하면 B를 A의 역행렬이라 한다.
# AB = BA = I(단위행렬 E)
# 가우스 조던 소거법을 이용하여 계산.

var1 = matrix(c(1,2,3,3,0,1,5,4,2), ncol=3)
var1

solve(var1)     # matrix inversion (역행렬)

# R array
# array 생성

var1 = array(c(1:24), dim=c(3,2,4)) # 1~24의 데이터를 이용
# 3행 2열 4면의 3차원 array 생성

var1 

#factor
# factor 생성

var1 = c("A", "O", "AB", "B", "A", "O", "A")
var1

var1_factor = factor(var1)

var1_factor                   # factor이기 때문에 
# data와 level이 같이 출력

nlevels(var1_factor)          # factor의 level개수
# 4 

levels(var1_factor)           # factor의 level 목록
# "A"  "AB"  "B"  "O"

is.factor(var1_factor)        # factor인지를 판단

ordered(var1)                 # 순서형 factor 생성

# level과 order 지정
# level에 지정이 안되면 NA로 처리
var1_factor = factor(var1, 
                     levels = c("O","A","B"), 
                     ordered = T)
var1_factor


var1_factor = factor(var1, 
                     levels = c("O","A","B","AB"), 
                     ordered = T)
var1_factor

levels(var1_factor) = c("A형","AB형","B형","O형")
levels(var1_factor)           

var1_factor                  # 결과를 꼭 확인해보자

# 남성과 여성의 데이터르 factor 생성 후 chart 그리기

gender = c("MAN", "WOMAN", "MAN", "MAN", "WOMAN")
gender

factor_gender = as.factor(gender)
factor_gender

table(factor_gender)     # 빈도수 구하기

plot(factor_gender)      # 빈도수로 막대그래프 생성

# list 

var_scalar = 100                            # scalar
var_scalar

var_vector = c(10,20,30)                    # vector
var_vector

var_matrix = matrix(1:4,nrow = 2,ncol = 2)  # matrix
var_matrix

var_array = array(1:8, dim=c(2,2,2))        # array
var_array

var_df = data.frame(id=1:3, age=c(10,15,20)) # data frame
var_df

var_factor = factor(c("A","B","C","A","B","A")) # factor
var_factor

my_list = list(var_scalar,
               var_vector,
               var_matrix,
               var_array,
               var_df,
               var_factor)
my_list


#dataframe

# data frame 생성

# vector를 이용한 data frame 생성
no = c(1,2,3)
name = c("홍길동","최길동","김길동")
pay = c(250,150,300)

df = data.frame(NO=no,Name=name,Pay=pay)

df

# matrix를 이용한 data frame 생성
mat1 = matrix(data = c(1,"홍길동",150,
                       2,"최길동",150,
                       3,"김길동",300),
              nrow = 3,
              by=T)           # 행 우선

mat1

memp = data.frame(mat1)
memp

# 3개의 vector를 이용하여 data frame 생성
df = data.frame(x=c(1:5),
                y=seq(2,10,2),
                z=c("a","b","c","d","e"))
df

# data frame의 column을 참조하기 위해서는 $ 이용

df$x           # 1 2 3 4 5

# str() 함수의 사용

df = data.frame(x=c(1:5),
                y=seq(2,10,2),
                z=c("a","b","c","d","e"))

str(df)

# 'data.frame':	5 obs. of  3 variables:
# $ x: int  1 2 3 4 5
# $ y: num  2 4 6 8 10
# $ z: Factor w/ 5 levels "a","b","c","d",..: 1 2 3 4 5

df = data.frame(x=c(1:5),
                y=seq(2,10,2),
                z=c("a","b","c","d","e"),
                stringsAsFactors = F)
df
str(df)    # factor가 아닌 문자열 형태로 사용

# summary() 함수의 사용

summary(df)

# apply() 함수의 사용
df = data.frame(x=c(1:5),
                y=seq(2,10,2),
                z=c("a","b","c","d","e"))

apply(df[,c(1,2)],2,sum) 

# subset() 함수의 사용

df = data.frame(x=c(1:5),
                y=seq(2,10,2),
                z=c("a","b","c","d","e"))

sub1 <- subset(df, x>=3)   # x가 3이상인 행 추출
sub1

sub2 <- subset(df, x>=3 & y<=8)
sub2
