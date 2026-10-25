from pathlib import Path
D=Path(__file__).resolve().parent
t=(D/'qualify_mmc3_ship_entries_v25.py').read_text();t=t.replace("O=D/'mmc3-ship-lives-v25'","O=D/'mmc3-sophia-stack-v27'")
anchor="report=dict(complete=False"
insert="""import sys
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address
bundle=load(ROM);sg=next(g for g in bundle['segs'].values()if g.get('name')=='"SMCCODE"');start,size,pos=(int(sg[k],0)for k in('start','size','ooffs'));mutable={address(bundle,n)+1:True for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']};mutable[address(bundle,'FarcallJmpTarget_SMC')+2]=True
full='ROSTER_CONFIG={out=OUTPUT}\\nFULL_SMC_GUARD='+im.lua(dict(start=start,bytes=list(bundle['raw'][pos:pos+size]),mutable=mutable))+'\\n'+(D/'mmc3_full_smc_guard_v1.lua').read_text()+'\\n'
"""
assert t.count(anchor)==1;t=t.replace(anchor,insert+anchor);assert t.count("script.write_text(text)")==1;t=t.replace('script.write_text(text)','script.write_text(full+text)');(D/'qualify_mmc3_entries_v27.py').write_text(t)
