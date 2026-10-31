"""Compare the true relocated FmNames pointer, not old absolute scratch bytes.

v2 retained a genuine changed R2/R3 name-table address after complete Select.
Only this exact pointer pair is normalized by its own linked FmNames base;
all other ZP, actual emitted16B packets and caller AXYP remain strict.
"""
from pathlib import Path
p=Path(__file__).with_name('arthur_goku_select_remap_controls_v2.py')
t=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'')
ns={'__file__':str(p)};exec(compile(t,str(p),'exec'),ns);s=ns['s']
s=s.replace("out=O/'menu-controls-v2.json'","out=O/'menu-controls-v3.json'")
s=s.replace("assert mm[0].ram[:0x100]==mm[1].ram[:0x100],('complete menu ZP',slot,variant,p)","""diff=[i for i in range(256)if mm[0].ram[i]!=mm[1].ram[i]]
     if diff:
      assert set(diff)<=set([mm[0].lab['R2'],mm[0].lab['R3']]),('other complete menu ZP',slot,variant,p,diff)
      rel=[m.get('R2')+256*m.get('R3')-m.lab['FmNames']for m in mm]
      assert rel[0]==rel[1]and 0<=rel[0]<33*16,('exact linked name pointer',slot,variant,p,rel)""")
exec(compile(s,__file__,'exec'),globals())
