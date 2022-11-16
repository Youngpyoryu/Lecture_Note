dat <-get(data(mtcars))
head(dat)

?mtcars #?:설명보는 것.

cor.test(dat$cyl,dat$hp) #cyl(실린더의 갯수) /hp:마력

plot(dat$cyl,dat$hp)

#다른 변수들의 상관관계를 확인하고 싶은데
# 두 변수 씩 짝지어 하나하나 코드를 돌려야 하나?
round(cor(dat),3)

#corrplot
#install.packages('corrplot')
library(corrplot)
corrplot(round(cor(dat),3))

#상관계수를 그림과 한번에 비교하는 방법.
corrplot(round(cor(dat),3),method = 'number')

#linear regression
lm_fit <-lm(hp~cyl,data = dat) #lm(formula,data,...)

summary(lm_fit)

plot(dat$cyl,dat$hp)
abline(lm_fit)

#formula+0
lm_fit_0<-lm(hp~cyl+0,data=dat)
summary(lm_fit_0)

plot(dat$cyl,dat$hp,xlim=c(0,8),ylim=c(-60,350))
abline(lm_fit_0)

#다중 선형회귀 분석
multi_fit<-lm(hp~cyl+wt,data=dat)
summary(multi_fit)

install.packages('car')
library(car)
vif(multi_fit)





