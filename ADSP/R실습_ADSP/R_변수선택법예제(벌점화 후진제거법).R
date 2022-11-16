# ElemStratLearn 패키지 다운 방법 : https://carriedata.tistory.com/entry/R-%ED%8C%A8%ED%82%A4%EC%A7%80-%EC%84%A4%EC%B9%98-%EC%98%A4%EB%A5%98-%EC%8B%9C-%ED%95%B4%EA%B2%B0-%EB%B0%A9%EB%B2%95
library(ElemStatLearn)
Data = prostate
#-ncol(Data) -> -10 ->train column drop
data.use = Data[, -ncol(Data)]
lm.full.Model = lm(lpsa~., data = data.use)

#후진제거법에서 AIC를 이용한 변수선택
backward.aic = step(lm.full.Model, lpsa~1, direction = 'backward')
