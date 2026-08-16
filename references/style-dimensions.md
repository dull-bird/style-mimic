# 文体分析维度（六层框架）

本文件是 style-mimic 的分析手册。框架综合文体学与语料库语言学的经典模型，每层给出：定义、观察清单、可量化指标（`scripts/style_analyze.py` 覆盖的标 ✓）、文献出处。

骨架是 Leech & Short (1981) 的四层清单（词汇 / 语法 / 修辞格 / 衔接与语境），补入 Hyland (2005) 的人际层（立场与介入）作第 5 层，再加叙事声音作第 6 层（2024–2026 文献调研后新增，叙事文本必需）。教学文体的核心恰在第五层"作者如何跟读者说话"。

---

## 第 1 层：词汇（Lexical）

**观察什么**

- 词汇丰富度：TTR（type-token ratio）✓。注意 TTR 随文本变长而下降，比较时要求样本长度相近；跨长度比较只作粗参考（Lu 2012 的批评）。
- 词汇密度（lexical density）：实词占总词数比例（Ure 1971；Halliday 1985 按小句计）。书面体一般高于口语体；Halliday 报告的英语书面语典型值约每小句 3–6 个实词。
- 语域（register）层级：口语词 / 通用词 / 书面词 / 术语的比例。教材的关键签名：术语出现后是否立即用日常词重述（"工作记忆，也就是你脑子里那块黑板"）。
- 高频实词与特征词 ✓（top_content）：作者的"词汇指纹"——偏爱哪些动词、哪些口头禅。
- 平均词长（英文）✓：信息密度与正式度的经典代理（Biber 1988）。

**进档案的写法**：不只记"TTR 0.42"，要记"术语必配口语重述""动词偏具体动作类（撞、弹、砌）而非抽象类（实现、构建）"。

## 第 2 层：句法（Grammatical / Syntactic）

**观察什么**

- 句长：均值只是起点，**标准差和分布形状**才是节奏 ✓（均值/中位数/标准差/p05–p95/IQR/MAD/偏度/CV/分桶）。长句连绵 vs 长短相间 vs 短句连发，是三种完全不同的文体。
- 句法复杂度：每句小句数 ✓（中文以逗号/分号/冒号分断，顿号仅作枚举不计；英文以逗号/分号/冒号加从属标记近似）。这是形合/意合（hypotaxis/parataxis）的操作化近似：英语靠连接手段显性组句（形合），汉语靠语义并置（意合）——连淑能 (1993) 视之为英汉最本质的句法差异（Nida 1982 同此判断）。模仿英文作者的中文译本时尤其要决定：保留形合的长从句，还是拆成意合的流水句。
- 句类分布 ✓：陈述 / 疑问 / 感叹比例；祈使句密度（教学文体的直接指令："试着……""记住……"）。
- Biber (1988) 式特征（质性估计）：被动语态多少、名词化（nominalization，"……的实现/性/化"）多少、并列 vs 主从哪个占优。Brown et al. (2024) 证实这组特征足以稳定区分不同作者与文体的风格。
- 句首习惯：主语先行，还是状语/连接词先行（"事实上，……""换句话说，……"）。

## 第 3 层：修辞（Figures of Speech）

**观察什么**（脚本只覆盖标记计数 ✓，识别靠阅读）

- 比喻系统：明喻标记频率 ✓（就像/好比/仿佛/like/as if）。更重要的是**比喻取材的一贯领域**——Oakley 的比喻全部来自日常物品与游戏（弹珠机、砌墙、僵尸），学术作者则常取自学科内部。记录：喻体领域、比喻与抽象概念的距离、比喻是否回收复用。
- 类比（analogy）与隐喻是教材的第一修辞：每个核心概念是否都配一个？配在哪（引入时还是难点处）？
- 设问与反问 ✓（疑问句比例 + 质性判断）：是否用"你会怎么做呢？"推进叙述——教学文体的标志性手段。
- 排比与反复：三连结构、句首反复（anaphora）。中文教材尤其要查"整句 vs 散句"。
- 举例标记 ✓（例如/比如/for example）频率与位置：先观点后例子，还是例子引出观点。
- 对比、引用、拟人、夸张：出现即记录实例。

