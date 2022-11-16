#변수 선언 및 사칙연산

#scalar: R의 vector 자료구조의 한 유형으로
#한개 값만 갖는 vector를 의미
a<-3
result<-a+2
result

result1<-a*3
result2<-a^2
result3<-a**2

#print() : 1개의 데이터를 출력
print(result)
print(result1)
print(result2)
print(result3)

#여러개의 데이터 출력
#cat() : 출력 후 개행이 일어나지 않음."\n"으로 개행 출력
cat('계산된 출력값은 : ', result)

cat('계산된 출력값들은 : ', result,result1)
print('계산된 출력값들은 : ', result,result1)

#Environment에 있는 모든 객체 삭제
#Console을 clear.
rm(list=ls()) #Environment 객체 삭제
cat("\014")
