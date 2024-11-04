--select * from employees;

--DESC employees -- �ڷ���

-- employess�� ���� first name, last name, salary ����غ���!
--select first_name, last_name, salary from employees;

-- JOB_ID�� ������!
--select JOB_ID from employees; -- �ߺ��� �����Ƿ� ���Ⱑ ����.

-- �ߺ� ����
--select distinct JOB_ID from employees;

-- ���ڿ����� ���ϱ�('||' ��ȣ ���)
-- employees���� first name�� last name�� ���ڿ��� ���ϰ� salary�� �Բ� ����غ���!
--select first_name || ' ' || last_name, salary from employees;
--select first_name || last_name, salary from employees;
-- ' '�� ���� ������ ���ڵ��� �پ ����� ��.

--�����Լ�
-- �������� �޴� ���� �� ���� ���� ���� ���ϱ�!(max)
--select max(salary) from employees;

-- ������ �߿� ���� �ֱٿ� �Ի�(hire_date)�� ��¥ ���ϱ�(max)
--select max(hire_date) from employess;

-- �������� �޴� ���� �� ���� ���� ���� ���ϱ�!
--select min(salary) from employees;

-- ������ �� ���� ���� �Ի��� ��¥ ���ϱ�!!!
--select min(hire_date) from employees;

-- ��ü ���� �� ���ϱ�(count)
--select count(*) from employees;

-- ���� �޿��� ����Ǵ� �� �ݾ��� ���ϱ�
--select sum(salary) from employees;

-- �������� ��� ���� ���ϱ�
--select avg(salary) from employees; 

-- �������� ��� ���� ���ϱ�(�Ҽ��� ���� �ڸ��� ������)
--select floor(avg(salary)) from employees;

-- ������ 12000 �̻�Ǵ� �������� LAST_NAME �� ������ ��ȸ�Ѵ�.
--select LAST_NAME, salary from employees where salary>=12000;

-- ������ 12000 �̻�Ǵ� �������� ID(DEPARTMENT_ID) LAST_NAME�� ����ϼ���.
--select LAST_NAME, DEPARTMENT_ID from employees where salary>=12000;

-- ������ 5000 ���� 12000�� ���� �̿��� ������� LAST_NAME �� ������ ��ȸ�Ѵ�.
--select LAST_NAME, salary from employees where salary<=5000 or salary>=12000;
--select HIRE_DATE from employees;
-- 05/MAR/20�Ϻ��� 08/AUG/01 ���̿� ���� ������� LAST_NAME ���(EMPLOYEE_ID), �������(HIRE_Date)�� ��ȸ�Ѵ�.
--select LAST_NAME, EMPLOYEE_ID, HIRE_DATE from employeeswhere HIRE_DATE >='20-MAR-05'and   HIRE_DATE <='01-AUG-08';
-- ������� ������ �����Ѵ�.
--select LAST_NAME, EMPLOYEE_ID, HIRE_DATE from employees where HIRE_DATE between TO_DATE('20-MAR-05') and TO_DATE('01-AUG-08') ORDER BY HIRE_DATE;

-- 20�� �� 50�� �μ����� �ٹ��ϴ� ������� LAST_NAME �� �μ� ��ȣ(DEPARTMENT_ID)�� ���ĺ������� ��ȸ�Ѵ�.
--select LAST_NAME, DEPARTMENT_ID from employees where DEPARTMENT_ID in (20,50) order by LAST_NAME ASC; --DESC

-- 2005�⿡ ���� ��� ������� LAST_NAME �� ����� ��ȸ�Ѵ�.
--select LAST_NAME, HIRE_DATE from employeeswhere to_char(HIRE_DATE, 'yyyy') = '2008';

--���丵�� o�� ����� �̸��� ã�� �� ���� ��ɾ�
--select last_name from employees where last_name like '_o%';

-- �̸��� ù ���縵�� A�̰� �ι�° ���縵�� ���� �𸣰ڰ�, ����° ���縵�� o�� ����� �˻��غ���.
--select last_name from employees where last_name like 'A_o%';

-- �Ŵ���(MANAGER_ID)�� ���� ������� LAST_NAME �� JOB_ID�� ��ȸ�Ѵ�.
--select LAST_NAME, JOB_ID, MANAGER_ID from employees where MANAGER_ID is null OR MANAGER_ID  = '';
-- �Ŵ���(MANAGER_ID)�� �ִ� ������� LAST_NAME �� JOB_ID�� ��ȸ�Ѵ�.
--select LAST_NAME, JOB_ID, MANAGER_ID from employees where MANAGER_ID is not null OR MANAGER_ID  != '';

--Ŀ�̼�(COMMISSION_PCT)�� ���� ��� ������� LAST_NAME, ���� �� Ŀ�̼��� ��ȸ��.
-- ���� ����, Ŀ�̼� �������� �����غ���.
-- select LAST_NAME, SALARY, COMMISSION_PCT from employees where NOT(COMMISSION_PCT is null) ORDER BY SALARY DESC, COMMISSION_PCT DESC;

-- LAST_NAME�� �׹�° ���ڰ� a�� ������� LAST_NAME�� ��ȸ�Ѵ�.
--select LAST_NAME from employees where LAST_NAME like '___a%';

-- LAST_NAME�� a�� (OR) e ���ڰ� �ִ� ������� LAST_NAME�� ��ȸ�Ѵ�.
--select LAST_NAME from employees where LAST_NAME LIKE '%a%' or    LAST_NAME LIKE '%e%';

-- ������ 2500, 3500, 7000�� �ƴϸ�, ������ SA_REP�̳� ST_CLERK�� ������� ��ȸ�Ѵ�.
--SELECT LAST_NAME, JOB_ID, SALARY  from employees where salary NOT in (2500,3500,7000) and JOB_ID in ('SA_REP','ST_CLERK');

-- �۾��� AD_PRESS�� ����� A����� , ST_MAN�� ����� B���, IT_PROG�� ����� C�����, SA_REP�� �����
-- D�����, ST_CLERK�� ����� E����� ��Ÿ�� 0�� �ο��Ͽ� ��ȸ
-- DECODE : SQL���� �����͸� ���ϰ� ���ǿ� ���� �ٸ� ���� ��ȯ�ϴ� �Լ�.
--select *
--from (
--   select EMPLOYEE_ID, --��������
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

-- ��� ������� LAST_NAME, �μ� �̸� �� �μ� ��ȣ ��ȸ�Ѵ�.
--SELECT  EMPLOYEE_ID, LAST_NAME,DEPARTMENT_NAME, D.DEPARTMENT_ID FROM    EMPLOYEES E,DEPARTMENTS D WHERE   E.DEPARTMENT_ID = D.DEPARTMENT_ID;

-- �μ���ȣ 30,90�� ������ �۾����� ������ �������� ��ȸ�Ѵ�.
SELECT  EMPLOYEE_ID, LAST_NAME,DEPARTMENT_NAME, D.DEPARTMENT_ID  FROM    EMPLOYEES E,DEPARTMENTS D  WHERE   E.DEPARTMENT_ID = D.DEPARTMENT_ID and D.DEPARTMENT_ID in (30,90) order by JOB_ID ;








