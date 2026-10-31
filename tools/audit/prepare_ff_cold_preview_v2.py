"""Export the genuine native DrawMetasprite symbol; no absolute fixture alias."""
from pathlib import Path
P=Path(__file__).with_name('prepare_ff_cold_preview_v1.py');s=P.read_text()
s=s.replace("O=R/'build/ff-cold-preview-v1'","O=R/'build/ff-cold-preview-v2'")
s=s.replace("p=J/'loader.s';old=p.read_text();s=old", "p=J/'entrypoint.s';write(p,p.read_text()+'\\n.export DrawMetasprite\\n')\n p=J/'loader.s';old=p.read_text();s=old")
s=s.replace("for n in['loader','veneers']:","for n in['main','loader','veneers']:")
s=s.replace("n in['loader.o','veneers.o','private.cfg'","n in['main.o','loader.o','veneers.o','private.cfg'")
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
