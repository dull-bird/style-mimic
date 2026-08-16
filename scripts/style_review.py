#!/usr/bin/env python3
"""style_review.py — AI 味测量 + 双文本文风相似度（中英文，纯标准库）

两个子命令：
  python3 style_review.py aiflavor file.txt        # AI 味测量：模式命中逐项列出 + 0-100 启发式评分
  python3 style_review.py sim sample.txt draft.txt # 文风相似度：分层距离分解 + 0-100 相似分

设计依据：
  - AI 味模式清单：Wikipedia "Signs of AI writing"（WP:AISIGNS）+ blader/humanizer 33 条模式的中文化
    （词表有时效性：按 WP:AISIGNS 的模型时代分层原则维护，判定按"模式簇"而非单个词）
  - 方差塌缩：Kirilloff et al. (2025, HDSR)——LLM 仿写句长 SD 约为真人的一半
  - 滑向平均腔 / 过度标准化：Wang et al. (2025)、Reinhart et al. (2025, PNAS)
  - 相似度用规则计数特征的相对差（可追溯复算），不用黑盒 embedding（Jangra et al. 2025：单指标不可靠）

判分是启发式的：用于 review 时定位要改的段落，不作为"是否 AI 生成"的检测结论。
"""
import re, sys, math, os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_analyze import analyze, detect_lang, split_sentences, ZH_FUNC_CHARS

# ── AI 味模式库（每条：名称、正则/词表、权重、说明）────────────────────
ZH_AI_WORDS = {
    '空洞大词': ['赋能', '抓手', '闭环', '沉淀', '心智', '生态位', '护城河', '底层逻辑', '方法论体系'],
    '升华动词': ['彰显', '凸显', '折射', '见证', '诠释', '谱写', '书写.*篇章', '开启.*新篇章', '注入.*活力'],
    '里程碑套话': ['里程碑', '新篇章', '新高度', '新纪元', '跨越式发展', '质的飞跃'],
    '模糊归因': ['研究表明', '有研究', '专家指出', '学者认为', '众所周知.*吗', '有人说', '有相关数据'],
    '开头结尾套路': ['在当今时代', '在这个.*时代', '随着.*的不断发展', '随着.*的快速发展', '总而言之', '综上所述', '让我们一起', '未来可期', '值得期待', '让我们共同'],
    '连接腔': ['值得注意的是', '不难发现', '由此可见', '换句话说.*来说', '从这个意义上说', '不可否认'],
}
EN_AI_WORDS = {
    'GPT-era 高频词': ['delve', 'tapestry', 'vibrant', 'intricate', 'showcase', 'testament', 'realm',
                    'embark', 'elevate', 'foster', 'nuanced', 'pivotal', 'meticulous', 'symphony',
                    'landscape', 'beacon', 'profound', 'underscore', 'highlight'],
    '套话': ["it's important to note", 'it is important to note', "in today's", 'in conclusion',
            'firstly.*secondly', 'not only.*but also', 'plays a (crucial|vital|key) role',
            'in the ever-evolving', 'a testament to', 'rich tapestry'],
    '模糊归因': ['studies show', 'research suggests', 'experts say', 'it is widely believed', 'many argue'],
}
ZH_PATTERNS = [
    ('否定排比/递进三连', r'不仅.{2,30}(而且|还).{2,30}(更|甚至)', 2),
    ('-ing 式句尾升华', r'(彰显|凸显|折射|见证|体现|诠释)了?(深刻|深远|非凡|独特|重要|时代|历史)', 2),
    ('排比三连（、结构）', r'(、[^，。]{2,12}){2,}(?=，|。)', 1),
]
EN_PATTERNS = [
    ('否定排比 not just/not only', r'not (just|only)\b.{5,60}\bbut (also)\b', 2),
    ('serve as / stand as 套式', r'\b(serves?|stands?) as a\b', 1),
]


def _term_count(text, term, lang):
    """Count a lexicon term without matching English substrings.

    Chinese entries may intentionally contain a regex (for example
    ``开启.*新篇章``); English entries are literal phrases and need token
    boundaries so ``delve`` does not match ``delves``.
    """
    if lang == 'zh':
        return len(re.findall(term, text))
    body = term if re.search(r'[.\\*+?()|\[\]]', term) else re.escape(term)
    return len(re.findall(r'(?<![a-z])(?:' + body + r')(?![a-z])', text.lower()))


