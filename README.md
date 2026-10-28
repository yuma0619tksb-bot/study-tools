# study-tools

電通大1年の試験対策用に、**答えを機械で検算した練習問題バンク**を作るリポジトリ。
スマホ用の練習ページ「通学ドリル」に取り込む `output/problems.json` を生成する。

- 科目: 解析学(`k`)・微積第二(`b`)・物理学概論第二(`p`)
- 問題数: 96 問(解析学 38 / 微積第二 37 / 物理学概論第二 21)
- 手で打った答えは1つもない。すべて SymPy(物理は浮動小数の公式)で計算し、
  さらに **別ルートで検算** してから出力している。検算できない問題は入れていない。

## 中身

| 科目 | 主な内容 |
| --- | --- |
| 解析学 | 部分分数分解による望遠鏡和、比・根・p 級数との比較による収束判定、絶対収束と条件収束(ライプニッツ)、収束半径(**$\sum a^n x^{2n}$ 型・$x^{2n+1}$ 型を9問**、端点まで調べる収束域を含む)、パラメータの場合分け |
| 微積第二 | 偏微分(合成関数・指数・対数・三角・逆三角・$x^y$)、連鎖律、接平面(陽関数・陰関数・平行条件)、2変数の極限(存在する/経路で値が変わる)、高階偏導関数、全微分(近似値・誤差) |
| 物理学概論第二 | 融解・沸騰のエントロピー $Q/T$、加熱のエントロピー $mc\log(T_2/T_1)$、理想気体の内部エネルギー($f=3,5$)、カルノー機関、等温・断熱変化。$R=8.31$、$0$℃$=273.15\ \mathrm{K}$、答えは有効数字3桁 |

レベルの意味:

- **Lv1** 教科書の典型問題の数値を変えたもの
- **Lv2** 同じ考え方を別の設定で使うもの
- **Lv3** 2つの考え方の組み合わせ、または場合分けが必要なもの

## 再生成と検証

```sh
pip install -r requirements.txt   # sympy, mpmath
python scripts/build.py           # output/problems.json と output/params.json を作り直す
python scripts/verify.py          # 検証(失敗すると終了コード 1)
```

`build.py` は乱数の種を固定しているので、何度実行しても同じファイルになる。

`verify.py` が確かめること:

1. **形式**: 必須キーちょうど・型・id の一意性と接頭辞・order の一意性・問題数 80〜100・
   `$` の対応・`{}` と `\left`/`\right` の対応・問題文の重複なし
2. **再現性**: `output/params.json` に保存した「問題の型とパラメータ」から問題を作り直し、
   保存されている問題文・途中式・答えと完全に一致するか(手で書き換えた答えはここで見つかる)
3. **検算**: 答えを解答とは別の道筋で求め直して一致するか。例えば
   - 望遠鏡和: 部分和の式を $N=1,\dots,13$ の厳密な和と照合し、SymPy の `summation` とも比べる
   - 収束判定・収束半径: 比と $n$ 乗根を大きな $n$ で高精度に数値計算して判定する
     (SymPy の `is_convergent` や階乗を含む極限は誤答することがあるので使わない)
   - 偏微分・接平面: mpmath の数値微分と比べる。連鎖律は「代入してから直接微分」と比べる
   - 2変数の極限: 原点のまわりのランダムな点で $|f-L|$ の上からの評価を確かめ、経路ごとの値も数値で出す
   - 物理: 数値積分 $\int dQ/T$、熱量保存の方程式を数値で解く、カルノーサイクルを4過程で模擬計算する、
     断熱変化を常微分方程式として解く、など
4. **物理の数値**: 答えに出てくる数値がすべて、検算値を有効数字3桁にしたものと一致するか
5. **決定性**: 生成器をもう一度動かした結果が保存済みの JSON と一致するか

## 単元と類題

- `output/params.json` には問題ごとの単元(`unit`、例: `収束半径(x²ⁿ型)`)も入っている。通学ドリルは
  これを `meta` コレクションに入れて、単元ごとの理解度を出すのに使う。
- 類題は「元の問題と同じ出題枠で数値だけ変えた問題」で、検算に通ったものだけを
  `problem_bank/variants.json` に追加する。ドリルで×や△だった問題の id を指定して実行する:

  ```sh
  python scripts/make_variants.py k024 b013 --per 1
  python scripts/build.py && python scripts/verify.py
  ```

  通学ドリルで「この型の類題をClaudeに頼む」を押すと、学生本人の記録(`data/users/<id>`)に
  `kind: "variant_request"` の文書が残る。Claude に「類題を追加して」と頼んだら、その文書と×・△の記録を読み、
  上のコマンドで類題を作って検証に通してから、ドリルの `problems` と `meta` コレクションに書き込む。

  類題の id は各科目の基本問題の後ろに続く(例: 解析学なら `k039` 以降)。数値の選択肢がない固定の問題
  (例: `k004`)は類題を作れないので、同じ単元の別の問題で練習する。

## JSON の形式

`output/problems.json` は次の形のオブジェクトの配列(キーはこれでちょうど)。

