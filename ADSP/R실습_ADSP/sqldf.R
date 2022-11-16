# R sqldf package 소개자료에 보면
#Perform SQL Selects on R Data Frames
#Manipulate R data frames using SQL

install.packages('MASS')
library('MASS')

str(Cars93)

#R의 aggregate() 함수로 차종(Type)별 도시 연비(MPG.city)와 
#고속도로 연비(MPG.highway)의 평균을 구해보겠습니다. 

# aggregate 

R_aggregate_mean <- aggregate(Cars93[,c(7,8)],
                              by = list(Car_Type = Cars93$Type), # list
                              FUN = mean, # function
                              na.rm = TRUE)
R_aggregate_mean
#번에는 install.packages()함수와 library()함수를 사용하여 sqldf Package 를 설치하고 
#호출한 후에, sqldf 패키지를 사용하여 위와 같이 차종(Type)별 
#도시 연비(MPG.city)와 고속도로 연비(MPG.highway)의 평균을 구해보겠습니다.


install.packages('sqldf')
library(sqldf)

R_sqldf_1 <- sqldf('
select "Type" as "Car_Type",
avg("MPG.city") as "mean_MPG.city",
avg("MPG.highway") as "mean_MPG.highway"
from Cars93 group by Type order by Type')
R_sqldf_1

#R의 aggregate()함수로 만든 평균과 sqldf로 만든 평균 데이터 셋을 차종(Type) 을 
#key로 항 merge 한 후에 두 값들이 서로 같은지 한번 점검해보겠습니다.

# 두개 데이터 셋 Merge, 동일 여부 check
Type_mean <- merge(R_aggregate_mean, R_sqldf_1, by = 'Car_Type')
Type_mean <- transform(Type_mean,
                       gap_MPG.city = MPG.city - mean_MPG.city,
                       gap_MPG.highway = MPG.highway - mean_MPG.highway)

Type_mean





#얼핏 보면 R의 aggregate() 함수와 sqldf 가 서로 큰 차이가 없거나 혹은 
#aggregate()함수가 더 편하다고 느낄 수도 있겠습니다.  
#그런데, 아래의 경우처럼 다수의 함수들(count, sum, avg, variance, stdev, min, max 등)을 
#그룹 변수에 대해서 구분해서 집계를 할 경우에는, 그리고 SQL에 익숙한 사용자라면 
#sqldf 패키지를 사용하는게 편할 수 있을 것입니다 

# SQL의 aggregation 함수 사용하기
R_sqldf_2 <- sqldf('
select "Type" as "Car_Type",
count("MPG.city") as "count_MPG.city",
sum("MPG.city") as "sum_MPG.city",
avg("MPG.city") as "mean_MPG.city",
variance("MPG.city") as "variance_MPG.city",
stdev("MPG.city") as "stdev_MPG.city",
min("MPG.city") as "min_MPG.city",
max("MPG.city") as "max_MPG.city"
from Cars93 group by Type order by Type desc')
# count :  행의 개수
 # sum : 합계
# avg : 평균
# var : 분산
# stddev : 표준편차
# min : 최소값
# max : 최대값
# order by xx desc : 내림차순 정렬
 
R_sqldf_2
