import pytest

# 1. (가짜) DB 연결 함수 정의 - 실제 환경에선 라이브러리를 쓰시겠죠?
class MockConnection:
    def __init__(self, name):
        self.name = name

    def begin(self):
        print(f"\n[DB Start] {self.name} 트랜잭션 시작")

    def rollback(self):
        print(f"\n[DB Rollback] {self.name} 롤백 완료")

def create_connection(name):
    return MockConnection(name)

# 2. 픽스처 정의 (xdist의 worker_id 활용)
@pytest.fixture(scope="function") 
def db_transaction(worker_id):
    # 각 워커(프로세스)마다 다른 이름의 DB를 바라보게 함 (충돌 방지 핵심!)
    db_name = f"test_db_{worker_id}" 
    
    connection = create_connection(db_name)
    connection.begin() # 트랜잭션 시작
    
    yield connection   # 테스트 실행
    
    connection.rollback() # 테스트 종료 후 롤백

# 3. 실제 테스트 함수 (병렬 실행 확인용으로 2개 만듦)
def test_example_one(db_transaction):
    print(f" --> 테스트 1 실행 중 (DB: {db_transaction.name})")
    assert True

def test_example_two(db_transaction):
    print(f" --> 테스트 2 실행 중 (DB: {db_transaction.name})")
    assert True