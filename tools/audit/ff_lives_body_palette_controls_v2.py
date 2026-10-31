"""Correct foreground SFC setup observation; retain v1 false-assert negative."""
from pathlib import Path
P=Path(__file__).with_name('ff_lives_body_palette_controls_v1.py')
s=P.read_text(encoding='utf-8')
s=s.replace("out=O/'controls.json'", "out=O/'controls-v2.json'")
s=s.replace("c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=flags);states=[]", "c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=flags);smc=bytes(m[0x15a:0x17b]);states=[]")
s=s.replace("assert m.rawtags==maps and bytes(m[0x15a:0x17b])==smc", "assert m.rawtags==maps\n  changed=[0x15a+i for i,(a,z)in enumerate(zip(smc,m[0x15a:0x17b]))if a!=z]\n  assert all(a==address(b,'NextBank_SMC')+1 for a in changed),('foreground SFC changes only genuine bank operand',changed)")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
