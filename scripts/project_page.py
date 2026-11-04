"""Print the project page (index.html): links, every project file, and README.md rendered.
Run by scripts/publish_web.sh:  python3 project_page.py README.md <files dir>"""
import html, json, pathlib, sys

readme = pathlib.Path(sys.argv[1]).read_text()
files_dir = pathlib.Path(sys.argv[2])
files = sorted(p.relative_to(files_dir).as_posix() for p in files_dir.rglob("*") if p.is_file())
rows = "\n".join(
    f'<li><a href="files/{html.escape(f)}" download>{html.escape(f)}</a> '
    f'<span class="size">({(files_dir / f).stat().st_size / 1024:,.1f} KB)</span></li>' for f in files
)
print(f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dummy Arm Watch</title>
<style>
:root {{ --bg:#fff; --fg:#1a1a1a; --muted:#666; --card:#f5f5f2; --line:#ddd; --accent:#F5C518; --link:#1f5fa8; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141414; --fg:#eee; --muted:#aaa; --card:#1f1f1f; --line:#333; --link:#7fb0ea; }} }}
body {{ background:var(--bg); color:var(--fg); font-family:system-ui,-apple-system,"Segoe UI",Arial,sans-serif; line-height:1.6; margin:0; }}
main {{ max-width:860px; margin:0 auto; padding:24px 16px 64px; }}
a {{ color:var(--link); }}
.hero {{ border-right:6px solid var(--accent); padding-right:14px; margin-bottom:24px; }}
.hero h1 {{ margin:0; font-size:2rem; }} .hero p {{ margin:4px 0; color:var(--muted); }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin:20px 0 28px; }}
.card {{ display:block; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; text-decoration:none; color:var(--fg); }}
.card b {{ display:block; font-size:1.1rem; }} .card span {{ color:var(--muted); font-size:.9rem; }}
.card:hover {{ border-color:var(--accent); }}
section {{ margin-top:28px; }}
.size {{ color:var(--muted); font-size:.85rem; }}
table {{ border-collapse:collapse; width:100%; display:block; overflow-x:auto; }}
th,td {{ border:1px solid var(--line); padding:6px 8px; text-align:right; vertical-align:top; }}
code,pre {{ background:var(--card); border-radius:4px; direction:ltr; unicode-bidi:embed; }}
code {{ padding:1px 4px; }} pre {{ padding:10px; overflow-x:auto; text-align:left; }}
#readme {{ border-top:2px solid var(--line); margin-top:32px; padding-top:8px; }}
</style>
</head>
<body><main>
<div class="hero">
  <h1>🦾 Dummy Arm Watch</h1>
  <p>קורס "וייב קודינג עם קלוד", אוניברסיטת אריאל, סמסטר א' תשפ"ז · אבן דרך M1 · איתן ג'וסף (הנדסת חשמל)</p>
</div>
<div class="cards">
  <a class="card" href="app/"><b>▶ האפליקציה</b><span>רצה בדפדפן, בלי התקנה (טעינה ראשונה כ-20 שניות)</span></a>
  <a class="card" href="https://my-dummy-robot.vercel.app"><b>🤖 מודל התלת-מימד</b><span>הרובוט Dummy: חקירה, בנייה ב-39 שלבים, תנועה</span></a>
  <a class="card" href="#readme"><b>📄 README.md</b><span>הגדרת הפרויקט המלאה (למטה בעמוד)</span></a>
  <a class="card" href="files/dummy-arm-watch.zip" download><b>⬇ כל קבצי הפרויקט (zip)</b><span>README, app.py, CLAUDE.md, requirements.txt, .gitignore, data/</span></a>
</div>
<section>
  <h2>קבצי הפרויקט</h2>
  <ul>{rows}</ul>
  <p class="size">הרצה מקומית: <code>pip install -r requirements.txt</code> ואז <code>streamlit run app.py</code></p>
</section>
<article id="readme"></article>
</main>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script>
const md = {json.dumps(readme, ensure_ascii=False)};
const el = document.getElementById("readme");
try {{
  el.innerHTML = marked.parse(md);
  el.querySelectorAll("a[href]").forEach(a => {{
    const h = a.getAttribute("href");
    if (!/^(https?:|#|mailto:)/.test(h)) a.setAttribute("href", "files/" + h.replace(/^\\.\\//, ""));
  }});
}} catch (e) {{ el.innerHTML = "<pre></pre>"; el.firstChild.textContent = md; }}
</script>
</body></html>""")
