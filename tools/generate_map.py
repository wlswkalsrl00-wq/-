#!/usr/bin/env python3
"""점프맵(Obby) 구조물을 Rojo 모델 파일(map/Obby.model.json)로 생성한다.

사용법: python3 tools/generate_map.py
좌표 단위는 스터드. 코스는 +Z 방향으로 진행한다.
캐릭터 기본 점프: 높이 약 6.4, 수평 거리 약 8 스터드 → 간격은 6.5 이하로 유지.
"""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parent.parent / "map" / "Obby.model.json"
THICK = 1.5

GREEN = [0.36, 0.78, 0.40]
STONE = [0.45, 0.47, 0.52]
BLUE = [0.30, 0.55, 0.95]
PURPLE = [0.62, 0.42, 0.92]
TEAL = [0.20, 0.75, 0.72]
PINK = [0.95, 0.45, 0.70]
GOLD = [1.00, 0.80, 0.20]
LAVA = [1.00, 0.30, 0.05]
WHITE = [0.95, 0.95, 0.95]
DARK = [0.15, 0.16, 0.20]

folders = {}


def folder(name):
    if name not in folders:
        folders[name] = {"Name": name, "ClassName": "Folder", "Children": []}
    return folders[name]["Children"]


def part(name, size, pos, color, group, material="SmoothPlastic", cls="Part",
         tags=None, attrs=None, children=None, **props):
    p = {
        "Size": size,
        "CFrame": list(pos) + [1, 0, 0, 0, 1, 0, 0, 0, 1],
        "Anchored": True,
        "Color": color,
        "Material": material,
        "TopSurface": "Smooth",
        "BottomSurface": "Smooth",
    }
    p.update(props)
    if tags:
        p["Tags"] = tags
    if attrs:
        p["Attributes"] = attrs
    inst = {"Name": name, "ClassName": cls, "Properties": p}
    if children:
        inst["Children"] = children
    folder(group).append(inst)
    return inst


def num(v):
    return {"Float64": float(v)}


def vec(x, y, z):
    return {"Vector3": [float(x), float(y), float(z)]}


def label(text, color=WHITE):
    return {
        "Name": "SurfaceGui",
        "ClassName": "SurfaceGui",
        "Properties": {"Face": "Front", "CanvasSize": [800, 400]},
        "Children": [{
            "Name": "Label",
            "ClassName": "TextLabel",
            "Properties": {
                "Size": {"UDim2": [[1, 0], [1, 0]]},
                "BackgroundTransparency": 1,
                "Text": text,
                "TextScaled": True,
                "TextColor3": color,
                "Font": "GothamBold",
            },
        }],
    }


class Course:
    """x: 중심선, y: 현재 발판 윗면 높이, z: 마지막 발판의 앞쪽 끝."""

    def __init__(self):
        self.x, self.y, self.z = 0.0, 11.0, 12.0
        self.stage = 0
        self.n = 0

    def plat(self, length, width=8, gap=5, dy=0, dx=0, color=GREEN,
             group="Platforms", name="Platform", **kw):
        self.x += dx
        self.y += dy
        near = self.z + gap
        self.n += 1
        inst = part(f"{name}{self.n}", [width, THICK, length],
                    [self.x, self.y - THICK / 2, near + length / 2],
                    color, group, **kw)
        self.z = near + length
        return inst

    def checkpoint(self, title, color, gap=5, dy=0, dx=0, finish=False):
        self.stage += 1
        self.plat(16, 16, gap, dy, dx, color=STONE, name="CheckpointBase")
        cz = self.z - 8
        tags = ["Checkpoint"] + (["Finish"] if finish else [])
        part(f"Checkpoint{self.stage}", [10, 0.4, 10], [self.x, self.y + 0.2, cz],
             GOLD if finish else color, "Checkpoints", material="Neon",
             tags=tags, attrs={"Stage": num(self.stage)})
        # 안내판: 플레이어가 다가오는 방향(-Z)을 향한다.
        for sx in (-3, 3):
            part("SignPost", [0.6, 7, 0.6], [self.x + 12 + sx, self.y + 3.5, cz],
                 DARK, "Signs")
        part(f"Sign{self.stage}", [9, 4, 0.5], [self.x + 12, self.y + 8, cz],
             DARK, "Signs", children=[label(title, color)])
        part("SignBase", [8, THICK, 4], [self.x + 12, self.y - THICK / 2, cz],
             STONE, "Signs")


