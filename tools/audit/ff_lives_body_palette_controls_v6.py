"""Remove duplicate report-only kind key; all source assertions unchanged."""
from pathlib import Path
P=Path(__file__).with_name('ff_lives_body_palette_controls_v5.py')
s=P.read_text(encoding='utf-8').replace("controls-v5.json","controls-v6.json")
s=s.replace("exec(compile(s,str(P),'exec'),", "s=s.replace('valid=valid,pc=pc,kind=kind,lag=lag,**z','valid=valid,pc=pc,lag=lag,**z')\nexec(compile(s,str(P),'exec'),")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
