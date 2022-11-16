#Gradient Descent with R code

## 샘플 데이터 생성.
x=runif(300,-10,10) #runif(n, min, max) / n은 생성할 난수의 수,
#min,max난수의 범위 / 범위를 생략하면 0에서 1사이의 난수.

Noise=rnorm(n=300,mean=0,sd=3) 
#1.rnorm : 난수함수(정규분포에 의거)
#2.확률밀도함수:  dnorm
#3.누적분포함수: pnorm
#4.분위수함수 : qnrom
y = x+Noise

DF<-data.frame(x=x,y=y)

remove.packages("ggplot2") # Unisntall ggplot
install.packages("ggplot2") # Install it again

library(ggplot2)

ggplot(DF,aes(x= x, y= y)) +
  geom_point(col = 'royalblue') +
  theme_bw() 

#geom_point : 점찍는것,
#theme_bw : 그래프의 배경색을 하얀색으로 만든다

#Learning_rate 설정(hyperparameter)
alpha = 0.01

#초기 가중치 행렬 생성.
Weights = matrix(c(0,0),nrow = 2)
Weights

#회귀식 계산을 위한 행렬 생성.
##행렬형태로 만들어 줌.
X = matrix(x)
X = cbind(1,X)
colnames(X) = c('V1','V2')
X

#Error Loss function 
#%*% : 행렬의 곱셈을 할 때 사용 함.
Error = function(x, y, Weight){
  sum(( y - x %*% Weight )^2) / (2*length(y))
} 

#알고리즘 학습
#학습을 돌리기 전에 Error(cost,Residual)값과
#가중치(회귀계수)가 저장될 빈 공간을 만들어야 함.

Error_surface = c()
Weight_value = list()

for ( i in 1 : 300){
  # X는 (300,2) 행렬
  # Weights (2,1)행렬 
  # X * Weights => (300,1) 행렬[각 데이터에서의 Error 연산]
  error = (X %*% Weights - y)
  # Delta Funtion 계산
  Delta_function = t(X) %*% error / length(y)
  # 가중치 수정
  Weights = Weights - alpha * Delta_function
  Error_surface[i] = Error(X, y, Weights)
  Weight_value[[i]] = Weights 
}

#시각화
p = ggplot(DF,aes(x=x,y=y))+
  geom_point(col='royalblue',alpha=0.4)+
  theme_bw()
for (i in 1:300){
  p = p+geom_abline(slope=Weight_value[[i]][2],
                    intercept=Weight_value[[i]][1],
                    col = 'red',alpha=0.4)
}
p
#error function 수렴성
DF$num = 1:300
DF$Error_value = Error_surface

ggplot(DF)+
  geom_line(aes(x=num,y=Error_value),group=1)+
  geom_point(aes(x=num,y=Error_value))+
  theme_bw()+
  ggtitle('Error function')+
  xlab('Num of iterations')

#일반 선형회귀(최소제곱(자승)법(least square method))
REG = lm(y~x)
A = summary(REG)
print(paste('R Square:',round(A$r.squared,4)))

# Gradient   / #intercept
GR_MODEL = Weight_value[[300]][1]+Weight_value[[300]][2]*x 
#slope
actual = y
rss = sum((GR_MODEL-actual)^2)
#tss = sum((actual) - mean(actual)^2)
tss = sum((actual - mean(actual))^2)
rsq = 1-rss/tss #R^2

print(paste('R square:',round(rsq,4)))