## 第 4 层：衔接与语篇（Cohesion & Discourse）

**观察什么**

- 连接词库存与频率 ✓，按 Halliday & Hasan (1976) 的功能分类：增补（而且/此外）、转折（但是/然而）、因果（因为/因此）、时序（首先/然后）。两个作者句长相同但连接词谱系不同，读感完全不同。
- 词汇衔接：关键词的复现率（同一概念反复点名 vs 换说法）✓ 部分（top_content）。
- 段落结构：平均段长、主题句位置（首/尾/无）、段落推进模式（观点→例→小结？问题→转折→解答？）。
- 章节级模式（教材特有）：开头是否先抛问题、结尾是否回收、小节之间是否埋钩子。
- 信息结构：是否严格"已知→新知"推进，新术语出现前是否必有铺垫。

## 第 5 层：立场与介入（Stance & Engagement）

依据 Hyland (2005) 的互动模型，这是"作者声音"最可测量的一层：

- **立场（stance，作者面向）**：hedges ✓（可能/或许/一般来说 vs may/perhaps）与 boosters ✓（一定/显然/事实上 vs certainly/indeed）的频率比——学术体 hedge 密集，通俗体 booster 偏多。self-mention ✓（我/我们/I/we）：作者是否现身讲故事。
- **介入（engagement，读者面向）**：读者代词 ✓（你/大家/you）、指令式 ✓（试着/记住/imagine/notice）、直接向读者提问（疑问句的一部分）、共享知识预设（"我们都知道……"）。
- 态度与情绪：幽默密度、轶事（anecdote）使用、评价性形容词（"惊人的""优雅的"）。

## 校验阶段的偏差判据

### 尾部与小样本门槛

`style_analyze.py` 对句长同时报告 p05/p95、四分位距 IQR、中位绝对偏差 MAD、偏度和变异系数 CV。p05/p95 在少于 20 句时标为不稳定；不要用一两句的标准差或 CV 给作者下结论。`style_review.py aiflavor` 只有在至少 8 句且句长至少有 4 个不同取值时才启用方差塌缩惩罚；`sim` 少于 5 句或 80 个单位时只输出线索分，不给“同一声纹”判语。这些是工程上的最小门槛，不是跨体裁普适常数。

`--compare` 输出的任何一项满足下列条件即视为漂移，需修正：

1. 句长均值偏差 > 20%，或标准差偏差 > 30%（节奏走形）；
2. 任一功能类标记频率比值 > 2 或 < 0.5（脚本已自动标 ⚠️）；
3. 句类比例明显倒置（样本 15% 疑问句，成品 0%）；
4. 质性条目逐条人工核对（比喻领域、段落模式、介入方式）——无法脚本化，不得跳过。

**簇判据（clusters, not isolated tells）**：单项轻微漂移不判失败；同一层三项以上漂移才判修正（借鉴 Wikipedia "Signs of AI writing" 的反误伤原则与 blader/humanizer 的误伤清单）。

**多信号集成**：单一指标与人工判断的相关性很差（Jangra et al. 2025，人评者间一致性：内容 0.78 > 风格 0.64 > 文字编辑 0.40——风格判断本身主观，100% 保真不是合理目标）。验收应组合三类异质信号：规则计数特征（本脚本，可追溯复算）+ LLM 判别（强制二选一提示，比自由回答有效 +34.5%）+ 人工抽查。LLM 生成的风格描述只作参考，不作判据（EMNLP 2025：LLM 自述的风格理由不代表其真实判断依据）。

## 声纹与体裁：两根独立的轴（Biber & Conrad 2009）