c = Course()

# ── 시작 지점 ────────────────────────────────────────────────
part("StartBase", [24, 2, 24], [0, 10, 0], STONE, "Platforms")
part("SpawnLocation", [8, 1, 8], [0, 11.5, -4], WHITE, "Spawn", cls="SpawnLocation",
     material="Neon", Duration=0)
part("StartSign", [14, 5, 0.5], [0, 20, 11.5], DARK, "Signs",
     children=[label("점프맵 시작!  →  앞으로", GOLD)])
for sx in (-6, 6):
    part("SignPost", [0.6, 6.5, 0.6], [sx, 14.25, 11.5], DARK, "Signs")

# ── 1단계: 기본 점프 ─────────────────────────────────────────
for length, width, gap, dx in [(8, 8, 4, 0), (7, 8, 4, 0), (6, 7, 5, 3), (6, 7, 5, -3),
                               (5, 6, 5.5, -3), (5, 6, 5, 3), (5, 5, 6, 3), (5, 5, 6, -3)]:
    c.plat(length, width, gap, dx=dx, color=GREEN)
c.checkpoint("STAGE 2\n용암 징검다리", LAVA)

# ── 2단계: 용암 바닥 + 징검다리 + 외나무다리 ───────────────
lava_len = 62
part("LavaFloor", [14, 1, lava_len], [c.x, c.y - 1.5, c.z + 3 + lava_len / 2], LAVA,
     "KillBricks", material="Neon", tags=["KillBrick"])
c.z += 3
for i, dx in enumerate([0, -3, 3, 3, -3, -3, 3, 0]):
    c.x += dx if i else 0
    c.n += 1
    part(f"Stone{c.n}", [4, 2, 4], [c.x, c.y - 1, c.z + 2 + 2], STONE, "Platforms",
         material="Slate")
    c.z += 2 + 4 + 1.5
c.z = c.z - 1.5
# 용암 끝까지 걸친 뒤 외나무다리
c.plat(6, 8, 4.5, color=STONE)
c.plat(22, 1.6, 0, color=WHITE, name="Beam")
c.plat(5, 6, 0, color=STONE)
c.plat(22, 1.4, 0, color=WHITE, name="Beam")
c.checkpoint("STAGE 3\n하늘 계단", BLUE, gap=0)

# ── 3단계: 올라가는 발판 + 사다리 ───────────────────────────
for i in range(10):
    c.plat(5, 5, 4, dy=3, dx=4 if i % 2 == 0 else -4, color=BLUE)
c.plat(10, 10, 4, dx=0, color=BLUE)
truss_h = 18
part("Ladder", [2, truss_h, 2], [c.x, c.y + truss_h / 2, c.z - 1], GOLD, "Platforms",
     cls="TrussPart", material="Metal")
c.plat(10, 10, 0, dy=truss_h, color=BLUE)
c.checkpoint("STAGE 4\n움직이는 발판", PURPLE)

# ── 4단계: 움직이는 발판 ─────────────────────────────────────
c.plat(6, 8, 5, color=PURPLE)
# (A) 앞뒤로 움직이는 발판
part("MoverA", [6, 1, 6], [c.x, c.y - 0.5, c.z + 2 + 3], WHITE, "Movers", material="Neon",
     tags=["Mover"], attrs={"MoveOffset": vec(0, 0, 14), "Period": num(6)})
c.z += 24
c.plat(8, 8, 0, color=PURPLE)
# (B) 좌우로 움직이는 발판: 왼쪽에서 타고 오른쪽에서 내린다
c.x -= 8
c.plat(6, 6, 4, color=PURPLE)
part("MoverB", [6, 1, 6], [c.x, c.y - 0.5, c.z + 4 + 3], WHITE, "Movers", material="Neon",
     tags=["Mover"], attrs={"MoveOffset": vec(16, 0, 0), "Period": num(5)})
c.z += 4 + 6
c.x += 16
c.plat(6, 6, 4, color=PURPLE)
# (C) 엘리베이터
part("MoverC", [6, 1, 6], [c.x, c.y - 0.5, c.z + 3 + 3], WHITE, "Movers", material="Neon",
     tags=["Mover"], attrs={"MoveOffset": vec(0, 14, 0), "Period": num(7)})
