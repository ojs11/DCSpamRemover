# DC Spam Remover

특정 ip 대역으로 무지성 도배가 오는경우 사용해 보세요.

나도 갤질하면서 이런게 필요할 줄 몰랐지...
아이피 대역 차단은 대체 어떻게 뚫는거냐고


## 사용법 - Python
```
git clone https://github.com/arwls1nzdw/DCSpamRemover
cd DCSpamRemover
pip install -r requirements.txt
copy config.ini.template config.ini
notepad config.ini
python main.py
```

## 사용법 - exe
```
main.exe 다운로드 후 실행
생성된 config.ini 수정 후 재실행
```

### Virus 감지되는데요?
[Refernce](https://nitratine.net/blog/post/issues-when-using-auto-py-to-exe/#my-antivirus-detected-the-exe-as-a-virus)

pyinstaller 오진이라고 합니다.

Virus 감지되는게 마음에 안들면 python 코드를 직접 돌리면 됨.


### Type of Post
작성자ㅏ 모든 유형을 다 알진 못하니, 필요하면 개발자 도구 켜서 확인할것

공지(icon_notice)는 항상 제외됨
```
1. icon_txt      : 일반글
2. icon_pic      : 이미지 첨부글
3. icon_movie    : 동영상 첨부글
4. icon_ai       : AI 이미지
5. icon_recomimg : 개념글
```


### For mobile
Kiwi 브라우저로 개발자 도구 사용 가능. 데스크탑 모드 키고 `mobile.js` 복붙해서 실행하면 됨