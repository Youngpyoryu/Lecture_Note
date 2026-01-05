from langchain_core.prompts import ChatPromptTemplate  # ChatPromptTemplate 클래스 가져오기

# 예전 경로: from langchain.chat_models import ChatOpenAI
# 현재 권장 경로: langchain-openai 패키지에서 가져오기
from langchain_openai import ChatOpenAI  # ChatOpenAI 클래스 가져오기


# 메세지로 구성된 프롬프트 구성
prompt = ChatPromptTemplate.from_messages(
    [
        (
            # AI의 기본값과 작동 방식 설정
            # AI에게 번역 봇 역할
            "system",
            "You are a translator bot. Translate sentences from {source_language} to {target_language}.",
        ),
        (
            # 번역을 원하는 문장에 해당하는 변수
            "human",
            "Translate this: {sentence}",
        ),
    ]
)

chat = ChatOpenAI(
    temperature=0.1,  # 낮을수록 응답의 무작위성을 줄일 수 있음

    # API key 추가
    # (실습용) 코드에 직접 넣기
    api_key="sk-proj-여기에_본인키_붙여넣기",

    # 모델 선택
    model="gpt-4o-mini",  # 계정 권한에 따라 변경
)

# 체인 생성 (액션 순서 지정)
# 파이프 연산자(|)는 각 구성요소를 다음 구성요소로 연결하고 실행시킴
# LangChainExpression Language(LCEL) : 여러 단계로 이루어진 매우 복잡한 체인을 구성할 수 있으며, 체인을 다른 체인과 연결하여 병렬로 실행 가능
# chair = prompt | chat | output_parser # 랭체인은 프롬프트의 형식 지정 > 채팅 모델에 전달 > 결과를 출력 파서를 통해 실행
chain = prompt | chat  # prompt 형식 지정 > prompt를 LLM에 전달

# response = chain.invoke() # invoke 메서드를 사용하여 체인 실행
# 입력값 유효성 검사 필요
# 템플릿은 필요한 모든 입력이 있는지 선 검증 과정을 필수로 함
# source_language, target_language, sentence
# 템플릿에 필요한 변수 제공
response = chain.invoke(
    {
        "source_language": "en",
        "target_language": "ko",
        "sentence": "I love you",
    }
)

# LangChain의 Chat 모델 응답은 보통 AIMessage 형태이므로 content를 출력하는 것이 안전
print(response.content)
