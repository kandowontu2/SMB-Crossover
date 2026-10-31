"""Fix actual left-control flags hazard after variant LDX in NEW source."""
from pathlib import Path
P=Path(__file__).with_name('prepare_bowser_source_core_v2.py')
s=P.read_text(encoding='utf-8').replace('bowser-source-core-v2','bowser-source-core-v3')
s=s.replace("exec(compile(s,str(P),'exec'),","s=s.replace(' bne SetX',' jmp SetX')\nexec(compile(s,str(P),'exec'),")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
