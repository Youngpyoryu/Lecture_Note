#출처 : https://rfriend.tistory.com/80
#예제로 사용할 데이터는 MASS 패키지에 내장되어 있는 Cars93 데이터 프레임의 차종(Type),
#제조국(Origin), 도시 연비(MPG.city), 고속도로 연비(MPG.highway) 4개의 변수를 사용해서
#가지의 경우의 수를 조합해 가면서 데이터를 녹였다가 (melt) 재구조화 (cast) 를 해보겠습니다.
str(Cars93)
table(Cars93$Type)


#데이터 양이 너무 많으면 melt(), cast()를 적용했을 때 데이터 구조가 변화하는 모양을 보기가 쉽지
#않기 때문에 차종(Type) 중에서 개수가 적은 "Compact"와 "Van" 만 선별해서 예제로 사용하겠습니다.

table(Cars93$Type)
Cars93_sample <- subset(Cars93, 
                        select = c(Type, Origin, MPG.city, MPG.highway), 
                        subset = (Type %in% c("Compact", "Van"))) 
Cars93_sample
dim(Cars93_sample)


#reshape 패키지의 melt(),cast()함수를 이용한 데이터 재구조화
# reshape package installation, 
install.packages("reshape")
library(reshape)
#이제 melt(data, id.vars, measure.vars) 함수를 사용해서 기존 데이터셋을 녹여보도록 하겠습니다.

# melt()
Cars93_sample_melt <- melt(data = Cars93_sample, 
                             id.vars = c("Type", "Origin"), 
                             measure.vars = c("MPG.city", "MPG.highway"))
Cars93_sample_melt
dim(Cars93_sample_melt)

#melt()함수를 사용해 녹인 데이터를 cast()함수를 사용해서 재구조화 해보자.
#세로와 가로에 무슨 별수가 넣을지가 결정되었다면 아래의 예제를 참고해서 구조에 맞게 작성하면 됨.
#fuction란에는 R에서 사용할 수 있는 통계량 함수를 사용하면 되며, 이번 예제에서는 평균(mean)함수를 사용.

#cast
options(digits = 3)
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

