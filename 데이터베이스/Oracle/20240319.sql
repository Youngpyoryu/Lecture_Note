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
--select LAST_NAME, salary from employees where salary>=12000;

-- 연봉이 12000 이상되는 직원들의 ID(DEPARTMENT_ID) LAST_NAME를 출력하세요.
--select LAST_NAME, DEPARTMENT_ID from employees where salary>=12000;

-- 연봉이 5000 에서 12000의 범의 이외인 사람들의 LAST_NAME 및 연봉을 조회한다.
--select LAST_NAME, salary from employees where salary<=5000 or salary>=12000;
--select HIRE_DATE from employees;
-- 05/MAR/20일부터 08/AUG/01 사이에 고용된 사원들의 LAST_NAME 사번(EMPLOYEE_ID), 고용일자(HIRE_Date)를 조회한다.
--select LAST_NAME, EMPLOYEE_ID, HIRE_DATE from employeeswhere HIRE_DATE >='20-MAR-05'and   HIRE_DATE <='01-AUG-08';
-- 고용일자 순으로 정렬한다.
--select LAST_NAME, EMPLOYEE_ID, HIRE_DATE from employees where HIRE_DATE between TO_DATE('20-MAR-05') and TO_DATE('01-AUG-08') ORDER BY HIRE_DATE;

-- 20번 및 50번 부서에서 근무하는 사원들의 LAST_NAME 및 부서 번호(DEPARTMENT_ID)를 알파벳순으로 조회한다.
--select LAST_NAME, DEPARTMENT_ID from employees where DEPARTMENT_ID in (20,50) order by LAST_NAME ASC; --DESC

-- 2005년에 고용된 모든 사람들의 LAST_NAME 및 고용일 조회한다.
--select LAST_NAME, HIRE_DATE from employeeswhere to_char(HIRE_DATE, 'yyyy') = '2008';

--스페링이 o인 사원의 이름을 찾을 때 쓰는 명령어
--select last_name from employees where last_name like '_o%';

-- 이름의 첫 스펠링이 A이거 두번째 스펠링을 뭔지 모르겠고, 세번째 스펠링이 o인 사원을 검색해보자.
--select last_name from employees where last_name like 'A_o%';

-- 매니저(MANAGER_ID)가 없는 사람들의 LAST_NAME 및 JOB_ID를 조회한다.
--select LAST_NAME, JOB_ID, MANAGER_ID from employees where MANAGER_ID is null OR MANAGER_ID  = '';
-- 매니저(MANAGER_ID)가 있는 사람들의 LAST_NAME 및 JOB_ID를 조회한다.
--select LAST_NAME, JOB_ID, MANAGER_ID from employees where MANAGER_ID is not null OR MANAGER_ID  != '';

--커미션(COMMISSION_PCT)을 버는 모든 사원들의 LAST_NAME, 연봉 및 커미션을 조회함.
-- 연봉 역순, 커미션 역순차로 정렬해보자.
-- select LAST_NAME, SALARY, COMMISSION_PCT from employees where NOT(COMMISSION_PCT is null) ORDER BY SALARY DESC, COMMISSION_PCT DESC;

-- LAST_NAME의 네번째 글자가 a인 사원들의 LAST_NAME을 조회한다.
--select LAST_NAME from employees where LAST_NAME like '___a%';

-- LAST_NAME에 a및 (OR) e 글자가 있는 사원들의 LAST_NAME을 조회한다.
--select LAST_NAME from employees where LAST_NAME LIKE '%a%' or    LAST_NAME LIKE '%e%';

-- 연봉이 2500, 3500, 7000이 아니며, 직업이 SA_REP이나 ST_CLERK인 사람들을 조회한다.
--SELECT LAST_NAME, JOB_ID, SALARY  from employees where salary NOT in (2500,3500,7000) and JOB_ID in ('SA_REP','ST_CLERK');

-- 작업이 AD_PRESS인 사람은 A등급을 , ST_MAN인 사람을 B등급, IT_PROG인 사람은 C등급을, SA_REP인 사람은
-- D등급을, ST_CLERK인 사람은 E등급을 기타는 0을 부여하여 조회
-- DECODE : SQL에서 데이터를 비교하고 조건에 따라 다른 값을 반환하는 함수.
--select *
--from (
--   select EMPLOYEE_ID, --서브쿼리
--    FIRST_NAME, 
--    LAST_NAME,
--    DECODE(JOB_ID
--    	   ,'AD_PRESS', 'A'
--    	   ,'ST_MAN','B' 
--  		   ,'IT_PROG','C'
--    	   ,'SA_REP','D'
--    	   ,'ST_CLERK','E',
--           ,'0')JOB_GRADE
--    	from EMPLOYEES
--    )
--WHERE JOB_GRADE = 'B'
--;

-- 모든 사원들의 LAST_NAME, 부서 이름 및 부서 번호 조회한다.
--SELECT  EMPLOYEE_ID, LAST_NAME,DEPARTMENT_NAME, D.DEPARTMENT_ID FROM    EMPLOYEES E,DEPARTMENTS D WHERE   E.DEPARTMENT_ID = D.DEPARTMENT_ID;

-- 부서번호 30,90을 포함한 작업들을 유일한 포맷으로 조회한다.
SELECT  EMPLOYEE_ID, LAST_NAME,DEPARTMENT_NAME, D.DEPARTMENT_ID  FROM    EMPLOYEES E,DEPARTMENTS D  WHERE   E.DEPARTMENT_ID = D.DEPARTMENT_ID and D.DEPARTMENT_ID in (30,90) order by JOB_ID ;








