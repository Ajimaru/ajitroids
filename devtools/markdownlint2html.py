import os
import re
from pathlib import Path

LOG_PATH = Path("markdownlint-report/report.log")
HTML_PATH = Path("markdownlint-report/report.html")

def parse_log(log_path):
    issues = []
    if not log_path.exists():
        return issues
    with log_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"(.+?):(\d+) (MD\d+)/(.*?) (.+)", line)
            if match:
                filename, lineno, rule, rule_name, desc = match.groups()
                issues.append({
                    "file": filename,
                    "line": lineno,
                    "rule": rule,
                    "rule_name": rule_name,
                    "desc": desc
                })
    return issues

def render_html(issues):
    log_file = LOG_PATH
    timestamp = ""
    if log_file.exists():
        ts = log_file.stat().st_mtime
        import datetime
        timestamp = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    html = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<title>Markdownlint Report</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; background: #f8f8f8; color: #222; }",
        "h1 { color: #0057b8; display: inline-block; }",
        ".timestamp { float: right; color: #666; font-size: 1em; margin-top: 18px; }",
        ".file { margin-top: 2em; font-weight: bold; color: #333; cursor: pointer; }",
        "table { border-collapse: collapse; width: 100%; background: #fff; table-layout: fixed; }",
        "th, td { border: 1px solid #ccc; padding: 6px 10px; }",
        "th { background: #e0e7ef; }",
        ".line { color: #0057b8; width: 60px; text-align: right; word-break: keep-all; }",
        ".rule { color: #b80000; font-weight: bold; width: 140px; word-break: break-word; }",
        ".desc { color: #444; width: auto; }",
        "td.desc { width: auto; overflow-wrap: break-word; }",
        "tr { vertical-align: top; }",
        ".toggle-btn { margin: 0 8px; padding: 2px 8px; background: #e0e7ef; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; }",
        "</style>",
        "<script>",
        "function toggleTable(id) {",
        "  var el = document.getElementById(id);",
        "  if (el.style.display === 'none') { el.style.display = ''; } else { el.style.display = 'none'; }",
        "}",
        "function expandAll() {",
        "  document.querySelectorAll('.toggle-table').forEach(function(el){ el.style.display = ''; });",
        "}",
        "function collapseAll() {",
        "  document.querySelectorAll('.toggle-table').forEach(function(el){ el.style.display = 'none'; });",
        "}",
        "</script>",
        "</head>",
        "<body>",
        f"<h1>Markdownlint Report</h1><span class='timestamp'>creating time : {timestamp}</span>",
        "<div style='margin-top:10px;'>",
        "<button class='toggle-btn' onclick='expandAll()'>Alle aufklappen</button>",
        "<button class='toggle-btn' onclick='collapseAll()'>Alle zuklappen</button>",
        "</div>"
    ]
    if not issues:
        html.append("<p>No issues found.</p>")
    else:
        files = {}
        for issue in issues:
            files.setdefault(issue["file"], []).append(issue)
        for idx, (file, file_issues) in enumerate(files.items()):
            table_id = f"table_{idx}"
            html.append(f"<div class='file' onclick=\"toggleTable('{table_id}')\">{file}</div>")
            html.append(f"<div id='{table_id}' class='toggle-table' style='display:none;'>")
            html.append("<table>")
            html.append("<colgroup><col style='width:60px;'><col style='width:140px;'><col style='width:auto;'></colgroup>")
            html.append("<tr><th>Line</th><th>Rule</th><th>Description</th></tr>")
            for issue in file_issues:
                rule_url = f"https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md#{issue['rule'].lower()}"
                rule_title = f"{issue['rule']} – {issue['rule_name']}"
                html.append(
                    f"<tr>"
                    f"<td class='line'>{issue['line']}</td>"
                    f"<td class='rule'>"
                    f"<a href='{rule_url}' target='_blank' rel='noopener' title='{rule_title}'>{issue['rule']}</a>"
                    f"<br><small>{issue['rule_name']}</small>"
                    f"</td>"
                    f"<td class='desc'>{issue['desc']}</td>"
                    f"</tr>"
                )
            html.append("</table>")
            html.append("</div>")
    html.append("</body></html>")
    return "\n".join(html)

def main():
    issues = parse_log(LOG_PATH)
    html = render_html(issues)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HTML_PATH.open("w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report written to {HTML_PATH}")

if __name__ == "__main__":
    main()