#install.packages('tseries')
#install.packages('forecast')
#install.packages('TTR')

library(tseries)
library(forecast)
library(TTR)
king <- scan("http://robjhyndman.com/tsdldata/misc/kings.dat", skip = 3)
king.ts <- ts(king)
plot.ts(king.ts)

#3년마다 평균을 내서 그래프를 부드럽게 표현
king.sma3 <- SMA(king.ts, n=3)
plot.ts(king.sma3)

#8년마다 평균을 내서 그래프를 부드럽게 표현
king.sma8 <- SMA(king.ts, n=8)
plot.ts(king.sma8)

#ARIMA적용->1차 차분
king.ff1 <- diff(king.ts, difference=1)
plot.ts(king.ff1)

#acf를 통해 ARIMA모델 결정
acf(king.ff1, lag.max=20)
acf(king.ff1, lag.max=20, plot=FALSE)

#PACF를 통해 lag 절단점 결정
pacf(king.ff1, lag.max=20)
pacf(king.ff1, lag.max=20, plot=FALSE)

#적절한 ARIMA 모형 찾기
auto.arima(king)

#ARIMA 적용
king.arima <- arima(king, order=c(0,1,1))
king.forecasts <- forecast(king.arima)
king.forecasts