def _evidence(text, term, lang, limit=2):
    """Return short source snippets so every hit can be manually checked."""
    if lang == 'zh':
        pattern, hay = term, text
    else:
        body = term if re.search(r'[.\\*+?()|\[\]]', term) else re.escape(term)
        pattern, hay = r'(?<![a-z])(?:' + body + r')(?![a-z])', text.lower()
    snippets = []
    for match in re.finditer(pattern, hay):
        start, end = max(0, match.start() - 12), min(len(text), match.end() + 12)
        snippets.append(text[start:end].replace('\n', ' '))
        if len(snippets) >= limit:
            break
    return '；'.join(snippets)


def aiflavor(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    lang = detect_lang(text)
    res = analyze(path)
    total = res['units']
    lex = ZH_AI_WORDS if lang == 'zh' else EN_AI_WORDS
    pats = ZH_PATTERNS if lang == 'zh' else EN_PATTERNS
    hits = []
    score = 0.0
    for group, words in lex.items():
        n = 0
        evidence = []
        for w in words:
            n += _term_count(text, w, lang)
            if len(evidence) < 2 and _term_count(text, w, lang):
                evidence.append(_evidence(text, w, lang, 1))
        if n and total:
            per = n / total * 1000
            pts = min(per * 2, 10)
            score += pts
            hits.append((f'{group}', n, round(per, 2), round(pts, 1), '；'.join(evidence)))
    for name, pat, w in pats:
        n = _term_count(text, pat, lang)
        if n and total:
            per = n / total * 1000
            pts = min(per * 3 * w, 12)
            score += pts
            hits.append((name, n, round(per, 2), round(pts, 1), _evidence(text, pat, lang)))
    # 方差塌缩（CV = stdev/mean；人类非虚构 CV 通常 0.6–0.9，LLM 常 < 0.5）
    cv = res['tail']['cv']
    sentence_lengths = [len(re.findall(r'[一-鿿]', s)) if lang == 'zh'
                        else len(re.findall(r"[a-zA-Z']+", s))
                        for s in split_sentences(text, lang)]
    enough_length_variation = len(set(sentence_lengths)) >= 4
    # CV and tail statistics need enough independent sentences.  Without this
    # gate every one-line note (and every subtitle line) is falsely “collapsed”.
    if res['sentences'] >= 8 and enough_length_variation and cv < 0.45:
        pts = 15
        score += pts
        hits.append((f'方差塌缩（CV={round(cv,2)} < 0.45）', '—', '—', pts))
    elif res['sentences'] >= 8 and enough_length_variation and cv < 0.55:
        score += 6
        hits.append((f'节奏偏匀（CV={round(cv,2)}）', '—', '—', 6))
    # 破折号密度
    dash = text.count('——') if lang == 'zh' else text.count('—') + text.count(' - ')
    dper = dash / total * 1000 if total else 0
    if dper > 8:
        score += 8
        hits.append(('破折号密集', dash, round(dper, 2), 8))
    score = min(round(score), 100)
    level = ('不可评分（无可分析单位）' if total == 0 else
             '低（像人写的）' if score < 15 else
             '中（有 AI 腔段落）' if score < 35 else '高（明显 AI 腔）')
    print(f'## AI 味测量：{path}')
    print(f'- 语言：{lang}｜规模：{total} 单位｜**AI 味评分 {score}/100（{level}）**')
    print('- 说明：启发式 review 工具，定位需修改处，不作"是否 AI 生成"的判定结论（WP:AISIGNS 反误伤原则：看模式簇不看单词）\n')
    if res['sentences'] < 8 or total < 80:
        print('- ⚠️ 样本过短：不启用方差塌缩判据，AI 味分数仅作线索，不能作稳定结论。\n')
    if hits:
        print('| 模式 | 命中数 | 每千单位 | 扣分 | 原文证据（最多2处） |\n|---|---|---|---|---|')
        for h in hits:
            print(f'| {h[0]} | {h[1]} | {h[2]} | {h[3]} | {h[4]} |')
    else:
        print('未命中已知 AI 腔模式。')
    return score


LAYERS = {
    '词汇': [('mattr', 1.0), ('ttr', 0.5)],
    '句法节奏': [('sent_len.mean', 1.0), ('sent_len.stdev', 1.5), ('sent_len.p90', 0.5),
                 ('tail.p05', 0.5), ('tail.p95', 0.5), ('tail.iqr', 0.8), ('clauses_per_sent.mean', 1.0)],
    '衔接标记': [('markers_per_1000.additive', 1), ('markers_per_1000.adversative', 1), ('markers_per_1000.causal', 1), ('markers_per_1000.temporal', 1)],
    '立场介入': [('markers_per_1000.hedges', 1.2), ('markers_per_1000.boosters', 1.2), ('markers_per_1000.self', 1), ('markers_per_1000.reader', 1.2), ('markers_per_1000.directives', 1)],
    '修辞标记': [('markers_per_1000.simile', 1.2), ('markers_per_1000.exemplify', 1), ('sent_overlap', 1)],
    '代词指纹': [('pronouns_per_1000.1sg', 1), ('pronouns_per_1000.1pl', 1), ('pronouns_per_1000.2nd', 1.2), ('pronouns_per_1000.3rd', 1)],
}


def _content_tokens(path, lang):
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    if lang == 'zh':
        chars = [c for c in re.findall(r'[一-鿿]', text) if c not in ZH_FUNC_CHARS]
        return set(''.join(chars[i:i + 2]) for i in range(len(chars) - 1))
    stop = set('the a an and or but if of to in on for with as at by from is are was were be been it its this that these those i you he she we they not no do does did have has had will would can could may might shall should must'.split())
    return set(w for w in re.findall(r"[a-z']+", text.lower()) if len(w) > 2 and w not in stop)


def _distance(a, b):
    """Bounded symmetric distance that behaves sensibly around zero."""
    if a == b:
        return 0.0
    return min(abs(a - b) / max(abs(a), abs(b), 1e-6), 1.0)


def getf(res, dotted):
    cur = res
    for k in dotted.split('.'):
        cur = cur[k]
    return cur


def sim(path_a, path_b):
    A, B = analyze(path_a), analyze(path_b)
    if A['lang'] != B['lang']:
        print(f'⚠️ 语言不同（{A["lang"]} vs {B["lang"]}），相似度仅供参考')
    print(f'## 文风相似度：{os.path.basename(path_a)} vs {os.path.basename(path_b)}\n')
    too_short = A['sentences'] < 5 or B['sentences'] < 5 or A['units'] < 80 or B['units'] < 80
    if too_short:
        print('⚠️ 样本过短：规则分布不稳定，综合分仅作线索，不能作“同一声纹”结论。\n')
    total_w, total_d = 0.0, 0.0
    divergent = []
    for layer, feats in LAYERS.items():
        lw, ld = 0.0, 0.0
        for f, w in feats:
            a, b = getf(A, f), getf(B, f)
            d = _distance(a, b)
            lw += w
            ld += w * d
            total_w += w
            total_d += w * d
            if d > 0.4:
                divergent.append((f, a, b, round(d, 2)))
        pct = round(100 * (1 - ld / max(lw, 1e-9)))
        print(f'- {layer}：相似 {pct}%')
    # TTR/MATTR can be equal for two texts with disjoint vocabularies. Add a
    # transparent content Jaccard signal to prevent that false positive.
    ta, tb = _content_tokens(path_a, A['lang']), _content_tokens(path_b, B['lang'])
    content_sim = len(ta & tb) / len(ta | tb) if ta or tb else 0.0
    content_weight = 2.0
    total_w += content_weight
    total_d += content_weight * (1 - content_sim)
    print(f'- 词汇内容（Jaccard）：相似 {round(content_sim * 100)}%')
    overall = round(100 * (1 - total_d / max(total_w, 1e-9)))
    verdict = ('样本过短，无法判定' if too_short else
               '同一声纹区间' if overall >= 85 else ('相近但有漂移' if overall >= 70 else '明显不同'))
    print(f'\n**综合相似度 {overall}%（{verdict}）**')
    if divergent:
        print('\n偏差最大的特征（对称相对差 > 0.4）：')
        for f, a, b, d in sorted(divergent, key=lambda x: -x[3])[:6]:
            print(f'- {f}：{a} vs {b}（差 {d}）')
    print('\n注：基于规则计数特征（可复算），未用 embedding；≥85 可视为同一声纹，70–85 需对照档案逐项查，<70 重写。')
    return overall


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'aiflavor':
        aiflavor(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'sim':
        sim(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)
