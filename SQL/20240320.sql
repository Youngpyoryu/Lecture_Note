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