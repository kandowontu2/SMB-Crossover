"""Successor retains v1 annotation-guard false positive; no original source change."""
from pathlib import Path
P=Path(__file__).with_name('reproduce_contra_force_source_v1.py')
s=P.read_text().replace("O=R/'build/contra-force-reproduction-v1'","O=R/'build/contra-force-reproduction-v2'")
s=s.replace("r'^.{12}0x[0-9A-Fa-f]{6}'", "r'^.{12}0x[0-9A-Fa-f]{6}\\s+[0-9A-Fa-f]{2}:[0-9A-Fa-f]{4}:'")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
