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



