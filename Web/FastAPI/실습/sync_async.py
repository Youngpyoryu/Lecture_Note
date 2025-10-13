# 동기적 처리 예제 -> 지연 -> 시간이 누적.
import time

def sync_task(name,delay):
  print("시작")
  time.sleep(delay)
  print(f"{name} 완료 (지연 : {delay}'s)")
  
def run_sync():
  start = time.time()
  sync_task("작업1",2)
  sync_task("작업2",3)
  end = time.time()
  print(f"총 실행시간 : {round(end-start,2)}초")
run_sync()


import asyncio #비동기적 처리 방식.

async def async_task(name,delay):
    print(f"{name} 시작")
    await asyncio.sleep(delay)
    print(f"{name} 완료 (지연 : {delay}'s)")

async def run_async():
    start = asyncio.get_event_loop().time()
    await asyncio.gather(
        async_task("작업 1", 2),
        async_task("작업 2",3)
    )
    end = asyncio.get_event_loop().time()
    print(f'총 실행시간 : {round(end-start,2)} 초')
asyncio.run(run_async())