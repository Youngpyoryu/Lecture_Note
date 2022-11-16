#비교연산자 : 두 값의 비교로서 맞으면 TRUE
#맞지 않으면 FALSE를 반환
a<-100
b<-200

a==b
a!=b

a>b
a<b
!(a<=b)
#할당 연산자 : 변수에 값을 할당(저장)하는데 사용
#오른쪽에서 왼쪽으로 저장.

a=100
a<-300

b<-200
cat(a,b)

#논리연산자 : 논리식을 판단하여, 참(true)과 거짓(false)를 반환. 

# 조건에 있는 값이 scalar면 &와 &&가 동일처리
TRUE & FALSE      # FALSE
TRUE && FALSE     # FALSE

# 조건에 있는 값이 scalar면 |와 ||가 동일처리
TRUE | FALSE      # TRUE
TRUE || FALSE     # TRUE

# 조건에 있는 값이 vector이면 
# &는 vector의 모든 조건에 대한 연산을 수행한 후 
# 결과를 vector로 return
# &&는 vector의 첫번째 조건에 대한 연산을 수행한 후
# 결과를 scalr로 return

c(TRUE,FALSE) & c(TRUE,TRUE)   # TRUE FALSE
c(TRUE,FALSE) && c(TRUE,TRUE)  # TRUE
c(TRUE,FALSE) & c(TRUE,TRUE,FALSE)  # Error

!c(TRUE,FALSE,TRUE)            # FALSE TRUE FALSE