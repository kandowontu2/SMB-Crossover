from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'build_mmc3_static_call_v28.py').read_text();t=t.replace("O=D/'mmc3-static-call-v28'","O=D/'mmc3-static-call-v29'")
old="old=(V/'source/src/mmc3.s').read_text();old=old[old.index('.segment \"SMCCODE\"'):]"
new="old=(V/'source/src/mmc3.s').read_text();begin=old.index('.segment \"SMCCODE\"');end=old.index('\\n  rts',begin)+len('\\n  rts\\n');old=old[begin:end]"
assert t.count(old)==1;t=t.replace(old,new);(D/'build_mmc3_static_call_v29.py').write_text(t)
