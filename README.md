# 로블록스 점프맵 (Obby)

6단계 점프맵입니다. `obby.rbxlx` 파일을 Roblox Studio에서 열면 바로 플레이할 수 있습니다.

## 여는 방법

1. 이 저장소에서 `obby.rbxlx`를 내려받습니다.
2. Roblox Studio를 실행하고 **File → Open from File**로 파일을 엽니다.
3. 위쪽 **Play**(F5)를 눌러 테스트합니다.
4. 로블록스에 올리려면 **File → Publish to Roblox**를 누릅니다.

## 구성

| 단계 | 내용 |
| --- | --- |
| 1 | 기본 점프 발판 |
| 2 | 용암 바닥 징검다리, 외나무다리 |
| 3 | 올라가는 발판, 사다리 |
| 4 | 움직이는 발판(앞뒤, 좌우, 엘리베이터) |
| 5 | 회전 막대, 밟으면 사라지는 발판 |
| 6 | 용암 띠, 높이 뛰기, 움직이는 발판 + 회전 막대 |

- 금색·색깔 발판(체크포인트)을 밟으면 저장되고, 죽으면 그 자리에서 다시 시작합니다.
- 리더보드에 현재 단계(`Stage`)가 표시됩니다.
- 완주 지점의 흰 발판을 밟으면 처음부터 다시 시작합니다.

## 파일 구조

- `obby.rbxlx`: Studio에서 여는 완성 파일
- `tools/generate_map.py`: 발판 배치를 만드는 스크립트 (맵 구조는 여기서 수정)
- `map/Obby.model.json`: 위 스크립트가 만든 구조물 데이터
- `src/server/ObbyServer.server.luau`: 체크포인트, 사망 처리, 사라지는 발판
- `src/client/ObbyClient.client.luau`: 움직이는 발판, 회전 막대
- `default.project.json`: [Rojo](https://rojo.space) 프로젝트 설정

## 다시 빌드하기

```bash
python3 tools/generate_map.py
rojo build -o obby.rbxlx
```

## 외부 공개 맵

`third_party/christmas-obby/`에 다른 제작자가 MIT 라이선스로 공개한 200단계 점프맵이 들어 있습니다. 자세한 내용은 그 폴더의 README를 참고하세요.
