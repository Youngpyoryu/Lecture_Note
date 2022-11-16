#install.packages('rpart')
#install.packages('party')
#install.packages('ROCR')

library(rpart)
library(party)
library(ROCR)

x <- kyphosis[sample(1:nrow(kyphosis), nrow(kyphosis), replace=F),]
x.train <- kyphosis[1:floor(nrow(x)*0.75),]
x.evaluate <- kyphosis[floor(nrow(x)*0.75):nrow(x),]
x.model <- cforest(Kyphosis~Age+Number+Start, data=x.train)
x.evaluate$prediction <- predict(x.model, newdata=x.evaluate)
x.evaluate$correct <- x.evaluate$prediction == x.evaluate$Kyphosis
print(paste("% of predicted classification correct", mean(x.evaluate$correct)))
x.evaluate$probabilities <- 1- unlist(treeresponse(x.model, newdata=x.evaluate), use.name=F)[seq(1,nrow(x.evaluate)*2,2)]

pred <- prediction(x.evaluate$probabilities, x.evaluate$Kyphosis)
perf <- performance(pred, "tpr", "fpr")
plot(perf, main="ROC curve", colorize=T)

perf <- performance(pred, "lift", "rpp")
plot(perf, main="lift curve", colorize=T)
