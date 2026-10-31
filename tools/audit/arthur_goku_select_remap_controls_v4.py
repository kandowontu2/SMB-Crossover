"""Compare exact native VRAM streams at complete Select for allflags.

The old convenience name parser handles literal packets only and faulted
on a native stream format during the expanded full-caller flag test. Exact
offset and full84B region comparison includes every byte and terminator;
the separate actual80-name assertions remain unchanged.
"""
from pathlib import Path
p=Path(__file__).with_name('arthur_goku_select_remap_controls_v3.py')
t=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'')
ns={'__file__':str(p)};exec(compile(t,str(p),'exec'),ns);s=ns['s']
s=s.replace("out=O/'menu-controls-v3.json'","out=O/'menu-controls-v4.json'")
s=s.replace("assert A.commands(mm[0])==A.commands(mm[1]),('foreign real menu packet',slot,variant,p)","""assert mm[0].get('VRAM_Buffer1_Offset')==mm[1].get('VRAM_Buffer1_Offset')
     streams=[bytes(m.ram[m.lab['VRAM_Buffer1']:m.lab['VRAM_Buffer1']+84])for m in mm]
     assert streams[0]==streams[1],('exact foreign full VRAM region',slot,variant,p,streams)""")
exec(compile(s,__file__,'exec'),globals())
