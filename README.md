# 정보대학 학생회 홈페이지 오픈소스

### 주소: [https://kuci.korea.ac.kr](https://kuci.korea.ac.kr)

## 0. 버전 정보
### 개발 환경
* Django: 1.6.10
* Python: 2.7

### 서버 환경
* OS: Ubuntu 14.04 (LTS)
* Apache: 2.4.7

## 1. 설정 파일
* kuci/settings.py

>Django의 기본 설정 파일 <br>
Database 설정 및 Secret key를 세팅해주어야한다.

* kuci/kuci_settings.py

> 학생회 홈페이지와 관련된 세팅<br>
메일을 보내기 위해 gmail 계정 설정을 해주어야한다.<br>
SMS를 보내기 위해 coolsms 계정 설정을 해주어야한다.

## 2. 기타 설정
* 이미지 업로드 크기 제한: 500KB (board/views.py)
* 파일 업로드 크기 제한: 5MB (board/views.py)
* 강의실 대관 가능 기간: 2015-03-02 ~ 2015-06-19 (rent/views.py)