"""Use exact constant padding and linked-size assertions for this source leaf.

Ca65 cannot resolve the inherited absolute proc/end expressions while
assembling this multi-segment Main unit; v2 compilation negative retained.
No ROM patch or linked-byte change is used. Actual label-size guards remain.
"""
from pathlib import Path
p=Path(__file__).with_name('prepare_arthur_goku_select_remap_v2.py')
t=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'')
ns={'__file__':str(p)};exec(compile(t,str(p),'exec'),ns);s=ns['s']
s=s.replace('arthur-goku-select-remap-v2','arthur-goku-select-remap-v3')
s=s.replace('.res $ae00-*,$ff','.res 1,$ff')
s=s.replace('.res {pending_size}-(*-FmPending),$ea','.res 7,$ea')
s=s.replace('.res {toggle_size}-(*-FmToggle),$ea','.res 0,$ea')
exec(compile(s,__file__,'exec'),globals())
