"""Existing exact FF lives consumers rebound to the disjoint joint cart."""
from pathlib import Path
P=Path(__file__).with_name('ff_lives_body_palette_controls_v1.py')
s=P.read_text(encoding='utf-8').replace("build/ff-lives-body-palette-v1","build/coherent62-lives-fixes-v1")
s=s.replace("out=O/'controls.json'","out=O/'ff-controls.json'")
s=s.replace("c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=flags);states=[]", "c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=flags);smc=bytes(m[0x15a:0x17b]);states=[]")
s=s.replace('(1,1,30,flags&0xcf,224)','(1,1,30,flags&0x4d,224)')
s=s.replace("assert m.rawtags==maps and bytes(m[0x15a:0x17b])==smc", "assert m.rawtags==maps\n  changed=[0x15a+i for i,(a,z)in enumerate(zip(smc,m[0x15a:0x17b]))if a!=z]\n  assert all(a in [address(b,'NextBank_SMC')+1,address(b,'SafereturnA_SMC')+1]for a in changed),('exact genuine foreground SFC volatile operands',changed)")
s=s.replace('valid=valid,pc=pc,kind=kind,lag=lag,**z','valid=valid,pc=pc,lag=lag,**z')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
