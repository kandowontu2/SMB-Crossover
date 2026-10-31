"""Model native final LDA#1 NZ while preserving all live CVDI flags."""
from pathlib import Path
P=Path(__file__).with_name('ff_lives_body_palette_controls_v3.py')
s=P.read_text(encoding='utf-8').replace('controls-v3.json','controls-v4.json')
s=s.replace("s=s.replace(\"a==address", "s=s.replace(\"a==address")
# Apply this correction to the v1 producer after the inherited transformations.
needle="exec(compile(s,str(P),'exec'),"
s=s.replace(needle,"s=s.replace('(1,1,30,flags&0xcf,224)','(1,1,30,flags&0x4d,224)')\n"+needle)
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
