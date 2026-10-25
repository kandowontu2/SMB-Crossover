from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'check_mmc3_static_layout_v39.py').read_text(encoding='utf-8')
s=s.replace("O=V/'layout-v1'","O=V/'layout-v2'")
old="g.get('type')=='rw'and v<0x8000"
new="g.get('type')=='rw'and g.get('name')!='\"SMCCODE\"'and v<0x8000"
assert s.count(old)==1
s=s.replace(old,new)
exec(compile(s,str(D/'check_mmc3_static_layout_v39.py'),'exec'),globals())
