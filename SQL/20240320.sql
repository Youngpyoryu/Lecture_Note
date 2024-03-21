--desc employees;
--EMPLOYEE_ID�� �����ȣ ����Ǿ� ����. PK
--HIRE_DATE�� �Ի��� ��¥.
--JOB_ID�� ���� �����ϰ� �ִ� ����
--SALARY�� ����� �ް� �ִ� �� �޿�,
--COMMISSION_PCT�� ���ʽ� ���� ����Ǿ� ����. / ���ʽ��� ���� �ʴ� ������� ��� NULL ->�� ����
--MANAGER_ID�� �� ����� �����ϰ� �ִ� ������(���)�� ��� ��ȣ�� ����Ǿ� ����.
--DEPARTMENT_ID�� ����� �ٹ��ϰ� �ִ� �μ� ��ȣ�̰�, �� �÷��� employees ���̺��� FK

--desc departments;
--DEPARTMENT_ID�� �μ��� ��ȣ�� �� �÷��� departments ���̺��� Primiary key(PK)�̴�.
--DEPARTMENT_NAME�� �μ��� �̸��� ����Ǿ� ����.
--MANAGER_ID���� �μ��� �����ϴ� ������, ��, �μ����� ��� ��ȣ�� ����Ǿ� ����.
--LOCATION_ID���� �μ��� ��ġ�� ������ ������ȣ�� ����Ǿ� ����. / departments�� foregien key(FK)�̴�.


--desc locations
--LOCATION_ID�� �μ��� ��ġ�� ������ ���� ��ȣ�� ����Ǿ� ����. locations ���̺��� PK�̴�.
--STREET_ADDRESS�� �ּ�, ���� ������� ������ �� �ܿ��� ��.
--POSTAL_CODE�� �����ȣ / ���� ������ ����.
-- CITY�� �μ��� ��ġ�� �����̸�.
-- STATE_PROVINCE�� COUNTRY_ID�� ��������� ����.

--��� ������� LAST_NAME, �μ���, ���� ID �� ���� ���� ��ȸ�Ѵ�.
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY from employees E,departments D, Locations L where E.Department_ID = D.department_ID and D.location_ID = L.location_ID;
-- �þ�Ʋ�� ��� ����� ȣ��.
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY from employees E,departments D, Locations L where E.Department_ID = D.department_ID and D.location_ID = L.location_ID and L.city = 'Seattle';

-- �þ�Ʋ�� ��� ����� ȣ�� -> ���������� ȣ���غ�����!
--select LAST_NAME, DEPARTMENT_NAME, L.LOCATION_ID, CITY
--from employees E,departments D, Locations L
--where E.Department_ID = D.department_ID
--and D.location_ID = L.location_ID
--and L.location_ID = (
--    				 select LOCATION_ID
--    				 from LOCATIONS
--   				 where city = 'Seattle'
--);
-- PK�� ��ȸ�ϴ� ��.
-- LAST_NAME�� DAVIES�� ������� �Ŀ� ���� ������� LAST_NAME �� HIRE_DATE�� ��ȸ�غ���.
--SELECT  LAST_NAME,HIRE_DATE
--FROM    EMPLOYEES
--WHERE   HIRE_DATE >=  (
--                        SELECT  HIRE_DATE
--                        FROM    EMPLOYEES
--                        WHERE   LAST_NAME = 'Davies'
--                      )
--ORDER   BY HIRE_DATE
--;

-- ȸ�� ��ü�� �ִ� ����, �ּҿ���, ���� �� �� �� ��� ������ �ڿ���(Round)�� �����Ͽ� ��ȸ�Ѵ�.
--select max(salary), min(salary), sum(salary), round(avg(salary))
--from employees;

-- �� JOB_ID ��, �ִ� ����, �ּ� ����, ���� ���� �� ��� ������ �ڿ���(ROUND)�� �����Ͽ� ��ȸ�Ѵ�.
--select JOB_ID, MAX(salary) MAX, min(salary) MIN, sum(salary) SUM, round(avg(salary)) AVG
--from employees
--group by JOB_ID
--order by JOB_ID;

--group by : ������ ���� ���� �÷��� �������� �׷캰 ������ ������.
-- �׻� �׷��Լ��� �Բ� ����. 
--select department_id, round(avg(salary))
--from employees
--group by department_id;
-- group by : �׷� �Լ��� group by���� ������ �÷��� ���� �࿡ ���ؼ� ��� ������ ���.
-- group by�� Ȱ���Ͽ��� �÷�(�μ�)��(department_id)�� ��� ���� �׷� �Լ��� ����Ͽ���!
--select round(avg(salary))
--from employees
--group by department_id;

-- 2�� �̻��� �׷�ȭ
--select department_id �μ���ȣ, job_id ����, sum(salary)
--from employees
--group by department_id,job_id
--order by department_id;

--select department_id �μ���ȣ, job_id ����, manager_id ����ȣ, sum(salary)
--from employees
--group by department_id,job_id,manager_id
--order by department_id;
--having  : groupby���� ���� ������ ��� �� �� ���ϴ� ���ǿ� �����ϴ� �����͸� ������ ��.
--select department_id, round(avg(salary)) ��ձ޿�
--from employees
--group by department_id
--having avg(salary)<7000;

--select job_id, sum(salary) �޿��Ѿ�
--from employees
--where job_id not like '%PER%'
--group by job_id
--having sum(salary)>13000
--order by sum(salary);

-- �Ŵ����� ��� �� �� �Ŵ��� �� ����� �� �ּ� ������ �޴� ����� ������ ��ȸ��.
-- �Ŵ����� ���� ������� ����, �ּ� ������ 6000�̸��� ���� ����, ���� ���� �������� ��ȸ
--select MANAGER_ID, MIN(SALARY)
--from employees
--where MANAGER_ID is not null
--group by MANAGER_ID
--having MIN(SALRY) >=6000 
--order by MIN(SALRY) Desc;

-- ȸ�� ��ü ��պ��� �� �޴� ������� ��� �� LAST_NAME�� ��ȸ�Ѵ�.
--select employee_id,LAST_NAME
--from employees
--where salary >= (
--    			select avg(salary)
--    			from employees);





