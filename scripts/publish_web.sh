#!/usr/bin/env bash
# Put the app on the web at https://dummy-arm-watch.vercel.app (Vercel project dummy-arm-watch).
# The same app.py runs inside the visitor's browser (stlite = Streamlit on Pyodide), so no server
# is needed and anyone with the link can open it. Run: scripts/publish_web.sh   (needs vercel CLI, logged in)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE="$ROOT/.web-build"
rm -rf "$SITE"; mkdir -p "$SITE/data"
cp "$ROOT/app.py" "$SITE/"
# The browser reads parquet with fastparquet, which breaks on the dot in "observation.state":
# the web copies name it "observation_state" (app.py renames it back).
"$ROOT/.venv/bin/python" - "$ROOT/data" "$SITE/data" <<'PY'
import sys, pathlib, pyarrow.parquet as pq
src, dst = map(pathlib.Path, sys.argv[1:])
for f in src.glob("*.parquet"):
    t = pq.read_table(f)
    pq.write_table(t.rename_columns([c.replace("observation.state", "observation_state") for c in t.column_names]), dst / f.name)
PY
cat > "$SITE/index.html" <<'HTML'
<!doctype html>
<html lang="he">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dummy Arm Watch</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.css" />
</head>
<body>
  <div id="root"></div>
  <script type="module">
    import { mount } from "https://cdn.jsdelivr.net/npm/@stlite/browser@1.11.0/build/stlite.js";
    mount({
      requirements: ["pandas", "fastparquet"],
      entrypoint: "app.py",
      files: {
        "app.py": { url: "app.py" },
        "data/dummy_sim_point.parquet": { url: "data/dummy_sim_point.parquet" },
        "data/so101_pickplace.parquet": { url: "data/so101_pickplace.parquet" },
      },
    }, document.getElementById("root"));
  </script>
</body>
</html>
HTML
vercel deploy --prod --yes --project dummy-arm-watch --cwd "$SITE" "$@"
