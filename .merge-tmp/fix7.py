import io
p = ".merge-tmp/patch_trunk2.py"
s = io.open(p, encoding="utf-8").read()
start = s.index("# 7. Capture form")
end = s.index("# 8. Disclosure")
new = (
"# 7. Capture form: the trunk already made it non-submitting; close the no-JS path too\n"
'sub(\'<input id="email" name="email" type="email" autocomplete="email" placeholder="you@example.com">\',\n'
'    \'<input id="email" type="email" autocomplete="email" placeholder="you@example.com">\',\n'
'    "7 capture: no name attribute, so a script-blocked submit carries nothing")\n'
'sub(\'</form>\\n<script>\',\n'
'    \'</form>\\n<p class="meta">The field deliberately has no <code>name</code> attribute: with scripting switched off there is no key/value pair for a browser to put into a URL, so an address cannot reach a server request log even in the fallback path.</p>\\n<script>\',\n'
'    "7 capture: fallback note")\n\n'
)
s = s[:start] + new + s[end:]
# kicker: match whatever the trunk emits
s = s.replace('''sub('<span class="kicker">Countertop cooking · Season: {esc(lead.get(\\'season\\') or current_season())}</span>',
    '<span class="kicker">Editor’s pick · Countertop cooking · Season: {esc(lead.get(\\'season\\') or current_season())}</span>',
    "3 kicker marks the pick")''',
'''_k = re.search(r'<span class="kicker">([^<]*Season: \\{esc\\(lead[^<]*)</span>', s)
if _k:
    _v = _k.group(1)
    s = s.replace(_k.group(0), '<span class="kicker">Editor\\u2019s pick · ' + _v + '</span>', 1)
    done.append("3 kicker marks the pick")
else:
    miss.append("3 kicker (trunk markup changed; skipped deliberately)")''')
io.open(p, "w", encoding="utf-8").write(s)
print("patch script fixed")
