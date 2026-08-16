#!/usr/bin/env python3
"""style_analyze.py — 文体计量分析（中英文，jieba 可选）

对一个或多个文本文件输出定量文体指标报告（Markdown 或 JSON）。
指标框架见 references/style-dimensions.md；主要依据：
  - Biber (1988) 66 项形态句法特征的可用子集（每千单位频率）
  - Hyland (2005) stance/engagement 标记（hedge/booster/self-mention/reader pronoun/directive）
  - Ure (1971) 词汇密度、TTR；Leech & Short (1981) 句类与衔接维度
  - 连淑能 (1993) 形合/意合：以"每句小句数"与"连接词密度"作操作化近似

用法：
  python3 style_analyze.py file1.txt [file2.txt ...]            # Markdown 报告
  python3 style_analyze.py file.txt --json                      # JSON
  python3 style_analyze.py sample.txt draft.txt --compare       # 双文本偏差对照
"""
import re, sys, json, math, argparse, logging, warnings
from collections import Counter

try:  # Optional: improves Chinese lexical measures without making it a dependency.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        import jieba  # type: ignore
    jieba.setLogLevel(logging.ERROR)
except Exception:  # pragma: no cover - exercised on minimal installations
    jieba = None

# ── 标记词表（按文献分类）────────────────────────────────────────────
ZH = {
    'additive':  ['而且', '并且', '此外', '另外', '同时', '还', '也'],
    'adversative': ['但是', '但', '然而', '可是', '不过', '却', '相反', '尽管', '虽然'],
    'causal':    ['因为', '所以', '因此', '由于', '于是', '导致', '可见', '故而'],
    'temporal':  ['首先', '其次', '然后', '接着', '最后', '第一', '第二', '接下来', '与此同时'],
    'hedges':    ['可能', '或许', '大概', '似乎', '好像', '往往', '通常', '一般来说', '某种意义上', '差不多', '左右'],
    'boosters':  ['一定', '必然', '毫无疑问', '显然', '确实', '绝对', '肯定', '众所周知', '事实上'],
    'self':      ['我', '我们', '咱们'],
    'reader':    ['你', '您', '你们', '大家'],
    'directives': ['请', '试着', '试试', '不妨', '记住', '注意', '想象', '想一想', '别忘了', '停下来'],
    'simile':    ['就像', '好比', '仿佛', '如同', '宛如', '犹如', '相当于', '像是', '跟……一样'],
    'exemplify': ['例如', '比如', '比方说', '举个例子', '以', '试想'],
}
EN = {
    'additive':  ['moreover', 'furthermore', 'also', 'in addition', 'besides', 'and'],
    'adversative': ['but', 'however', 'yet', 'although', 'though', 'nevertheless', 'whereas', 'while'],
    'causal':    ['because', 'so', 'therefore', 'thus', 'hence', 'as a result', 'since'],
    'temporal':  ['first', 'second', 'then', 'next', 'finally', 'afterward', 'meanwhile'],
    'hedges':    ['may', 'might', 'perhaps', 'probably', 'possibly', 'seems', 'appears', 'tend to', 'generally', 'roughly', 'almost', 'about'],
    'boosters':  ['certainly', 'definitely', 'clearly', 'obviously', 'indeed', 'always', 'never', 'in fact', 'of course', 'must'],
    'self':      ['i', 'we', 'my', 'our', 'me', 'us'],
    'reader':    ['you', 'your', 'yours'],
    'directives': ['try', 'imagine', 'notice', 'remember', 'consider', 'picture', "let's", 'let us', 'think about'],
    'simile':    ['like', 'as if', 'as though', 'just as', 'imagine', 'picture'],
    'exemplify': ['for example', 'for instance', 'e.g.', 'such as', 'say,'],
}
ZH_FUNC_CHARS = set('的了是在我不有和人这中大为上个国他以要你他到时说们就来去对生会子着自年那她可以于出好也都就还又呢吗吧啊嘛把被让从但而及与或且如果因为所虽然很更最没有什怎样么')


