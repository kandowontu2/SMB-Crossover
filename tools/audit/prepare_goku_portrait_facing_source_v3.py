"""Use cc65's workspace-relative genuine include path; retain v2 compile failure."""
from pathlib import Path
p=Path(__file__).with_name('prepare_goku_portrait_facing_source_v2.py');ns={'__file__':str(p),'__name__':'prepare_only'}
s=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'')
exec(compile(s,str(p),'exec'),ns)
s=ns['s'].replace('goku-portrait-facing-source-v2','goku-portrait-facing-source-v3')
s=s.replace("(O/'admission.inc').as_posix()+'\"'","(O/'admission.inc').relative_to(R).as_posix()+'\"'")
exec(compile(s,__file__,'exec'),globals())
