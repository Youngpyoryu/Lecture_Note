d <- matrix(1:9, ncol = 3)

#apply example

# 행별로 합
apply(d, MARGIN = 1, sum)
rowSums(d)
#MARGIN으로 행과 열을 선택

# 열별로 합
apply(d, MARGIN = 2, sum)
colSums(d)

#lapply() : list로 반환됨.
d <- c(1, 2, 3)
result <- lapply(d, function(x) {x * 2})

#결과를 vector로 바꾸고 싶다면,
unlist(result)

x <- list(a = 1:3, b = 4:6)
lapply(x, mean)

#sapply : 결과를 matrix, vector등의 데이터 타입으로 반환
lapply(iris[ , 1:4], mean)

sapply(iris[ , 1:4], mean)

class(sapply(iris[ , 1:4], mean))

#lapply ()와 다르게 sapply()는 numeric으로 결과를 반환.
#이를 역시 dataframe으로 바꾸는 것이 가능.
x <- sapply(iris[ , 1:4], mean)
as.data.frame(x)

#위에서 봤던 모양으로 바꿀려면 전치행렬로 바꿔야함.
as.data.frame(t(x))

#많은 컬럼을 포함하는 데이터 프레임을 볼 때 각 컬럼의 데이터 타입을 보는 방법.
sapply(iris, class)

str(iris)

#tapply() : 그룹별로 function을 적용하기 위해 사용.
tapply(X = iris$Sepal.Length, INDEX = iris$Species, mean)
#3가지 종이 존재하고 각각의 sepal length에 대한 평균을 확인할 수 있습니다.
#이번에는 조금 더 복잡한 그룹화를 해봅시다.

m <- matrix(11:18, ncol = 2, dimnames = list(c("spring", "summer", "fall", "winter"), 
                                             c("male", "female")))
m
#4x2의 행렬이 만들어졌습니다. 여기서 반기별 성별 셀의 합을 구할 겁니다.

#다시 말해, 봄, 여름의 남성과 여성 셀 각각의 합 그리고 가을, 겨울의 남성과 여성 셀 각각의 합을 구합니다.

#상기 행렬에서 INDEX를 지정 시, (n, m)에서 n을 먼저 나열한 뒤 m 값을 나열하면 됩니다.

#일단 행부터 묶는것이고 spring, summer는 첫 번째 그룹이니 1을 할당하고, fall, winter는 2를 할당합니다.

#열을 묶을 때는 male을 첫 번째 그룹으로 1에 할당하고 female은 2에 할당합니다.

#이것을 코드로 표현하면 아래와 같습니다.


#mapply() : mapply()는 다수의 인자를 받아 처리하는 함수가 있고 함수에 넘겨줄 인자들이 데이터로 저장되어 있을 때, 데이터에 저장된 값들을 인자로 하여 함수를 호출합니다.

#rnorm()을 사용하여 정규분포를 따르는 난수를 발생시킨 뒤 mapply()에 적용시켜 보겠습니다.

#일단, rnorm(n = 1, mean = 0, sd = 1) / rnorm(n = 2, mean = 10, sd = 1) / rnorm(n = 3, mean = 100, sd = 1) 세 개의 값들을 호출해야 되는 상황이라고 가정해 봅시다.

#첫 번째 방법은 위의 함수 3개를 각각 호출하는 것입니다.

rnorm(n = 1, mean = 0, sd = 1)
rnorm(n = 2, mean = 10, sd = 1)
rnorm(n = 3, mean = 100, sd = 1)
mapply(rnorm, c(1, 2, 3), c(0, 10, 100), c(1, 1, 1))
