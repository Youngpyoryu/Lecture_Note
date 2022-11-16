#iris Species (setosa/versicolor/virginica)

install.packages("tidyverse")
library(tidyverse) #ggplot,dplyr,stringr 등 총 8개의 패키지가 내장되어 있 음.

iris # iris데이터를 불러오자.
summary(iris) # iris 데이터의 요약 통계량을 보자.

#결측치 확인하기.
table(is.na(iris))

#전반적인 변수 및 속성 확인하기.
str(iris)

#install.packages("ggvis") # 설치가 안되어 있으면 설치
library(ggvis) # 패키지 로드
# 종 도식화 %>%함수를 사용 했기 때문에 dplyr패키지 설치가 되어 있어야 한다.
iris %>% 
  ggvis(~Petal.Length, ~Petal.Width, fill = ~factor(Species)) %>%
  layer_points()

#분포 살펴보기

iris %>% 
  select(Sepal.Width) %>% 
  ggplot(mapping = aes(x = Sepal.Width))+ #aes :axis
  #stat_density : 밀도분포 그래프.
  stat_density(alpha = 0.7,
               fill = 'steelblue',
               color = 'blue')+
  labs(title = 'Distribution:Sepal.Width')
#fill : 색깔을 면적색으로 기준으로 설정하는 것.
#alpha : fille 색을 투명도를 설정할 수 있음.
ggplot(data=iris)+
  stat_density(mapping=aes(x=Sepal.Width, fill = Species), postion = 'identity')
#postion : stat_density()함수는 default로 postion이 stack이므로, identity로 각각 그려주세요.

#나머지 변수들의 분포 확인하기

A <- iris %>% 
  select(Sepal.Length) %>% 
  ggplot(mapping = aes(x = Sepal.Length))+
  stat_density(alpha = 0.6,
               fill = 'orange')
B<- iris %>% 
  select(Petal.Length) %>% 
  ggplot(mapping = aes(x = Petal.Length))+
  stat_density(alpha = 0.6,
               fill = 'green')
C <- iris %>% 
  select(Petal.Width) %>% 
  ggplot(mapping = aes(x = Petal.Width))+
  stat_density(alpha = 0.6,
               fill = 'gray')

D <- iris %>% 
  select(Species) %>% 
  ggplot(mapping = aes(x = Species))+
  geom_bar(alpha = 0.6,
           fill = 'firebrick')

gridExtra::grid.arrange(A, B, C, D, ncol = 2)

#종속변수와 개별 독립변수들 간의 관계 파악.
AA <- iris %>% 
  ggplot(mapping = aes(x = Sepal.Length, y = Sepal.Width))+
  #geom_point : ggplot함수가 만들어 놓은 좌표평면 위에, 점이라는 도형을 이용하여
  # 그래프를 그림.
  geom_point(aes(color = Species))+
  geom_smooth(method = 'lm')+ #lm : linear regression
  scale_color_brewer(palette = 'Set1')

BB <- iris %>% 
  ggplot(mapping = aes(x = Petal.Length, y = Sepal.Width))+
  geom_point(aes(color = Species))+
  geom_smooth(method = 'lm')+
  scale_color_brewer(palette = 'Set1')

CC <- iris %>% 
  ggplot(mapping = aes(x = Petal.Width, y = Sepal.Width))+
  geom_point(aes(color = Species))+
  geom_smooth(method = 'lm')+
  scale_color_brewer(palette = 'Set1')

DD <- iris %>% 
  ggplot(mapping = aes(x = Species, y = Sepal.Width))+
  geom_boxplot(aes(color = Species))+
  scale_color_brewer(palette = 'Set1')

gridExtra::grid.arrange(AA, BB, CC, DD,  ncol = 2)

iris %>% 
  ggplot(mapping = aes(x = Sepal.Length, y = Sepal.Width))+
  geom_point(aes(color = Species))+
  geom_smooth(method = 'lm')+
  facet_wrap(~Species)+
  scale_color_brewer(palette = 'Set1')

#train/test split 67%:33%
random_samples<-sample(2,row(iris),replace = TRUE,prob=c(0.67,0.33))

#train set
iris.training <-iris[random_samples==1,1:4]

#train label
iris.trainLabels<-iris[random_samples==1,5]

#test set
iris.test<-iris[random_samples==2,1:4]

#test label
iris.test<-iris[random_samples==2,5]

#라이브 러리 세팅

library(class)

#k=3에 대해 KNN 실행.
iris_model<-knn(train=iris.training, test = iris.test,cl = iris.trainLabels,k=3)





