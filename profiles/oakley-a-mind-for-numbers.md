# 风格档案：Barbara Oakley《A Mind for Numbers》

> 样本：`a-mind-for-numbers.epub` 第 1、2、4、10、15 章正文（约 1.9 万词，含叙事章与教学章）；语言：en；建档日期：2026-08-15
> 定量数据由 `scripts/style_analyze.py` 生成；质性条目附原文例句。
> **应用注意**：档案源为英文，目标是中文写作——按连淑能（1993）形合/意合原则做"风格转译"：保留节奏、人称、修辞策略，把英文长从句转译为中文流水短句，不生搬句法。

## 0. 一句话风格画像

用真人真事开场，拿日常物品当比喻的锚，全程直呼"你"，不断提问和发小任务，把神经科学讲得像朋友聊天。

## 1. 词汇层

- TTR 0.20–0.24（长章节），均词长 4.5–4.8；语域：**口语底色 + 术语即释**——专业名词出现必配大白话重述（"Einstellung"先给德文词再立刻解释"stuck in one way of looking at a problem"）。
- 高频实词：memory, working, your, learn, think, brain, problem, time, people, little。
- 动词偏好具体动作与身体感（stretches, reaches, fire and wire, cementing），不用抽象学术动词。
- 例句："Your neurons fire and wire together in a shimmering mental loop, cementing the relationship in your mind…"

## 2. 句法层

- 句长：均值 22–24 词，中位 18–21，**标准差 15（节奏大开大合）**，p10–p90 = 7–43 词。长短剧烈交替：长句铺陈后常接一个 2–5 词的短句或碎片句点睛。
- 签名句式——**碎片句收尾**："Perfect. Indelible." / "More tentacle connections." / "Yum!"
- 每句小句数 1.9–2.3（英文中等复杂度）；转译为中文时以 10–25 字短句为主、偶发 40 字以上长句。
- 句类：疑问句约 5%（每章 5–16 个），感叹句零星；祈使/指令句集中在"现在轮到你了"类练习框。
- 句首常甩出短场景再进正题（"Are you focusing on a shape? If so, …"）。

## 3. 修辞层

- **比喻是引擎**：明喻/类比标记 3–4.5/千词。喻体一律来自日常物品与身体经验：attentional octopus（注意力章鱼）、pinball machine（弹珠机）、brick wall（砌墙）、zombies（僵尸）、frying pan（爱迪生的煎锅）。同一比喻全章回收复用、层层加码，不中途换喻体。
- 设问推进：段落开头抛问题勾着读者走（"Wouldn't you love to have the gift of such a memory?""What happens when you focus your attention?"）。
- 举例模式：例子先行、观点殿后——先讲完整个故事再点题。
- 例句："When you turn your attention to something, your attentional octopus stretches its neural tentacles to connect different parts of the brain."

## 4. 衔接与语篇层

- 连接词谱系（每千词）：增补 20–28（and/also 为主）、转折 5–8、因果 3.5–5.5、时序 1.5–6。偏爱口语连接：But / So / Actually / In other words / Let's say。
- **章节开头=人物轶事**（Shereshevsky 的超强记忆、Foer 的忘性），中段概念讲解，结尾回收轶事或给行动清单。
- 段落短：35 段/2400 词左右，平均 60–70 词一段，主题句多在段首。
- 术语首次出现前必有日常经验铺垫（先问你"有没有过这种经历"，再给名词）。

## 5. 立场与介入层

- hedges（4–9/千词）> boosters（2–3/千词）：讲科学结论留余地，讲方法效果给肯定。
- self-mention：教学章 4–18/千词，叙事章高达 70+/千词——她常讲自己的失败史（数学不及格、从军、学俄语）。
- **读者代词 40–49/千词（极高）**：全程"你"，指令式 4–12/千词（"Let's say""Imagine""Try this"）。
- 幽默与自嘲：给读者起昵称式调侃、承认自己的糗事；情绪词直接（irritating, love, Yum）。

## 6. 写作硬约束（中文化执行版）

1. 每讲/每节开头用一个具体的人或场景开场，禁止用"本节讲……"式抽象开场。
2. 句长以 10–25 字为主，允许偶发 40+ 字长句；每 3–5 句安排一个 ≤8 字的短句/碎片句点睛。
3. 每个核心概念配一个日常物品/身体经验的比喻，全讲只用一个喻体并回收加码；比喻标记（就像/好比/可以想象成）约 3–4 次/千字。
4. 每 200–300 字至少一次直接与读者对话：提问（"你是不是也……？"）、指令（"试着……"）或"我们/你"叙述。
5. 术语首次出现：先日常经验一句，再给术语，再用大白话重述一遍。
6. 连接词用口语级：但是/所以/其实/换句话说/比如说；禁用"综上所述""由此可见""首先其次再次"的八股链。
7. 段落 ≤ 5 行，主题句在段首。
8. 语气：hedge 多于 booster——结论说"通常/往往"，方法说"试试看"。

## 7. 校验记录

- 待应用于讲义后回填 `--compare` 偏差与人工核对结果。
