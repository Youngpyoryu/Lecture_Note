patient_id<-1:4
patient_id
age<-c(25,34,28,52)
age
type<-c("Type1","Type2","Type2","Type1")
type
status<-c("poor","Improved","Ecellent","poor")
status
df_patient<-data.frame(patient_id,age,type,status)
df_patient
str(df_patient)
head(df_patient,n=2)
tail(df_patient,n=2)
str(mtcars)
mtcars
summary(mtcars)

#dataframe에서특정컬럼(변수)의 내용만 확인
df_patient$patient_id
df_patient$age

mtcars$hp#벡터(vector)
mtcars["hp"]
mtcars[c("mpg","cyl","wt")]


head(mtcars,n=2)
mtcars["MazdaRX4",]

plot(mtcars$wt,mtcars$mpg)
