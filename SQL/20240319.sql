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
--select LAST_NAME, salary 
--    from employees 
--    where salary>=12000;

-- ������ 12000 �̻�Ǵ� �������� ID(DEPARTMENT_ID) LAST_NAME�� ����ϼ���.
--select LAST_NAME, DEPARTMENT_ID 
--from employees 
--where salary>=12000;

-- ������ 5000 ���� 12000�� ���� �̿��� ������� LAST_NAME �� ������ ��ȸ�Ѵ�.
select LAST_NAME, salary 
from employees 
where 	salary<=5000
or		salary>=12000;


