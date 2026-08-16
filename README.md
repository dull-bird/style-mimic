# style-mimic

基于文体学（stylistics）与语料库语言学的文风模仿 skill：从样本提取可复用的**风格档案**（词汇/句法/修辞/语篇/立场五层，定量指标 + 质性描写），再按档案约束新写作，并用脚本量化校验成品与样本的偏差。

## 结构

- `SKILL.md` — skill 入口（触发条件、五步工作流、失败模式排查、伦理边界、练习分级）
- `references/style-dimensions.md` — 六层分析框架手册（词汇/句法/修辞/衔接语篇/立场介入/叙事声音 + 中文计量 + LLM 失败模式 + 偏差判据 + 文献出处）
- `references/profile-template.md` — 风格档案模板（Claim–Evidence 对 + 平均作者差分 + 体裁校准）
- `scripts/style_analyze.py` — 定量分析脚本（中英文，纯标准库，零依赖）：句长分布/句类/小句数/功能标记/MATTR/代词向量/句间重叠/标点指纹 + `--compare` 偏差对照（含方差塌缩报警）
- `scripts/style_review.py` — review 工具：`aiflavor` 测 AI 味（WP:AISIGNS 模式清单 + 方差塌缩，0–100 启发式评分，逐项可追溯）；`sim` 测双文本文风相似度（六层距离分解，≥85 同一声纹）
- `profiles/` — 已提取的风格档案（含 oakley-a-mind-for-numbers 示例）

## 快速开始

```bash
# 1. 定量分析样本
python3 scripts/style_analyze.py sample.txt

# 2. 按 references/style-dimensions.md 做质性阅读，填 references/profile-template.md
#    存为 profiles/<名称>.md

# 3. 按档案写作后，校验偏差
python3 scripts/style_analyze.py sample.txt draft.txt --compare
```

## 框架依据

Leech & Short (1981) 四层文体清单；Biber (1988) 形态句法特征集；Hyland (2005) stance & engagement 模型；Ure (1971) 词汇密度；Halliday & Hasan (1976) 衔接理论；连淑能 (1993) 形合/意合英汉对比；Brown et al. (2024, arXiv:2410.16107) 对该特征集区分写作风格有效性的近期验证。完整出处见 `references/style-dimensions.md` 参考文献节。

## 作为 agent skill 安装

把本目录软链或拷贝到 agent 的 skills 目录（如 `~/.agents/skills/style-mimic`）即可被 `style-mimic` 名称触发。
