# 네오포지 모딩을 위한 파이썬 툴

현재 1.21.1 NeoForge와 완벽하게 호환됩니다.
패키지 내부 파일을 수정해서 네오포지 버전과 자바 버전 그리고 마크 버전을 수정할 수 있습니다.

## 작동 원리

파이썬 파일을 패키징해서 JSON 파일 생성후 그 JSON 파일을 자바로 해석해서 모드를 만들어 주는 것 입니다.

## 유저 사용법

먼저 pip를 이용해 pyneoforge 패키지를 다운로드 합니다.

```powershell
pip install pyneoforge
```

그 후 모드를 만들 폴더를 생성후 그곳에서 코딩을 합니다. (예제는 후술)

그리고 나서 init을 이용해 폴더 구조를 초기화 시켜줍니다.

```powershell
pyneoforge init 모드명 --from 코드/위치/파일명.py --mod-id 모드_네임스페이스 --mod-name "모드 이름"
```

만일 파일명.py가 위치해있는 폴더에 textures 폴더가 있다면 내부의 있는 파일까지 같이 가져가서 초기화 해줍니다. 없다면 새로 생성해줍니다.

코딩 완료 후 만들어진 폴더에 들어가서

```powershell
pyneoforge package
```

이 명령어를 입력하면 알아서 빌드까지 해줍니다.

## 코드 예제

```py
from pyneoforge import block, config, creative_tab, item, shaped_recipe, pickaxe, axe, shovel, hoe, sword, food, custom_tier

config(mod_version=1211)

item(
    "white_item",
    display_name="White Piece",
    max_stack_size=64,
    texture_file="textures/white_piece.png",
)

block(
    "white_block",
    display_name="White Block",
    hardness=3.0,
    max_stack_size=64,
    texture_file="textures/white_block.png",
)

custom_tier(
    "white_tier",
    durability=1250,
    mining_speed=8.5,
    attack_damage_bonus=3.0,
    enchantment_value=20,
    repair_ingredient="white_item",
    base_tier="diamond",
)

sword(
    "white_sword",
    display_name="White Sword",
    tier="white_tier",
    attack_damage=7.0,
    attack_speed=2.0,
    texture_file="textures/white_sword.png",
)

shovel(
    "white_shovel",
    display_name="White Shovel",
    tier="white_tier",
    attack_damage=5.0,
    attack_speed=1.0,
    texture_file="textures/white_shovel.png",
)

pickaxe(
    "white_pickaxe",
    display_name="White Pickaxe",
    tier="white_tier",
    attack_damage=5.0,
    attack_speed=1.2,
    texture_file="textures/white_pickaxe.png",
)

axe(
    "white_axe",
    display_name="White Axe",
    tier="white_tier",
    attack_damage=9.0,
    attack_speed=0.9,
    texture_file="textures/white_axe.png",
)

hoe(
    "white_hoe",
    display_name="White Hoe",
    tier="white_tier",
    attack_damage=1.0,
    attack_speed=3.0,
    texture_file="textures/white_hoe.png",
)

food(
    "white_food",
    display_name="White Food",
    nutrition=6,
    saturation=7.2,
    texture_file="textures/white_food.png",
)

creative_tab(
    "main_tab",
    display_name="WhiteCraft",
    icon="white_item",
    entries=["white_item", "white_block", "white_sword", "white_shovel", "white_pickaxe", "white_axe", "white_hoe", "white_food"],
)

shaped_recipe(
    "white_block",
    result="white_block",
    pattern=["###", "###", "###"],
    key={"#": "white_item"},
)

shaped_recipe(
    "white_sword",
    result="white_sword",
    pattern=[" # ", " # ", " | "],
    key={"#": "white_item", "|": "minecraft:stick"},
)

shaped_recipe(
    "white_shovel",
    result="white_shovel",
    pattern=[" # ", " | ", " | "],
    key={"#": "white_item", "|": "minecraft:stick"},
)

shaped_recipe(
    "white_pickaxe",
    result="white_pickaxe",
    pattern=["###", " | ", " | "],
    key={"#": "white_item", "|": "minecraft:stick"},
)

shaped_recipe(
    "white_axe",
    result="white_axe",
    pattern=["## ", "## ", " | "],
    key={"#": "white_item", "|": "minecraft:stick"},
)

shaped_recipe(
    "white_hoe",
    result="white_hoe",
    pattern=["## ", " | ", " | "],
    key={"#": "white_item", "|": "minecraft:stick"},
)

shaped_recipe(
    "white_food",
    result="white_food",
    pattern=["   ", " # ", "   "],
    key={"#": "white_item"},
)
```

## 구동시 필요한 환경

- Java 21
- NeoForge 1.21.1
- Python 3.10+
- Gradle이 `PATH`에 등록되어 있을 것

기본적으로 Gradle 프로젝트는 이 경로를 사용합니다.

```properties
org.gradle.java.home=C:/Program Files/Java/jdk-21
neo_version=21.1.200
```

하지만 패키징을 할때 `--java-home`과 `--neo-version`을 이용하여 경로를 바꿀수도 있습니다.

## 개발자용 섹션

```powershell
pip install pyneoforge -e
```

이 명령줄을 이용하여 수정 가능한 버전으로 설치 가능합니다.