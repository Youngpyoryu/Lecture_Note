#상황 설정 : "각 부대에서 올라온 보급 물자 요청 내역이 문자열로 뒤죽박죽 섞여서 도착했습니다. 
# 이걸 품목별로 합산해서 보고해야 합니다. 그런데 대소문자도 엉망이고,
# 품목이 계속 늘어날 텐데 if문으로 다 짤 수가 없습니다."

data = "Rifle-10, ration-50, rifle-5, Ammo-100, Ration-20, helmet-50"

def calc_supplies(text):
    # 콤마로 대충 자름
    items = text.split(',')
    
    # 변수를 일일이 만듦 (매우 비효율적)
    rifle_cnt = 0
    ammo_cnt = 0
    ration_cnt = 0
    
    for i in items:
        # 하이픈(-)으로 이름과 수량을 나눔
        parts = i.split('-')
        name = parts[0].strip() # 공백 제거
        qty = int(parts[1])     # 숫자로 변환
        
        # 하나하나 비교 (노가다)
        if name == "Rifle":
            rifle_cnt = rifle_cnt + qty
        elif name == "Ammo":
            ammo_cnt = ammo_cnt + qty
        elif name == "ration": # 대소문자 처리를 안 함 (Ration은 무시됨)
            ration_cnt = ration_cnt + qty
            
    print("소총: " + str(rifle_cnt))
    print("탄약: " + str(ammo_cnt))
    print("식량: " + str(ration_cnt))

calc_supplies(data)