#f(x)=x^3+2x^2+7

x<-x0 #초기값 setting
f<-x^3+2*x^2-7
tolerance<-0.000001
while (abs(f)>tolerance){
  f.prime<-3*x^2+4*x #gradient 방향
  x<- x-f / f.prime
  f<-x^3+2*x^2-7
}
x

x<-x0 #초기값 setting
f<-x^3+2*x^2-7
tolerance<-0.000001
repeat (abs(f)<tolerance) break
  f.prime<-3*x^2+4*x #gradient 방향
  x<- x-f / f.prime
  f<-x^3+2*x^2-7
}
x

Eratosthenes<-function(n){
  #(에라토스테네스의 체에 근거해서)
  #n까지 모든 소수를 반환하라.
  if (n>=2){
    #소수값의 배수를 명확하게 소거하고 싶으면
    #noMultiples로 부르는 작은 함수에
    #그 동작을 포함시킴으로써 가능하다.
    noMultiples<-function (j) sieve([sieve%%j]!=0)
    sieve<-seq(2,n) #2,3,4,5,6,7,
    prime<-c()
    for (i in seq(2,n)){
      if (any(sieve==i)){
        prime<-c(prime,i)
        sieve<-c(sieve[(sieve%%i)!=0],i)
      }
    }
    return(prime)
  }else{
    stop('Input value of n should be at least 2')
  }
}

#p.137 함수의 효력이 미치는 범위
#변수의 범위(Scope)는 변수가 인식되는 장소를 의미.
f<-function(){
  x<-1
  g() #<- g는 지역변수 x에 영향을 주지 않을 것이다.
  return(x)
}

g<-function(){
  x<-2 #이는 f함수의 지역변수 x가 아니라, 
  #g 함수의 지역변수 x를 변경한다.
}
f()