def detect_lang(text):
    """Return the dominant script without a brittle absolute-size cutoff.

    The old ``cjk > 50`` rule classified short Chinese notes (including a
    one-sentence draft) as English and then silently reported zero units.
    Pure-script short inputs are unambiguous; for mixed inputs the script with
    the larger count wins, with a small tie-break in favour of Chinese because
    Chinese does not use whitespace tokenisation.
    """
    cjk = len(re.findall(r'[一-鿿]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    if cjk == 0:
        return 'en'
    if latin == 0:
        return 'zh'
    return 'zh' if cjk >= latin else 'en'


def split_sentences(text, lang):
    # 剥离 VTT/SRT 时间戳与序号行，避免污染计数
    text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
    text = re.sub(r'(?m)^\d{2}:\d{2}:\d{2}[.,]\d+\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d+.*$', '', text)
    if lang == 'zh':
        # 字幕等无句读文本：换行也视为边界
        parts = re.split(r'(?<=[。！？…])|\n+', text)
    else:
        text = re.sub(r'\s+', ' ', text)
        parts = re.split(r'(?<=[.!?])\s+', text)
    return [p for p in (s.strip() for s in parts) if p and re.search(r'[一-鿿a-zA-Z]', p)]


def units_of(text, lang):
    """统计单位：zh 返回汉字数；en 返回词列表。"""
    if lang == 'zh':
        return len(re.findall(r'[一-鿿]', text))
    return re.findall(r"[a-zA-Z']+", text.lower())


def zh_tokens(text):
    """Return Chinese word tokens when jieba is available, else characters."""
    if jieba is not None:
        return [w for w in jieba.lcut(text) if re.search(r'[一-鿿]', w)]
    return re.findall(r'[一-鿿]', text)


def sent_len(s, lang):
    if lang == 'zh':
        return len(re.findall(r'[一-鿿]', s))
    return len(re.findall(r"[a-zA-Z']+", s))


def clauses_per_sentence(sents, lang):
    """每句小句数近似；中文顿号是枚举标记，不算小句边界。"""
    marks = '，；：' if lang == 'zh' else ',;:'
    vals = []
    for s in sents:
        n = sum(s.count(m) for m in marks)
        vals.append(1 + n)
    return vals


def percentile(vals, p):
    if not vals:
        return 0
    vals = sorted(vals)
    k = (len(vals) - 1) * p / 100
    f, c = math.floor(k), math.ceil(k)
    return round(vals[f] + (vals[c] - vals[f]) * (k - f), 1)


def marker_counts(text, lang):
    table = ZH if lang == 'zh' else EN
    out = {}
    hay = text if lang == 'zh' else ' ' + re.sub(r'\s+', ' ', text.lower()) + ' '
    for cat, words in table.items():
        if lang == 'zh':
            # Longest-first, non-overlapping matching prevents “但是” from
            # being counted once as “但是” and again as “但”.
            pattern = '|'.join(re.escape(w) for w in sorted(words, key=len, reverse=True))
            n = len(re.findall(pattern, hay))
        else:
            n = sum(len(re.findall(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', hay))
                    for w in words)
        out[cat] = n
    return out


def top_content(text, lang, k=25):
    if lang == 'en':
        stop = set('the a an and or but if of to in on for with as at by from is are was were be been it its this that these those i you he she we they not no do does did have has had will would can could may might shall should must'.split())
        words = [w for w in re.findall(r"[a-z']+", text.lower()) if w not in stop and len(w) > 2]
        return Counter(words).most_common(k)
    if jieba is not None:
        stop = set('的了是在我不有和人这中大为上个国他以要你到时说们就来去对生会子着自年那她可以于出好也都还又')
        words = [w for w in zh_tokens(text) if w not in stop and len(w) > 1]
        return Counter(words).most_common(k)
    # No tokenizer: use a reproducible two-character approximation.
    chars = re.findall(r'[一-鿿]', text)
    bigrams = (''.join(chars[i:i+2]) for i in range(len(chars) - 1))
    bigrams = [b for b in bigrams if b[0] not in ZH_FUNC_CHARS and b[1] not in ZH_FUNC_CHARS]
    return Counter(bigrams).most_common(k)


def mattr(tokens, win=50):
    """移动平均 TTR（MATTR）——长度无关的词汇丰富度（Covington & McFall 2010），
    解决裸 TTR 随文本变长系统性下降的问题（Lu 2012 的批评）。"""
    if len(tokens) < win:
        return round(len(set(tokens)) / max(len(tokens), 1), 3)
    vals = [len(set(tokens[i:i + win])) / win for i in range(len(tokens) - win + 1)]
    return round(sum(vals) / len(vals), 3)


def pronoun_vector(text, lang):
    """人称代词相对频率（每千单位）——Hicke & Mimno (2025)：代词是功能词中最强的作者级风格载体。"""
    if lang == 'zh':
        total = max(len(re.findall(r'[一-鿿]', text)), 1)
        # Match plural forms first and exclude their first character from the
        # singular bucket; ``str.count('我')`` would otherwise count ``我们``
        # twice across the two person categories.
        counts = {
            '1sg': len(re.findall(r'(?<![们咱])我(?!们)', text)),
            '1pl': len(re.findall(r'我们|咱们', text)),
            '2nd': len(re.findall(r'你们|你|您', text)),
            '3rd': len(re.findall(r'他们|她们|它们|他|她|它', text)),
        }
        return {g: round(n / total * 1000, 1) for g, n in counts.items()}
    words = re.findall(r"[a-z']+", text.lower())
    total = max(len(words), 1)
    c = Counter(words)
    groups = {'1sg': ['i', 'me', 'my', 'mine'], '1pl': ['we', 'us', 'our', 'ours'],
              '2nd': ['you', 'your', 'yours'], '3rd': ['he', 'him', 'his', 'she', 'her', 'hers', 'they', 'them', 'their', 'it', 'its']}
    return {g: round(sum(c[w] for w in ws) / total * 1000, 1) for g, ws in groups.items()}


def sentence_overlap(sents, lang):
    """相邻句词汇重叠率（Coh-Metrix 式指称衔接近似）：相邻句共享实词比例。"""
    def content(s):
        if lang == 'zh':
            ch = [c for c in re.findall(r'[一-鿿]', s) if c not in ZH_FUNC_CHARS]
            return set(ch)
        return set(w for w in re.findall(r"[a-z']+", s.lower()) if len(w) > 3)
    vals = []
    for a, b in zip(sents, sents[1:]):
        A, B = content(a), content(b)
        if A and B:
            vals.append(len(A & B) / len(A | B))
    return round(sum(vals) / len(vals), 3) if vals else 0.0


def punct_fingerprint(text, lang):
    """标点指纹（每千单位）——Hicke & Mimno (2025)：标点/大小写模式携带作者级风格信号。"""
    total = max(len(re.findall(r'[一-鿿]', text)) if lang == 'zh' else len(re.findall(r"[a-zA-Z']+", text)), 1)
    marks = '，、；：。？！…—「」“”' if lang == 'zh' else ',;:.?!—-"\''
    return {m: round(text.count(m) / total * 1000, 1) for m in marks if text.count(m) > 0}


def analyze(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    lang = detect_lang(text)
    sents = split_sentences(text, lang)
    paras = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
    u = units_of(text, lang)
    total = u if lang == 'zh' else len(u)
    lens = [sent_len(s, lang) for s in sents]
    cls = clauses_per_sentence(sents, lang)
    mc = marker_counts(text, lang)
    per1000 = {k: round(v / max(total, 1) * 1000, 2) for k, v in mc.items()}
    q = sum(1 for s in sents if s.rstrip().endswith(('？', '?')) if s.strip())
    ex = sum(1 for s in sents if s.rstrip().endswith(('！', '!')) if s.strip())
    mean = sum(lens) / max(len(lens), 1)
    var = sum((x - mean) ** 2 for x in lens) / max(len(lens), 1)
    sd = math.sqrt(var)
    median = percentile(lens, 50)
    mad = percentile([abs(x - median) for x in lens], 50)
    skewness = (sum((x - mean) ** 3 for x in lens) / max(len(lens), 1)
                / max(sd ** 3, 1e-9)) if len(lens) >= 3 and sd > 0 else 0.0
    tail = {
        'p05': percentile(lens, 5),
        'p95': percentile(lens, 95),
        'iqr': round(percentile(lens, 75) - percentile(lens, 25), 1),
        'mad': round(mad, 1),
        'skewness': round(skewness, 3),
        'cv': round(sd / max(mean, 1e-9), 3) if mean else 0.0,
        'min': min(lens) if lens else 0,
        'max': max(lens) if lens else 0,
        # Tail percentiles are unstable for tiny samples; expose this so a
        # caller cannot mistake a point estimate for a reliable distribution.
        'reliable': len(lens) >= 20,
    }
    buckets = [0, 0, 0, 0, 0]
    edges = (10, 20, 35, 50) if lang == 'zh' else (8, 15, 25, 40)
    for L in lens:
        i = 0
        while i < 4 and L > edges[i]:
            i += 1
        buckets[i] += 1
    ttr = None
    if lang == 'en':
        toks = u
        ttr = round(len(set(toks)) / max(len(toks), 1), 3)
        lex_tokens = toks
    else:
        tokens = zh_tokens(text)
        ttr = round(len(set(tokens)) / max(len(tokens), 1), 3)
        lex_tokens = tokens
    return {
        'file': path, 'lang': lang,
        'units': total, 'sentences': len(sents), 'paragraphs': len(paras),
        'ttr': ttr, 'mattr': mattr(lex_tokens),
        'pronouns_per_1000': pronoun_vector(text, lang),
        'sent_overlap': sentence_overlap(sents, lang),
        'punct_per_1000': punct_fingerprint(text, lang),
        'sent_len': {'mean': round(mean, 1), 'median': median,
                     'stdev': round(sd, 1), 'p10': percentile(lens, 10),
                     'p90': percentile(lens, 90),
                     'buckets': buckets, 'bucket_edges': edges,
                     'p05': tail['p05'], 'p95': tail['p95'],
                     'iqr': tail['iqr'], 'mad': tail['mad'],
                     'skewness': tail['skewness'], 'cv': tail['cv']},
        'tail': tail,
        'clauses_per_sent': {'mean': round(sum(cls) / max(len(cls), 1), 2),
                             'p90': percentile(cls, 90)},
        'sent_types': {'declarative': len(sents) - q - ex, 'interrogative': q, 'exclamatory': ex},
        'markers_per_1000': per1000,
        'ttr': ttr,
        'mean_word_len': (round(sum(len(w) for w in u) / max(len(u), 1), 2) if lang == 'en' else None),
        'top_content': top_content(text, lang),
        'tokenization': ('jieba' if lang == 'zh' and jieba is not None else
                         'char' if lang == 'zh' else 'whitespace-word'),
    }


def md_report(res):
    L = res['sent_len']
    lines = [f"## {res['file']}",
             f"- 语言：{res['lang']}｜规模：{res['units']} 单位 / {res['sentences']} 句 / {res['paragraphs']} 段",
             f"- 句长：均值 {L['mean']}，中位 {L['median']}，标准差 {L['stdev']}，p10–p90 = {L['p10']}–{L['p90']}",
             f"- 尾部：p05–p95 = {res['tail']['p05']}–{res['tail']['p95']}，IQR {res['tail']['iqr']}，MAD {res['tail']['mad']}，偏度 {res['tail']['skewness']}，CV {res['tail']['cv']}" + ("（n<20，尾部不稳定）" if not res['tail']['reliable'] else ''),
             f"- 句长分布（≤{L['bucket_edges'][0]} / …{L['bucket_edges'][1]} / …{L['bucket_edges'][2]} / …{L['bucket_edges'][3]} / >{L['bucket_edges'][3]}）：{res['sent_len']['buckets']}",
             f"- 每句小句数：均值 {res['clauses_per_sent']['mean']}，p90 {res['clauses_per_sent']['p90']}（形合度近似）",
             f"- 句类：陈述 {res['sent_types']['declarative']} / 疑问 {res['sent_types']['interrogative']} / 感叹 {res['sent_types']['exclamatory']}",
             f"- TTR：{res['ttr']}｜MATTR：{res['mattr']}（长度无关）｜分词：{res['tokenization']}" + (f"，均词长 {res['mean_word_len']}" if res['mean_word_len'] else ''),
             "- 标记（每千单位）：" + '，'.join(f"{k} {v}" for k, v in res['markers_per_1000'].items()),
             "- 代词（每千单位）：" + '，'.join(f"{k} {v}" for k, v in res['pronouns_per_1000'].items()),
             f"- 句间词汇重叠率：{res['sent_overlap']}（指称衔接近似）",
             "- 标点指纹（每千单位）：" + '，'.join(f"{k} {v}" for k, v in res['punct_per_1000'].items()),
             "- 高频实词/二字元：" + '，'.join(f"{w}×{c}" for w, c in res['top_content'][:15])]
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--compare', action='store_true', help='两个文件时输出偏差对照')
    a = ap.parse_args()
    results = [analyze(f) for f in a.files]
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return
    for r in results:
        print(md_report(r), '\n')
    if a.compare and len(results) == 2:
        s, d = results
        print('## 偏差对照（draft 相对 sample）')
        if s['lang'] != d['lang']:
            print(f"⚠️ 语言不同（{s['lang']} vs {d['lang']}），不应把该结果当作声纹偏差")
        for k in ('mean', 'stdev'):
            sv, dv = s['sent_len'][k], d['sent_len'][k]
            print(f"- 句长{k}：{sv} → {dv}（{'↑' if dv > sv else '↓'} {round(abs(dv-sv),1)}）")
        # 方差塌缩检查（Kirilloff et al. 2025：LLM 仿写最常见的系统性失败是离散度塌缩而非均值偏差）
        ss, ds = s['sent_len']['stdev'], d['sent_len']['stdev']
        if s['sentences'] >= 20 and d['sentences'] >= 20 and ss > 0 and ds / ss < 0.7:
            print(f"⚠️ 方差塌缩：句长标准差 {ss} → {ds}（比值 {round(ds/ss,2)} < 0.7），节奏多样性明显不足")
        for key in ('p05', 'p95', 'iqr', 'mad', 'cv'):
            print(f"- 尾部:{key}：{s['tail'][key]} → {d['tail'][key]}")

        def flag_delta(sv, dv, high=2.0, low=0.5, floor=1.0):
            # A zero baseline must still flag a newly introduced feature.
            if sv == 0:
                return ' ⚠️新增' if dv != 0 else ''
            return ' ⚠️' if dv / sv > high or dv / sv < low or abs(dv - sv) > floor and sv < floor else ''

        for name, key in (('MATTR', 'mattr'), ('句间重叠', 'sent_overlap')):
            sv, dv = s[key], d[key]
            flag = flag_delta(sv, dv, high=1.5, low=0.67, floor=0.05)
            print(f"- {name}：{sv} → {dv}{flag}")
        for cat in s['markers_per_1000']:
            sv, dv = s['markers_per_1000'][cat], d['markers_per_1000'][cat]
            flag = flag_delta(sv, dv)
            print(f"- {cat}：{sv} → {dv}{flag}")
        for cat in s['pronouns_per_1000']:
            sv, dv = s['pronouns_per_1000'][cat], d['pronouns_per_1000'][cat]
            flag = flag_delta(sv, dv)
            print(f"- 代词:{cat}：{sv} → {dv}{flag}")


if __name__ == '__main__':
    main()
