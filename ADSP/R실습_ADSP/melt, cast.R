#예제로 사용할 데이터는 MASS 패키지에 내장되어 있는 Cars93 데이터 프레임의 차종(Type), 
#제조국(Origin), 도시 연비(MPG.city), 고속도로 연비(MPG.highway) 4개의 변수를 사용해서 
#몇가지의 경우의 수를 조합해 가면서 데이터를 녹였다가 (melt) 재구조화 (cast) 를 해보겠습니다.

#출처: https://rfriend.tistory.com/80 [R, Python 분석과 프로그래밍의 친구 (by R Friend)]

install.packages('MASS')
library('MASS')
str(Cars93)


#데이터 양이 너무 많으면 melt(), cast()를 적용했을 때 데이터 구조가 변화하는 모양을 보기가 쉽지 않기 때문에 
#차종(Type) 중에서 개수가 적은 "Compact"와 "Van" 만 선별해서 예제로 사용하겠습니다.

table(Cars93$Type)

Cars93_sample<-subset(Cars93, select = c(Type,Origin, MPG.city, MPG.highway), 
                      subset = (Type %in% c('Compact','Van')))
                      
Cars93_sample

#R의 reshape 패키지는 별도의 설치가 필요합니다. 

install.packages("reshape")
library(reshape)

Cars93_sample_melt <- melt(data = Cars93_sample, 
                           id.vars = c("Type", "Origin"),
                           measure.vars = c("MPG.city", "MPG.highway"))

Cars93_sample_melt


#이렇게 melt()함수를 사용해 녹인 데이터를 cast()함수를 사용해서 재구조화 해보겠습니다.
#cast()
options(digits=3) #  소숫점 너무 밑에 까지 나오지 않도록 설정

# 한개의 id.var 기준(세로) & variable(가로) 조합의 value 값에 mean 함수 적용
cast(data = Cars93_sample_melt, Type ~ variable, fun = mean)

cast(data = Cars93_sample_melt, Origin ~ variable, fun = mean)

# 두개의 id.var 기준(세로) & variable(가로) 조합의 value 값에 mean 함수 적용


cast(data = Cars93_sample_melt, Type + Origin ~ variable, fun = mean)


# 한개의 id.var 기준(세로) & 다른 id.var + variable (가로) 조합의 value 값에 mean 함수 적용

cast(data = Cars93_sample_melt, Type ~ Origin + variable, fun = mean)

cast(data = Cars93_sample_melt, Origin ~ Type + variable, fun = mean)


# 한개의 id.var + variable (세로) & 다른 id.var (가로) 조합의 value 값에 mean 함수 적용

cast(data = Cars93_sample_melt, Type + variable ~ Origin, fun = mean)

cast(data = Cars93_sample_melt, Origin + variable ~ Type, fun = mean)
