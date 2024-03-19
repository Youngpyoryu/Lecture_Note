--select * from employees;

--DESC employees -- 자료형

-- employess에 대한 first name, last name, salary 출력해보자!
--select first_name, last_name, salary from employees;

-- JOB_ID를 봐보자!
--select JOB_ID from employees; -- 중복이 있으므로 보기가 힘듦.

-- 중복 제거
--select distinct JOB_ID from employees;

-- 문자열끼리 더하기('||' 기호 사용)
-- employees에서 first name과 last name의 문자열을 더하고 salary도 함께 출력해보자!
--select first_name || ' ' || last_name, salary from employees;
--select first_name || last_name, salary from employees;
-- ' '을 쓰지 않으면 문자들이 붙어서 출력이 됨.

--집계함수
-- 직원들이 받는 월급 중 가장 많은 월급 구하기!(max)
--select max(salary) from employees;

-- 직원들 중에 가장 최근에 입사(hire_date)한 날짜 구하기(max)
--select max(hire_date) from employess;

-- 직원들이 받는 월급 중 가장 낮은 월급 구하기!
--select min(salary) from employees;

-- 직원들 중 가장 먼저 입사한 날짜 구하기!!!
--select min(hire_date) from employees;

-- 전체 직원 수 구하기(count)
--select count(*) from employees;

-- 월간 급여로 지출되는 총 금액을 구하기
--select sum(salary) from employees;

-- 직원들의 평균 월급 구하기
--select avg(salary) from employees; 

-- 직원들의 평균 월급 구하기(소수점 이하 자리는 버리기)
--select floor(avg(salary)) from employees;

-- 연봉이 12000 이상되는 직원들의 LAST_NAME 및 연봉을 조회한다.
--select LAST_NAME, salary 
--    from employees 
--    where salary>=12000;

-- 연봉이 12000 이상되는 직원들의 ID(DEPARTMENT_ID) LAST_NAME를 출력하세요.
--select LAST_NAME, DEPARTMENT_ID 
--from employees 
--where salary>=12000;

-- 연봉이 5000 에서 12000의 범의 이외인 사람들의 LAST_NAME 및 연봉을 조회한다.
select LAST_NAME, salary 
from employees 
where 	salary<=5000
or		salary>=12000;


