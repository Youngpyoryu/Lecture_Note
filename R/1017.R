#plot : 저수준의 함수 ->직관적으로 
#알아보기 쉬움. ->시각화가 가장 중요.
# 1.plot()함수
x<-rnorm(100,sd=2) #mu=100,standard deviation=2
?rnorm #Normal distribution(정규분포)
y<-0.3+2*x+rnorm(100,sd=1)
#y = ax+b+입실론(white noise)
plot(x)
#MASS: Support Functions and Datasets for Venables and Ripley's MASS
library(MASS)
head(Animals)
Animals['body'] , Animals.body
plot(x=Animals$body,y=Animals$brain,
     pch=16, col='blue',
     xlab='Body Weight(kg)',
     ylab='Brain weight(g)',
     xlim=c(0,250),ylim = c(0,1400))
text(x=Animals$body,y=Animals$brain,
     labels=row.names(Animals), pos=4)
#그림 범례(legend) 표시

#xlab: x,y축 이름 / pch : 점의 종류
#cex : 점의 크기, col :색상,
#xlim,ylim : x,y축의 값 범위
plot(~Sepal.Length+Sepal.Width, data=iris, 
     pch=rep(15:17, each=50), 
     col=c("red", "blue", "green")[iris$Species], 
     cex=1.5,main='iris data') 
legend("topright", legend = levels(iris$Species), 
       pch=15:17, 
       col=c("red", "blue", "green"), cex=1.2,
       bty="o") #bty:box type /n:None,o:box하는것.
#barplot
pie.sales<-c(0.12,0.3,0.26,0.16,0.04,0.12)
barplot(pie.sales,
        names.arg = c('Blueberry','Cherry',
                      'Apple','Boston Cream',
                      'Other','Vanilla Cream'),
        las=2)
names(pie.sales)<-c('Blueberry','Cherry',
                    'Apple','Boston Cream',
                    'Other','Vanilla Cream')
barplot(pie.sales,las=2) #las=2 : x-tick
#barplot options:
counts<-table(mtcars$vs, mtcars$gear)
#counts
#count1<-data.frame(mtcars$vs, mtcars$gear)
#count1
barplot(counts,main='Car distribution by gears and VS',
        xlab='Numer of Gears', col=c('darkblue','red'),
        legend=rownames(counts),horiz=T,angle=45)
pie(pie.sales)
#par()함수
x<-rnorm(100)
par(mfrow=c(1,2))
hist(x);plot(x)
#cars dataset : 자동차의 속도(speed)와 
#정지시까지의 거리(dist)
data(cars)
head(cars,3)
tail(cars,3)

hist(cars$speed, nclass=8, main='Histogram',
     xlab='speed')
#box plot(수염그림, 상자수염그림)
boxplot(Sepal.Length~Species,data=iris,main='Box plot')
#scatter plot(산점도)
plot(cats)
#abline
plot(Petal.Length~ Sepal.Length,
     data=iris,
     bty='l' ,pch=20)
abline(a=0,b=1,lty=2,lwd=2)
#lty = 0, lty = "blank" : 그리지 않음
#lty = 1, lty = "solid" : 실선 (기본값)
#lty = 2, lty = "dashed" : 대시
#lty = 3, lty = "dotted" : 점
#lty = 4, lty = "dotdash" : 점과 대시
#lty = 5, lty = "longdash" : 긴 대시

#lwd(line width)
abline(lm(Petal.Length ~ Sepal.Length,
          data=iris), lty=1,lwd=2)
#여러개의 산점도를 동시에 그리기:pair()
pairs(iris[,1:4], main="Fisher's Iris data",
      pch=21, bg=c('red','green3','blue')
[unclass(iris$Species)])
