c.z += 3 + 6
c.plat(8, 8, 3, dy=14, color=PURPLE)
# (D) 연속 두 개 (서로 반대 박자)
for i in range(2):
    part(f"MoverD{i + 1}", [5, 1, 5], [c.x - 6, c.y - 0.5, c.z + 4 + 2.5], WHITE, "Movers",
         material="Neon", tags=["Mover"],
         attrs={"MoveOffset": vec(12, 0, 0), "Period": num(4.5), "Phase": num(i * 3.14159)})
    c.z += 4 + 5
c.checkpoint("STAGE 5\n회전 막대", TEAL, gap=4, dx=-8)

# ── 5단계: 회전 막대 + 사라지는 발판 ─────────────────────────
walk_len = 66
c.plat(walk_len, 10, 4, color=TEAL)
start = c.z - walk_len
for i, speed in enumerate([1.4, -1.9, 2.4]):
    sz = start + 13 + i * 20
    part("SpinnerHub", [2, 3, 2], [c.x, c.y + 1.5, sz], DARK, "Platforms", material="Metal")
    part(f"Spinner{i + 1}", [20, 1.2, 1.2], [c.x, c.y + 1.3, sz], LAVA, "Spinners",
         material="Neon", tags=["Spinner", "KillBrick"], attrs={"SpinSpeed": num(speed)})
for i in range(7):
    c.plat(5, 5, 4, dx=[3, -3, -3, 3, 3, -3, 0][i], color=WHITE, group="Vanishing",
           name="Vanish", material="Glass", tags=["Vanish"], Transparency=0.25)
c.checkpoint("STAGE 6\n마지막 관문", PINK)

# ── 6단계: 용암 띠 + 높이 뛰기 + 마지막 조합 ─────────────────
strip_len = 50
c.plat(strip_len, 8, 4, color=PINK)
start = c.z - strip_len
for i in range(5):
    part(f"LavaStrip{i + 1}", [8, 0.6, 3], [c.x, c.y + 0.3, start + 8 + i * 9], LAVA,
         "KillBricks", material="Neon", tags=["KillBrick"])
for i in range(6):
    c.plat(3.5, 3.5, 5, dy=2.5, dx=3 if i % 2 == 0 else -3, color=PINK)
c.plat(8, 8, 4, dx=0, color=PINK)
part("MoverE", [5, 1, 5], [c.x, c.y - 0.5, c.z + 2 + 2.5], WHITE, "Movers", material="Neon",
     tags=["Mover"], attrs={"MoveOffset": vec(0, 0, 16), "Period": num(7)})
part("SpinnerHubFinal", [2, 10, 2], [c.x + 7, c.y - 3, c.z + 12.5], DARK, "Platforms",
     material="Metal")
part("SpinnerFinal", [22, 1.2, 1.2], [c.x + 7, c.y + 1.3, c.z + 12.5], LAVA, "Spinners",
     material="Neon", tags=["Spinner", "KillBrick"], attrs={"SpinSpeed": num(0.9)})
c.z += 2 + 5 + 16 + 2
c.checkpoint("완주! 축하합니다", GOLD, gap=0, finish=True)

# 완주 지점: 처음으로 돌아가는 발판
part("RestartPad", [5, 0.4, 5], [c.x - 9, c.y + 0.2, c.z + 4], WHITE, "Checkpoints",
     material="Neon", tags=["Restart"])
part("RestartBase", [8, THICK, 8], [c.x - 9, c.y - THICK / 2, c.z + 4], STONE, "Platforms")
part("RestartSign", [6, 2.5, 0.5], [c.x - 9, c.y + 5, c.z + 8], DARK, "Signs",
     children=[label("처음부터 다시", WHITE)])

# ── 낙사 처리용 용암 바다 ────────────────────────────────────
total = c.z + 60
part("LavaSea", [500, 2, total + 120], [0, -30, total / 2 - 30], LAVA, "KillBricks",
     material="CrackedLava", tags=["KillBrick"])

model = {"ClassName": "Folder", "Children": list(folders.values())}
OUT.write_text(json.dumps(model, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
count = sum(len(f["Children"]) for f in folders.values())
print(f"{OUT.name}: 파트 {count}개, 코스 길이 {c.z:.0f} 스터드, 최종 높이 {c.y:.1f}")
