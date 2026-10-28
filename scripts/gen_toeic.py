"""Gemini に TOEIC 形式の問題の下書きを作らせ、toeic/drafts/ に保存する。

使い方:
  python scripts/gen_toeic.py 5 --per-level 24          # Part 5 を各レベル24題
  python scripts/gen_toeic.py 6 --per-level 2           # Part 6 を各レベル2セット(1セット4問)
  python scripts/gen_toeic.py 5 --per-level 6 --focus 関係詞 --focus 準動詞   # 苦手分野を厚く
下書きはそのまま使わない。scripts/crosscheck_toeic.py で別のモデルに答えを見ずに解かせ、
食い違った問題を人(Claude)が見直してから scripts/check_toeic.py に通す。
"""
import argparse
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "toeic"))

from gemini import generate_json  # noqa: E402
from taxonomy import LEVELS, N_CHOICES, SKILLS  # noqa: E402

COMMON = """You are writing ORIGINAL practice questions in the style of the TOEIC Listening & Reading test for a Japanese university student.
Rules:
- Everything must be newly written. Do not copy or closely paraphrase official ETS questions or commercial textbooks.
- Business/everyday workplace settings typical of TOEIC (offices, stores, travel, events, hiring, shipping, facilities).
- EXACTLY ONE choice must be correct. Distractors must be clearly wrong for a careful test-taker (grammatically impossible, contradicted by the text, or not answering the question), but plausible-looking.
- Vary which choice is correct (answer index spread over all positions).
- "explain" is in natural Japanese (2-3 sentences): why the answer is right and why the tempting distractor is wrong. Quote the key English words.
- "skill" must be one of the listed skills, written exactly.
- Level meanings: """ + "; ".join(f"{k}: {v}" for k, v in LEVELS.items()) + """
Output ONLY JSON: an array of item objects as specified below. No markdown."""

PART = {
    5: """Part 5 (incomplete sentences). Each item = one sentence with one blank written as "____".
Item: {"part":5,"level":<600|730|860>,"questions":[{"q":"sentence with ____","choices":[4 words/phrases],"answer":<0-3>,"skill":"<skill>","explain":"..."}]}
Skills: SKILLS. For grammar skills, the four choices should usually be forms of the same word or same category (e.g. relate/related/relating/relation). For 語彙, four different words of the same part of speech.""",
    6: """Part 6 (text completion). Each item = one short business text (email, memo, notice, article; 90-140 words) with 4 blanks written as [1], [2], [3], [4] in order. Exactly one blank is a sentence-insertion blank (skill 文挿入) whose choices are 4 full sentences; the others are word/phrase blanks.
Item: {"part":6,"level":...,"passage":{"type":"<email|memo|notice|article|letter>","title":"short heading","text":"... [1] ... [2] ..."},"questions":[{"q":"[1]","choices":[...],"answer":..,"skill":"..","explain":".."}, ... 4 questions for [1]..[4]]}
Skills: SKILLS.""",
    7: """Part 7 (reading comprehension). Each item = one text (email, notice, advertisement, article, text-message chat with names and times; 100-180 words) with 2 or 3 questions.
Item: {"part":7,"level":...,"passage":{"type":"<email|notice|advertisement|article|chat|form>","title":"short heading","text":"..."},"questions":[{"q":"What is the purpose of the e-mail?","choices":[4 options],"answer":..,"skill":"..","explain":".."}]}
For 語句の意味 use the TOEIC wording: 'The word "X" in paragraph 1, line 2, is closest in meaning to'. For 文挿入, mark positions [1]-[4] in the text and ask 'In which of the positions marked [1], [2], [3], and [4] does the following sentence best belong? "..."' with choices "[1]".."[4]".
Skills: SKILLS.""",
    2: """Part 2 (question-response, listening). Each item = one spoken question or statement by one speaker and THREE spoken responses (A)(B)(C) by another speaker. Nothing is printed on the test page; the student only hears them.
Item: {"part":2,"level":...,"script":[{"sp":"W","t":"question or statement"}],"questions":[{"q":"","choices":[3 response sentences],"answer":<0-2>,"skill":"..","explain":".."}]}
Use "M" or "W" for speakers. Typical traps: similar-sounding words, answering a different WH-word, repeating a word from the question. The correct answer may be indirect (e.g. "I just got here myself.").
Skills: SKILLS.""",
    3: """Part 3 (conversations, listening). Each item = one conversation of 6-9 turns between 2 (sometimes 3) speakers, 100-150 words, and THREE printed questions with 4 printed choices each. Include one question of skill 発言の意図 in about half of the items, quoting a phrase: 'What does the man mean when he says, "..."?'
Item: {"part":3,"level":...,"script":[{"sp":"M","t":"..."},{"sp":"W","t":"..."},...],"questions":[{"q":"...","choices":[4],"answer":..,"skill":"..","explain":".."}, x3]}
Speakers: "M", "W", or "M2"/"W2" for a third person. Skills: SKILLS.""",
    4: """Part 4 (talks, listening). Each item = one short talk by ONE speaker (announcement, voicemail, radio ad, tour guide, meeting excerpt), 100-140 words, and THREE printed questions with 4 printed choices each. Include one 発言の意図 question in about half of the items.
Item: {"part":4,"level":...,"script":[{"sp":"W","t":"the whole talk"}],"questions":[{"q":"...","choices":[4],"answer":..,"skill":"..","explain":".."}, x3]}
Skills: SKILLS.""",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", type=int, choices=sorted(PART))
    ap.add_argument("--per-level", type=int, required=True, help="レベルごとの数(Part 5/2 は問題数、他はセット数)")
    ap.add_argument("--levels", type=int, nargs="*", default=[600, 730, 860])
    ap.add_argument("--focus", action="append", default=[], help="厚くする分野(何度でも)")
    ap.add_argument("--avoid", default="", help="重複を避けたい既存問題の要約を書いたファイル")
    a = ap.parse_args()

    skills = SKILLS[a.part]
    spec = PART[a.part].replace("SKILLS", " / ".join(skills))
    plan = f"Write {a.per_level} items for EACH of these levels: {a.levels} (total {a.per_level * len(a.levels)} items)."
    if a.focus:
        plan += f" Give about half of the questions the skills {a.focus}; spread the rest over the other skills."
    else:
        plan += " Spread questions evenly over all skills."
    avoid = ""
    if a.avoid:
        avoid = "\nAlready used (do not repeat these sentences, topics or answers):\n" + pathlib.Path(a.avoid).read_text(encoding="utf-8")[:20000]
    prompt = f"{COMMON}\n\n{spec}\n\n{plan}{avoid}"
    items, model = generate_json(prompt, temperature=0.8)
    if isinstance(items, dict):
        items = items.get("items") or next(v for v in items.values() if isinstance(v, list))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = ROOT / "toeic" / "drafts" / f"p{a.part}-{stamp}.json"
    out.write_text(json.dumps({"model": model, "part": a.part, "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    nq = sum(len(i.get("questions", [])) for i in items)
    print(f"{len(items)} セット・{nq} 問を {out.relative_to(ROOT)} に保存した(モデル {model}, 選択肢 {N_CHOICES[a.part]} 個)")


if __name__ == "__main__":
    main()
