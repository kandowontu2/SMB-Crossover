"""Finish D's retained host adapter failure without repeating passed math."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert json.loads((D/'compiled-axis-c.json').read_text())['status'].startswith('PASS')
    original=R/'tools/audit/check_easy49_sophia_terrain_ig.py'
    text=original.read_text().replace("V/'root49-sophia-source-body-hs/source/build'","V/'root49-combined-working-c/source/build'")
    text=text.replace("'compiled-ig.json'","'compiled-original96-d.json'")
    ns={'__file__':str(original),'__name__':'original96_d_current_parent'}
    exec(compile(text,str(original),'exec'),ns);ns['D']=D;ns['main']()
    parent=R/'tools/audit/check_easy49_sophia_head_axis_c.py';text=parent.read_text()
    a="    ns['main']()";assert text.count(a)==1
    text=text.replace(a,"    assert json.loads((D/'compiled-axis-c.json').read_text())['status'].startswith('PASS')")
    a='    mod.main()';assert text.count(a)==1
    text=text.replace(a,"    assert json.loads((D/'compiled-original96-d.json').read_text())['status'].startswith('PASS')")
    text=text.replace("sha(D/'compiled-ig.json')","sha(D/'compiled-original96-d.json')")
    ns={'__file__':str(parent),'__name__':'split_ceiling_d'}
    exec(compile(text,str(parent),'exec'),ns);ns['D']=D;ns['main']()
    (D/'host-completion-e.json').write_text(json.dumps(dict(status='PASS_D_ORIGINAL96_AND_SPLIT_CEILING_WITH_MATH_REUSED',
        script_sha256=sha(__file__),retained_host_negative_sha256=sha(D/'compiled-host-d.log'),
        mathematical_oracle=sha(D/'compiled-axis-c.json'),origin=sha(D/'origin-and-query-d.json'),
        original96=sha(D/'compiled-original96-d.json'),head_span=sha(D/'complete-head-span-c.json')) ,indent=2)+'\n')


if __name__=='__main__':main()