风格档案失效的最常见原因，是把**作者声纹**（voice/style，作者稳定的语言选择习惯）和**体裁约束**（register/genre，文本类型的功能要求）混为一谈：

- **声纹回答"这句话像不像他写的"**：句长节奏、比喻取材、人称介入、hedge/booster 配比——同一个人写书写信写推特，这些都稳定。
- **体裁回答"这个文本类型该有什么零件"**：讲义要有核心问题与自测，书章可以有页级轶事，论文要有文献综述——同一作者跨体裁时，这些必须变。

操作原则：档案的 §1–§6 只装声纹；每次写作任务在档案 §6.5 加一条"体裁校准"——结构零件按体裁清单来，声纹指标只对个别维度做松紧调制（如讲义版压缩轶事长度），其余原样。校验时 `--compare` 只核对声纹指标，体裁零件用清单人工核对。

Biber & Conrad (2009) 的原始区分是 style/register/genre 三分：register 由情境功能决定，genre 由文本常规结构决定，style 是非功能性的个人选择偏好。本 skill 的简化够用即可：**结构听体裁的，措辞听声纹的**。

---

## 第 6 层：叙事声音（Narrative Voice）——小说与叙事非虚构必需

前五层覆盖"怎么措辞"，叙事文本还有一层"谁在说、谁在看"——这是 voice 的主体（2024–2026 调研的共识性增量）：

- **POV 与人称**：第一/第三、单数/复数、叙述者是否现身（narratorial vs reflector 模式，Simpson 1993）。
- **话语呈现连续体**（Leech & Short 1981 第 10 章）：NRS（叙述者转述）→ IS（间接引语）→ FIS（自由间接）→ DS（直接引语）→ FDS（自由直接）；思想呈现平行（IT/FIT/DT/FDT）。逐段标注；FIS 是 Austen 式风格的关键标记，引号有无、报道从句有无、时态与人称归属都是可标注信号。
- **聚焦（focalization）**：POV（谁在说）≠ 聚焦（谁在看/感受）——第三人称也可以是内聚焦。按 FocalLens（Alam et al. 2026）的操作化三元标注：聚焦类型（internal/external/zero）× facet（perceptual 感知 / psychological 心理 / ideological 意识形态）。中文文本加申丹（2023）的修正：叙述眼光（文体学路径）与聚焦模式（叙事学路径）分开挂账，不照搬 Genette 术语。
- **情态遮蔽**（Simpson 1993）：叙述声音的确定性/义务感/愿望性（positive/negative/neutral shading），可用情态动词分布近似量化（Elhambakhsh & Saqafi 2026 已验证其可操作性）。
- **注意**：对文学文本，Hyland 立场介入层要与本层并列使用——FIS 里的态度是人物的，不是作者的，误判是常见错误。

## 中文计量补充（形合/意合之外的实证依据）

- **语体语法**（冯胜利）：中文语体沿"正式—非正式""典雅—便俗"两轴分布。可操作的正式度代理：双音节动词占比（"吃饭"→"就餐"越高越正式）、形式动词（加以/进行）、庄典标记（嵌偶词、合偶词）、标点比例（小说散文高、公文新闻低）。邹沁清 & 饶高琦 (2021, CCL) 用语料库方法验证了这批特征的语体区分力。
- **中文 MDA**：hy-stylo.cn（朱宇团队）提供 100+ 项汉语特征自动测算；袁亮杰、王治敏、朱宇 (2022, CCL) 对 111 项特征做因子分析得到中文学术语篇 7 个维度——中文"Biber 维度体系"的直接依据。CAT-LLM（Li et al. 2024, arXiv:2401.05707）提示中文风格定义需单列修辞与文化层。
- 工程化选项（非必需）：jieba 分词提升高频词准确度；LTP/spaCy zh 依存句法可把形合/意合操作化从标点近似升级为结构识别。

