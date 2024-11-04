--���̺� �ۼ� ��(�����뿩�� ���̺�)
create table BookList(
    BookNum VARCHAR2(5) NOT NULL, --5 ���ڹ��ڿ�,
    --null���� �� �� ���� �ϴ� �������� �߰�
    title VARCHAR2(30) NOT NULL,
    makeyear number(4), --���ǳ⵵, ��������, 4����Ʈ�� �ƴϰ� 4�ڸ� ����
    inprice number(6), --�԰���
    outprice number(6), --�����
    
    CONSTRAINT booklist_pk primary key(BookNum) 
    --�߰� ���� ���� Booknum�� �⺻Ű�� ����
    --���̺��� �ܺο��� ������ ���� ������ booklist_pk�� ���� ����.
);

select * from BookList; --���̺��� ����� ��ȸ�ϴ� ���



--Ex02) ���̺� ���� ����
--�ʵ� : PersonNum, PersonName, Phone, Birth, Bpoint
CREATE TABLE person(
    PersonNum VARCHAR2(5) NOT NULL, --�ʵ巹���� ����(NOT NULL)
    PersonName VARCHAR2(12) NOT NULL, --�ʵ巹���� ����
    Phone VARCHAR2(13) NOT NULL, --�ʵ巹���� ����
    Birth DATE,
    enterDate DATE default sysdate,
    Bpoint NUMBER(6) default(0),
    
    CONSTRAINT person_pk PRIMARY KEY(PersonNum)
    -->���̺� ������ ����
);
select * from person;

create table in_out(
    out_date DATE NOT NULL, --�뿩��¥, ������ �⺻Ű
    indexk NUMBER(3) NOT NULL, --�뿩 ���� -������ �⺻Ű
    booknum VARCHAR2(5) NOT NULL, --�뿩������ȣ
    personnum VARCHAR2(5) NOT NULL, --ȸ����ȣ
    discount NUMBER(6), --���αݾ�
    CONSTRAINT in_out_pk PRIMARY KEY(out_date,indexk),
    --������ primary ���� ���� ��, �̵��� �����ؼ� ������ Ű�� ����.
    CONSTRAINT fk1 FOREIGN KEY (booknum) REFERENCES booklist(booknum),
    CONSTRAINT fk2 FOREIGN KEY (personnum) REFERENCES person(personnum)
);
--�����ʹ� ��ü ���Ἲ�� �����ϵ��� ������ �Ѵ�.
--booklist�� ���� ���� booknum�� �ü� ����.
--���� ���Ἲ--out_date, indexk �ΰ��� �ʵ带 �����ؼ� �⺻Ű�� ����.
--booknum�� in_out ���̺��� �ܷ�Ű(fk1)�μ� booklist���̺��� booknum ������.
--personnum in_out ���̺��� �ܷ�Ű(fk2)�μ� person ���̺��� personum�� ������.

-- �⺻Ű�� ���� ���Ἲ -> ��ü���Ἲ
-- �ܷ�Ű�� ���� ���Ἲ -> �������Ἲ

select * from in_out;









