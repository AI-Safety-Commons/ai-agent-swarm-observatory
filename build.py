"""Build the public static dashboard from the committed aggregate dataset."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "visualizations"
data = (SOURCE / "chart-data.json").read_text(encoding="utf-8")
parsed = json.loads(data)
totals = [sum(row[5] for row in parsed["rows"] if row[2] == i) for i in range(4)]
assert totals == [14591, 5217, 101, 4], totals
assert sum(row[3] for row in parsed["recreations"]) == 68
for char, escape in [("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026")]:
    data = data.replace(char, escape)
template = (SOURCE / "wiki-activity.template.html").read_text(encoding="utf-8")
assert template.count("__CHART_DATA__") == 1
fragment = template.replace("__CHART_DATA__", data)
# Keep the original inline preview usable, with the same theme as the public page.
fragment = "<style>\n" + (SOURCE / "dashboard.css").read_text() + "\n</style>\n" + fragment
assert len(fragment.encode("utf-8")) < 1_000_000
(SOURCE / "wiki-activity.html").write_text(fragment, encoding="utf-8")
subprocess.run([sys.executable, str(SOURCE / "package_dashboard.py"), "--output", str(ROOT / "index.html")], check=True)
shutil.copyfile(ROOT / "index.html", ROOT / "wiki-activity-dashboard.html")
print("Build complete: index.html (also copied to wiki-activity-dashboard.html)")
