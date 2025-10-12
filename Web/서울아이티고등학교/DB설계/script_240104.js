// 버튼 클릭 이벤트 추가
document.getElementById('submitButton').addEventListener('click', () => {
    // 폼 데이터 가져오기
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const pizza = document.getElementById('pizza').value;
    const size = document.querySelector('input[name="size"]:checked');
    const toppings = Array.from(document.querySelectorAll('input[name="topping"]:checked'))
        .map(checkbox => checkbox.value)
        .join(', ');
    const time = document.getElementById('time').value;
    const request = document.getElementById('request').value;

    // 필수 값 체크
    if (!name || !phone || !pizza || !size) {
        alert('필수 항목을 모두 입력해주세요!');
        return;
    }

    // 데이터 출력
    alert(`고객명: ${name}\n전화번호: ${phone}\n피자 종류: ${pizza}\n피자 사이즈: ${size.value}\n추가 토핑: ${toppings || '없음'}\n희망 배달 시간: ${time || '지정하지 않음'}\n추가 요청 사항: ${request || '없음'}`);

    console.log({
        name,
        phone,
        pizza,
        size: size.value,
        toppings,
        time,
        request,
    });
});
