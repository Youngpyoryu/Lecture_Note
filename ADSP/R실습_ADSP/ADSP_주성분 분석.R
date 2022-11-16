library(datasets)
data(USArrests)
pairs(USArrests, panel=panel.smooth, main="USArrests data")

US.prin <- princomp(USArrests, cor = TRUE)
summary(US.prin)
screeplot(US.prin, npcs=4, tpye="lines")

loadings(US.prin)
US.prin$scores


arrests.pca <- prcomp(USArrests,center = TRUE,scale. = TRUE)
biplot(arrests.pca, scale=0)
