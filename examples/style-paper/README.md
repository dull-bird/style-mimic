# 文体实验室：一题十一声

这是 `style-mimic` 的离线展示页与配套 LaTeX 论文。它把同一篇关于框架本身的论文拆成五个语义单元，再用六种中文/英文文体学取向各写一版，页面和论文都从 [`data/styles.json`](data/styles.json) 读取同一份内容。

## 本地查看

```bash
cd examples/style-paper
python3 -m http.server 8765
```

打开 <http://127.0.0.1:8765/>。页面没有外部资源；使用 HTTP 是为了让浏览器正常读取 JSON。完整 PDF 在 [`tex/style-mimic-paper.pdf`](tex/style-mimic-paper.pdf)。

## 重新测量与编译

```bash
python3 scripts/measure_styles.py data/styles.json
cd tex
./build.sh
```

`measure_styles.py` 为每个声音生成 CV、p05/p95、IQR、MATTR、AI 味 review 分和同语言中性基线相似度；`build.sh` 用 XeLaTeX + BibTeX 生成论文、附录和 `build.log`。

这些分数是可追溯的编辑线索，不是作者识别器，也不是“文本是否由 AI 生成”的判决。活人作者部分均标为教学仿写，不冒充原作或作者背书。
