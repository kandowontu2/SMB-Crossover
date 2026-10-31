"""Keep all strict assertions on the genuine service17+lives-palette successor."""
from pathlib import Path
P=Path(__file__).with_name('ff_cold_preview_controls_v1.py');s=P.read_text()
s=s.replace("build/ff-cold-preview-v3","build/ff-cold-preview-v5").replace("controls-v1.json","controls-v2.json")
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
