#정보대학 학생회 홈페이지 오픈소스
======================

## 0. 버전 관리
-------------
### 개발 환경
* Django: 1.6.10
* Python: 2.7
### 서버 환경
* OS: Ubuntu 14.04 (LTS)
* Apache: 2.4.7

## 1. 설정 파일
-------------
* kuci/settings.py
** Django의 기본 설정 파일
** Database 설정 및 Secret key를 세팅해주어야한다.
* kuci/kuci_settings.py
** 학생회 홈페이지와 관련된 세팅
** 메일을 보내기 위해 gmail 계정 설정을 해주어야한다.
** SMS를 보내기 위해 coolsms 계정 설정을 해주어야한다.
