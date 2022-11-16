install.packages("tidyverse") #데이터 전처리 패키지
install.packages('ggplot2')
install.packages('plotly')
install.packages('caret')# 데이터 처리 패캐지.

library(tidyverse)
library(ggplot2)
library(plotly)
library(caret)

train_set <-read.csv("C:/Users/user/Documents/train.csv")
#EDA
str(train_set)
#as.factor: 통계학에서 카테고리형 변수를 표현하는것을 factor라고 함.
train_set$Pclass<-as.factor(train_set$Pclass)
train_set$Name<-as.factor(train_set$Name)
train_set$Ticket<-as.character(train_set$Ticket)
train_set$Cabin<-as.character(train_set$Cabin)

str(train_set)
#sapply:lapply와 유사하지만, 리스트 대신에 행렬,벡터 등의
#데이터 타입으로 결과를 반환.
sapply(train_set,function(x){
  sum(is.na(x))
})

#결측치 채우기.
train_set$Age[is.na(train_set$Age)]<-median(train_set$Age,na.rm = T)
#na.rm : R / inplace: python

#요약 통계량
summary(train_set)
#Pclass : 1등급이 216명, 2등급 184명,3등급 491명으로 구성.
#성별 : Male(314) / Female(577)
# 나이는 최솟값:0.42세, 최댓값:80세, 평균->29.7
# 1분위수 20.12세,2분위수 38세, NA가 177 
#함께 탑승한 형제(Sibsp)또는 배우자의 수 / 최대 8명/평균 : 0.5
#함께 탑승한 부모 또는 자녀의 수는 최대 6명이고 평균이 0.38

#나이 데이터 전처리(Binning(구간화))
#mutate : 데이터 프레임 자료형에서 새로운 파생 column 생성
train_set <- train_set %>% 
  mutate(Ages = case_when(
    Age < 10 ~ "Under 10",
    Age < 20 ~ "10 ~ 20",
    Age < 30 ~ "20 ~ 30",
    Age < 40 ~ "30 ~ 40",
    Age < 50 ~ "40 ~ 50",
    Age < 60 ~ "50 ~ 60",
    TRUE ~ "over 60"
  )) 
train_set$Ages <- 
  factor(train_set$Ages,
         levels = c("Under 10", "10 ~ 20", "20 ~ 30", "30 ~ 40", "40 ~ 50", "50 ~ 60", "over 60"))

data_cleanging <- train_set %>% 
  group_by(Ages) %>% 
  summarise(Ages_count = n())

ggplot(data_cleanging, aes(x = Ages, y = Ages_count, fill=Ages)) +
  geom_col() +
  geom_text(aes(label=(Ages_count)), vjust=3, hjust = 0.5,color="black", size=4) +
  theme(axis.text.x = element_text(size=10)) +
  theme(axis.text.y = element_text(size=10))


#성별에 따른 생존 여부
ggplot_data<-ggplot(train_set,aes(x=Survived,fill=Sex))+
  geom_bar()+
  ggtitle('성별에 따른 생존 여부')+
  theme_bw()

ggplotly(ggplot_data,height=500,width=800)

#Pclass에 따른 생존 여부
ggplot_data<-ggplot(train_set,aes(x=Survived,fill=Pclass))+
  geom_bar()+
  ggtitle('PClass에 따른 생존 여부')+
  theme_bw()

ggplotly(ggplot_data,height=500,width=800)


dev.off()
#나이에 따른 생존 여부
ggplot_data <- train_set %>% 
  ggplot(aes(x = Survived, fill = Ages)) +
  geom_bar() +
  ggtitle(" 나이에 따른 생존 여부 ") +
  theme_bw() 

ggplotly(ggplot_data, height = 500, width = 800)

#Sibsp
ggplot_data <- train_set %>% 
  ggplot(aes( x = Survived, fill = factor(SibSp))) +
  geom_bar() +
  ggtitle( "같이 탑승한 배우자 또는 형제에 따른 생존여부") +
  theme_bw()

ggplotly(ggplot_data, height = 500, width = 800)

#Parch
ggplot_data <- train_set %>% 
  ggplot(aes( x = Survived, fill = factor(Parch))) +
  geom_bar() +
  ggtitle( "함께 탑승한 부모 또는 자녀의 수에 따른 생존 여부.") +
  theme_bw()

ggplotly(ggplot_data, height = 500, width = 800)

#Decision Tree
install.packages('rpart') #의사결정 나무
install.packages('rpart.plot') #의사결정 나무 시각화
library(rpart)
library(rpart.plot)
#의사결정나무 모델 사용
rpart_m <-rpart(Survived~ Pclass+Age+Sex,data=train_set)

#의사결정나무 시각화
prp(rpart_m,type=4,extra=1,digits=3)
#type: Tree의 타입을 결정(모든 노드의 레이블 표시.)
#extra : Tree의 추가적인 정보 설정
#(각 노드별 관측값 대비 올바르게 분류된 데이터의 비율.)







