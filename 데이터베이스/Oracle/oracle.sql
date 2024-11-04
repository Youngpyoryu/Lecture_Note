--테이블 작성 예(도서대여점 테이블)
create table BookList(
    BookNum VARCHAR2(5) NOT NULL, --5 글자문자열,
    --null값이 될 수 없게 하는 제약조건 추가
    title VARCHAR2(30) NOT NULL,
    makeyear number(4), --출판년도, 숫자형식, 4바이트가 아니고 4자리 숫자
    inprice number(6), --입고가격
    outprice number(6), --출고가격
    
    CONSTRAINT booklist_pk primary key(BookNum) 
    --추가 제약 조건 Booknum을 기본키로 설정
    --테이블의 외부에서 현재의 제약 조건을 booklist_pk로 접근 가능.
);

select * from BookList; --테이블의 명령을 조회하는 명령



--Ex02) 테이블 생성 예제
--필드 : PersonNum, PersonName, Phone, Birth, Bpoint
CREATE TABLE person(
    PersonNum VARCHAR2(5) NOT NULL, --필드레벨로 설정(NOT NULL)
    PersonName VARCHAR2(12) NOT NULL, --필드레벨로 설정
    Phone VARCHAR2(13) NOT NULL, --필드레벨로 설정
    Birth DATE,
    enterDate DATE default sysdate,
    Bpoint NUMBER(6) default(0),
    
    CONSTRAINT person_pk PRIMARY KEY(PersonNum)
    -->테이블 레벨로 설정
);
select * from person;

create table in_out(
    out_date DATE NOT NULL, --대여날짜, 조합한 기본키
    indexk NUMBER(3) NOT NULL, --대여 순번 -조합한 기본키
    booknum VARCHAR2(5) NOT NULL, --대여도서번호
    personnum VARCHAR2(5) NOT NULL, --회원번호
    discount NUMBER(6), --할인금액
    CONSTRAINT in_out_pk PRIMARY KEY(out_date,indexk),
    --마땅한 primary 값이 없을 때, 이둘을 조합해서 고유한 키를 만듦.
    CONSTRAINT fk1 FOREIGN KEY (booknum) REFERENCES booklist(booknum),
    CONSTRAINT fk2 FOREIGN KEY (personnum) REFERENCES person(personnum)
);
--데이터는 객체 무결성을 유지하도록 만들어야 한다.
--booklist에 없는 값이 booknum에 올수 없다.
--참조 무결성--out_date, indexk 두개의 필드를 조합해서 기본키를 만듦.
--booknum는 in_out 테이블의 외래키(fk1)로서 booklist테이블의 booknum 참조함.
--personnum in_out 테이블의 외래키(fk2)로서 person 테이블의 personum을 참조함.

-- 기본키에 대한 무결성 -> 개체무결성
-- 외래키에 대한 무결성 -> 참조무결성

select * from in_out;









