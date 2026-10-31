"""Same original-source/controller tests on actual left-latch source repair."""
from pathlib import Path
P=Path(__file__).with_name('bowser_source_core_controls_v3.py')
s=P.read_text(encoding='utf-8').replace('bowser-source-core-v2','bowser-source-core-v3').replace('controls-v3.json','controls-v4.json')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
