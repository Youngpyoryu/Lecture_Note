# 테스트 대상 함수
def inc(x):
    return x+1

# 테스트 1
def test_answer():
    assert inc(3) == 4

#테스트 2
def test_answer2():
    assert inc(0) == 1