## LLM 仿写的已知系统性失败模式（校验时逐项排查）

来自 2024–2026 实证研究的一致性结论：

1. **滑向平均腔**（regression to the generic mean）：生成文本默认滑向"平均通用腔"，非正式文体（博客/论坛）比结构化文体（新闻/邮件/学术）严重；增加 few-shot 示例收益递减（Wang et al. 2025, arXiv:2509.14543；Bhandarkar et al. 2024）。
2. **方差塌缩**：LLM 仿写的首要失败是离散度塌缩而非均值偏差——真实作者句长 SD≈22，GPT-4 仿写 SD≈10.5（Kirilloff et al. 2025, Harvard Data Science Review）。脚本已内置塌缩检查（SD 比值 < 0.7 报警）。
3. **照抄输入**：零样本风格迁移时 LLM 倾向直接复制输入文本不改风格（Lai et al. 2024, arXiv:2410.00593）——检查输出与样本的逐句重合度。
4. **语法过度标准化**：LLM 文本的语法变异系统性小于人类，指令微调模型更甚（Reinhart et al. 2025, PNAS；Milička 2025）。
5. **微特征丢失**：省略号、非标准大小写、小众俚语、个人标点癖（Jangra et al. 2025）——这正是标点指纹与代词向量要逐项对照的原因。
6. **AI 腔负向清单**（改写后防"去人味"）：模式清单以 Wikipedia "Signs of AI writing" 为一手来源（按模型时代分层更新，词表有时效性），操作化版本见 blader/humanizer 的 33 条模式 + 误伤清单 + 人类正面特征（具体怪细节、未解决的张力、自我修正）。

## 风格画像的表示法（2025 年实证最有效的结构）

