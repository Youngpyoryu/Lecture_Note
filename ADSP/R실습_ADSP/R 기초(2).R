a<-1
b<-3

result<-a/b
result
options(digits=10) #숫자를 몇 자리까지 출력할 것인가?
#default=7
result
#sprintf(): print와 유사하지만 주어진 인자들을 특정한 규칙에
#맞게 변환해 출력해주는 차이점이 존재
#%d : 부호 있는 십진법으로 나타난 정수
#%f : 십진법으로 나타낸 부동 소수점 수
#%s : 문자열
sprintf("%0.7f",a/3)
sprintf("결과값 : %f", a/3)

result1<- a %/% b #몫 구하기 1/3 = 0.33333
result1

result2<- a %% b #나머지 구하기 1/3 = 0.3333
result2
