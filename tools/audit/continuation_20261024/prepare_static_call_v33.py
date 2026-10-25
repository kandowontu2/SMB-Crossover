from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'build_mmc3_static_call_v31.py').read_text();t=t.replace("O=D/'mmc3-static-call-v31'","O=D/'mmc3-static-call-v33'")
begin=t.index('import re\ncfg=');end=t.index("text=(V/'source/src/megaman_weapons.s')",begin)
replacement='''# Append after the unchanged original Gradius driver, in its actual FF tail.
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load
parent_bundle=load(V/'candidate.nes');parent=parent_bundle['raw'];g=next(g for g in parent_bundle['segs'].values()if g.get('name')=='"VIC_NATIVE_AUDIO"');tail=int(g['ooffs'],0)+int(g['size'],0);bank=(tail-16)//8192
assert bank==253 and (tail-16)%8192+96<=8192 and parent[tail:tail+96]==bytes([255])*96
add('smb1base-mmc3-oversized.cfg','    VECTORS:    load = PRGFix, type = ro,  start = $fffa;','    M3_CELL_RESET: load=M3_FREE_FD,type=ro; # Append after native audio; preserve its original bytes.\\n    VECTORS:    load = PRGFix, type = ro,  start = $fffa;')
'''
t=t[:begin]+replacement+t[end:];(D/'build_mmc3_static_call_v33.py').write_text(t)