按 Kumar et al. (2025, arXiv:2502.13028）的 Author Writing Sheet 方法：

- 每条风格判断写成 **Claim–Evidence 对**（结论 + 原文摘录佐证），不写无证据的形容词；
- 与"平均作者"基线**做差分**（同一题目让通用模型写一版，目标作者的特征 = 与基线的差），避免把"所有学术写作都有的特征"误记为个人风格；
- 叙事类文本分四类记账：Plot / Creativity / Development / Language Use——实证显示 Language Use 和 Creativity 最容易个性化，与 prompt 强绑定的 Plot 最难迁移；
- 条目可转成 LISA（Patel et al. 2023）式可打分属性："The author uses X"句式 + 0–1 打分，在定性与定量之间架桥。

---

## 参考文献

**文体学与语料库语言学（框架地基）**

- Biber, D. (1988). *Variation across Speech and Writing*. Cambridge University Press.
- Biber, D., & Conrad, S. (2009). *Register, Genre, and Style*. Cambridge University Press.
- Halliday, M. A. K., & Hasan, R. (1976). *Cohesion in English*. Longman.
- Hyland, K. (2005). Stance and engagement: A model of interaction in academic discourse. *Discourse Studies*, 7(2), 173–192.
- Leech, G., & Short, M. (1981; 2nd ed. 2007). *Style in Fiction*. Longman / Pearson.（四层清单 1981: 75–82；话语呈现连续体见第 10 章）
- Simpson, P. (1993). *Language, Ideology and Point of View*. Routledge.（情态四系统与 POV shading）
- Ure, J. (1971). Lexical density and register differentiation. In Perren & Trim (Eds.), *Applications of Linguistics*. CUP.
- Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type–token ratio (MATTR). *Journal of Quantitative Linguistics*, 17(2), 94–100.
- Lu, X. (2010). Automatic analysis of syntactic complexity in second language writing. *International Journal of Corpus Linguistics*, 15(4), 474–496.（L2SCA 14 指标）
- Graesser, A. C., et al. (2004). Coh-Metrix. *Behavior Research Methods*, 36, 193–202.
- 连淑能 (1993). 《英汉对比研究》. 高等教育出版社.
- 冯胜利 (2010). 《汉语的韵律、词法与句法》（修订本）. 北京大学出版社.（语体语法两轴）
- 邹沁清、饶高琦 (2021). 汉语语体特征的计量与分类研究. *CCL 2021*.
- 袁亮杰、王治敏、朱宇 (2022). 人文社科学术论文语言变异的多维度分析. *CCL 2022*.
- 申丹 (2019). 《叙述学与小说文体学研究》（第 4 版）. 北京大学出版社. ISBN 978-7-301-29365-2；及申丹 (2023)《外语教学与研究》第 5 期.

**计算文体学与 LLM 风格实证（2023–2026）**

- Jin, D., et al. (2022). Deep learning for text style transfer: A survey. *Computational Linguistics*, 48(1), 155–205.
- Mukherjee, A., et al. (2024). A survey of text style transfer: Applications and ethical implications. arXiv:2407.16737.
- Patel, A., et al. (2023). Learning interpretable style embeddings via prompting LLMs (LISA). *Findings of EMNLP 2023*, 15270–15290.
- Patel, A., et al. (2025). StyleDistance. *NAACL 2025*, 8662–8685. arXiv:2410.12757.
- Kumar, S., et al. (2025). Whose story is it? Personalizing story generation by inferring author styles. arXiv:2502.13028.（Author Writing Sheet / Claim–Evidence / 平均作者差分）
- Wang, Y., et al. (2025). Catch me if you can? Not yet: LLMs still struggle to imitate the implicit writing styles of everyday authors. arXiv:2509.14543.
- Bhandarkar, A., et al. (2024). Emulating author style. *PERSONALIZE 2024*, 76–82.
- Kirilloff, G., et al. (2025). "Written in the style of": ChatGPT and the literary canon. *Harvard Data Science Review*.（方差塌缩）
- Reinhart, A., et al. (2025). Do LLMs write like humans? *PNAS*, 122(8), e2422455122. arXiv:2410.16107.
- Jangra, A., et al. (2025). Evaluating style-personalized text generation. arXiv:2508.06374.（多指标集成、IAA、微特征）
- Lai, H., et al. (2024). Style-specific neurons for steering LLMs in text style transfer. arXiv:2410.00593.（照抄输入失败模式）
- Hicke, R., & Mimno, D. (2025). Looking for the inner music: Probing LLMs' understanding of literary style. arXiv:2502.03647.（标点/代词/词序的风格信号）
- Sterman, S., et al. (2020). Interacting with literary style through computational tools. *CHI 2020*.（范例锚定、200 词粒度、作品内风格不均匀）
- Przystalski, K., et al. (2025). Stylometry recognizes human and LLM-generated texts in short samples. *Expert Systems with Applications*, 296, 129001.
- Li, X., et al. (2024). CAT-LLM: Style-enhanced LLMs with text style definition for Chinese article-style transfer. arXiv:2401.05707.
- Alam, T., et al. (2026). FocalLens: Visualizing narratives through focalization. arXiv:2604.14456.（聚焦三元操作化）

**实践资源**

- Wikipedia: Signs of AI writing（WP:AISIGNS，持续更新）——AI 腔模式清单一手来源，注意词表时效性。
- blader/humanizer（GitHub）——33 条模式 + 误伤清单 + voice calibration 的镜像实现。
- Mailchimp Content Style Guide——"voice 恒定 / tone 随情境"的行业金标准表述。
- 工具：StyloMetrix（arXiv:2309.12810）、pybiber/pseudobibeR、NeoSCA、hy-stylo.cn（中文百项特征）、AntConc（KWIC/keyness）、stylo(R)。

注：Leech & Short (2007)、Simpson (1993)、Biber & Conrad (2009)、连淑能 (1993) 原书未能直接获取全文，结构性要点均经开放文献交叉核实；如获得原书 PDF 可进一步校准页码级引用。
