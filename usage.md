# 1. 画幅合成自检
python services/scroll_composer.py
# 预期：output/tmp/ 下生成 5 张测试图（立轴/横卷/屏风/团扇/册页）

# 2. 安全检查自检
python core/safety.py
# 预期：8 个测试用例全部通过

# 3. 交互式模式
python main.py
# 按提示选择：主题 → 预设 → 引擎 → 画幅 → 装裱 → 种子

# 4. 快速模式（一行命令）
python main.py --preset dunhuang --engine pollinations --composition horizontal --seed 2026
# 预期：output/tang/dunhuang_*.png，带横卷装裱

# 5. 全流程合成（含装裱）
## 出图
python compose_artwork.py --preset tengu --engine pollinations

## 装裱
python -c "from services.scroll_composer import ScrollComposer;from PIL import Image;from pathlib import Path;p=sorted(Path('output/yokai').glob('tengu_*.png'))[-1];img=Image.open(p);r=ScrollComposer(seed=42).compose(img,'vertical');r.save('output/yokai/tengu_mounted.png');print('装裱完成:',r.size)"

## 一键跑全部自检（用 && 串联）
python services/scroll_composer.py && python core/safety.py && python compose_artwork.py --preset tengu --engine pollinations && python main.py --preset dunhuang --engine pollinations --composition horizontal --seed 2026