```json
{
  "id": "k024",
  "order": 24,
  "subject": "解析学",
  "title": "x²ⁿ 型の収束半径",
  "level": 1,
  "question": "整級数 $\\displaystyle\\sum_{n=0}^{\\infty} 5^{n}\\,x^{2 n}$ の収束半径を求めよ。途中式も書くこと。",
  "tool": "$x^{2n}$ の係数しかなく奇数次の係数が $0$ なので、係数の比の公式はそのまま使えない。…",
  "steps": ["$t=x^{2}$ とおくと …", "…"],
  "answer": "$R=\\dfrac{\\sqrt{5}}{5}$"
}
```

| キー | 型 | 内容 |
| --- | --- | --- |
| `id` | 文字列 | 科目の接頭辞(`k` 解析学 / `b` 微積第二 / `p` 物理学概論第二)+ 3桁の番号 |
| `order` | 整数 | 全体での並び順(1 から) |
| `subject` | 文字列 | `解析学` / `微積第二` / `物理学概論第二` |
| `title` | 文字列 | 短い題名 |
| `level` | 整数 | 1 / 2 / 3 |
| `question` | 文字列 | 問題文。数式は `$...$`(KaTeX で表示できることを確認済み) |
| `tool` | 文字列 | どの道具をなぜ使うか(1〜2文) |
| `steps` | 文字列の配列 | 要点となる途中式 |
| `answer` | 文字列 | 最終的な答え |

`output/params.json` は検算用で、id ごとに問題の型・レベル・パラメータを持つ(ドリルへの取り込みには不要)。

## TOEIC 単語

`toeic/words_src.py` が単語リストの元データ(600・730・860点レベル各60語、例文はすべて自作)。
各語に意味・例文・訳と、Part 5 風の穴埋め用の誤答3つ(答えと同じ語形で、文法か意味のどちらかで明らかに入らない語)を持つ。

```sh
python scripts/check_words.py   # 重複・例文の [ ] ・語形・誤答の形を検証して toeic/words.json を作る
```

通学ドリルでは `words` コレクションにレベルごとの文書(`b600` など、`list` に単語の配列)として入れる。
学習の記録(間隔反復の状態)は学生本人の `data/users/<id>` に `w_<単語id>` として保存される。

## TOEIC 問題(Part 2〜7)

問題の下書きは Gemini に作らせ(Claude のトークン節約のため)、別の Gemini モデルに答えを見せずに解かせて検算する。
食い違った問題だけを Claude が見直し、直すか捨てる。検算の記録がない問題は `check_toeic.py` が通さない。

```sh
python scripts/gen_toeic.py 5 --per-level 24            # 下書き(toeic/drafts/)。--focus 関係詞 で苦手分野を厚く
python scripts/crosscheck_toeic.py toeic/drafts/p5-*.json   # 答えを見ずに解かせる
python scripts/merge_toeic.py --drafts toeic/drafts/p5-*.json --checks toeic/drafts/check-*.json
#   → 一致したものは questions_src.json へ、食い違いは review-*.json へ。見直して verified="reviewed" を付けたら
python scripts/merge_toeic.py --reviewed toeic/drafts/review-XXXX.json
python scripts/check_toeic.py                           # 形式と検算記録を確かめて toeic/questions.json を作る
```

- レベル: 600(600点前後の人が7割正解)、730(同じく7割)、860(860点前後の人で5〜6割)。
- 分野は `toeic/taxonomy.py`(例: Part 5 は品詞・動詞の形・準動詞・関係詞・接続詞と前置詞・代名詞・比較・数量・語彙)。
- Gemini の API キーは環境変数 `GEMINI_API_KEY` か gemini-pdf-digest スキルの `api_key.txt` から読む。リポジトリには入れない。
- 通学ドリルでは `toeic` コレクションにパートごとの文書(`p5` など、`list` にセットの配列)として入れる。
  解答の記録は学生本人の `data/users/<id>` に `t_<設問id>_<時刻>` として保存し、推定スコアと分野別の正答率を出す。

## ファイル構成

```
problem_bank/
  core.py          TeX 整形・有効数字・数値比較・問題の型の登録
  series_tools.py  級数の収束を数値で判定する検算用ツール
  kaiseki.py       解析学の問題の型と出題リスト
  bisekibun2.py    微積第二の問題の型と出題リスト
  butsuri2.py      物理学概論第二の問題の型と出題リスト
  bank.py          全科目をまとめて id・order・単元を振る(類題も含む)
scripts/
  build.py         JSON を再生成する
  verify.py        検証する
  make_variants.py ×・△の問題から検算つきの類題を作る
  check_words.py   TOEIC 単語リストを検証して toeic/words.json を作る
  gen_toeic.py / crosscheck_toeic.py / merge_toeic.py / check_toeic.py   TOEIC 問題の下書き・検算・取り込み・検証
toeic/
  words_src.py     単語リストの元データ
  words.json       検証済みの単語リスト(ドリルに入れるもの)
output/
  problems.json    ドリルに取り込む問題
  params.json      検算用のパラメータ
```

問題を増やすときは、各科目モジュールに `@kind(...)` で型(問題を作る関数と検算する関数の組)を足し、
`specs()` に出題を追加してから `build.py` → `verify.py` の順に実行する。
