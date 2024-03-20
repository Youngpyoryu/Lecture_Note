--desc employees;
--EMPLOYEE_ID는 사원번호 저장되어 있음. PK
--HIRE_DATE는 입사한 날짜.
--JOB_ID는 현재 수행하고 있는 업무
--SALARY는 사원이 받고 있는 월 급여,
--COMMISSION_PCT는 보너스 값이 저장되어 있음. / 보너스를 받지 않는 사원들의 경우 NULL ->빈 공간
--MANAGER_ID는 이 사원을 관리하고 있는 관리자(사수)의 사원 번호가 저장되어 있음.
--DEPARTMENT_ID는 사원이 근무하고 있는 부서 번호이고, 이 컬럼이 employees 테이블의 FK

--desc departments;
--DEPARTMENT_ID는 부서의 번호로 이 컬럼이 departments 테이블의 Primiary key(PK)이다.
--DEPARTMENT_NAME은 부서의 이름을 저장되어 있음.
--MANAGER_ID에는 부서를 관리하는 관리자, 즉, 부서장의 사원 번호가 저장되어 있음.
--LOCATION_ID에는 부서가 위치한 지역의 지역번호가 저장되어 있음. / departments의 foregien key(FK)이다.


--desc locations
--LOCATION_ID는 부서가 위치한 지역의 지역 번호가 저장되어 있음. locations 테이블의 PK이다.
--STREET_ADDRESS는 주소, 자주 사용하지 않으니 안 외워도 됨.
--POSTAL_CODE는 우편번호 / 자주 쓰이지 않음.
-- CITY는 부서가 위치한 도시이름.
-- STATE_PROVINCE와 COUNTRY_ID도 사용하지는 않음.