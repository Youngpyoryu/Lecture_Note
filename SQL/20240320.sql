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

--모든 사람들의 LAST_NAME, 부서명, 지역 ID 및 도시 명을 조회한다.
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY from employees E,departments D, Locations L where E.Department_ID = D.department_ID and D.location_ID = L.location_ID;
-- 시애틀에 사는 사람만 호출.
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY from employees E,departments D, Locations L where E.Department_ID = D.department_ID and D.location_ID = L.location_ID and L.city = 'Seattle';

-- 시애틀에 사는 사람만 호출 -> 서브쿼리로 호출해보세요!
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY
--from employees E,departments D, Locations L
--where E.Department_ID = D.department_ID
--and D.location_ID = L.location_ID
--and L.location_ID = (
--    				 select LOCATION_ID
--    				 from LOCATIONS
--   				 where city = 'Seattle'
--);
-- PK로 조회하는 것.
-- LAST_NAME이 DAVIES인 사람보다 후에 고용된 사원들의 LAST_NAME 및 HIRE_DATE를 조회해보자.
--SELECT  LAST_NAME,HIRE_DATE
--FROM    EMPLOYEES
--WHERE   HIRE_DATE >=  (
--                        SELECT  HIRE_DATE
--                        FROM    EMPLOYEES
--                        WHERE   LAST_NAME = 'Davies'
--                      )
--ORDER   BY HIRE_DATE
--;

-- 회사 전체의 최대 연봉, 최소연봉, 연봉 총 합 및 평균 연봉은 자연수(Round)로 포맷하여 조회한다.
--select max(salary), min(salary), sum(salary), round(avg(salary))
--from employees;

-- 각 JOB_ID 별, 최대 연봉, 최소 연봉, 연봉 총합 및 평균 연봉을 자연수(ROUND)로 포맷하여 조회한다.
--select JOB_ID, MAX(salary) MAX, min(salary) MIN, sum(salary) SUM, round(avg(salary)) AVG
--from employees
--group by JOB_ID
--order by JOB_ID;

--group by : 동일한 값을 가진 컬럼을 기준으로 그룹별 연산을 적용함.
-- 항상 그룹함수와 함꼐 스임. 
--select department_id, round(avg(salary))
--from employees
--group by department_id;
-- group by : 그룹 함수를 group by절에 지정된 컬럼의 값이 행에 대해서 통계 정보를 계산.
-- group by를 활용하여서 컬럼(부서)별(department_id)로 평균 월급 그룹 함수를 계산하여라!
--select round(avg(salary))
--from employees
--group by department_id;

-- 2개 이상의 그룹화
--select department_id 부서번호, job_id 직업, sum(salary)
--from employees
--group by department_id,job_id
--order by department_id;

--select department_id 부서번호, job_id 직업, manager_id 상사번호, sum(salary)
--from employees
--group by department_id,job_id,manager_id
--order by department_id;
--having  : groupby절에 의해 생성된 결과 값 중 원하는 조건에 부합하는 데이터만 보고자 씀.
--select department_id, round(avg(salary)) 평균급여
--from employees
--group by department_id
--having avg(salary)<7000;

--select job_id, sum(salary) 급여총액
--from employees
--where job_id not like '%PER%'
--group by job_id
--having sum(salary)>13000
--order by sum(salary);

-- 매니저의 사번 및 그 매니저 밑 사원들 중 최소 연봉을 받는 사원의 연봉을 조회함.
-- 매니저가 없는 사람들은 제외, 최소 연봉이 6000미만인 경우는 제외, 연봉 기준 역순으로 조회
--select MANAGER_ID, MIN(SALARY)
--from employees
--where MANAGER_ID is not null
--group by MANAGER_ID
--having MIN(SALRY) >=6000 
--order by MIN(SALRY) Desc;

-- 회사 전체 평균보다 더 받는 사원들의 사번 및 LAST_NAME을 조회한다.
--select employee_id,LAST_NAME
--from employees
--where salary >= (
--    			select avg(salary)
--    			from employees);





