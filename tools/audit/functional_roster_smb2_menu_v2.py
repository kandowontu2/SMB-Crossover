"""Retain v1's old newly-ready-Quick-only fixture assumption as negative.

Quick is already ready in both current inputs, so both correctly retain bit20
at Start. Their actual full launch registers remain compared identically.
"""
from pathlib import Path
p=Path(__file__).with_name('functional_roster_smb2_menu_v1.py');text=p.read_text()
text=text.replace("B.O/'menu-controls'","B.O/'menu-controls-v2'")
anchor="exec(compile(s,__file__,'exec'),A.__dict__)";assert text.count(anchor)==1
text=text.replace(anchor,"s=s.replace(\"pair[0].get('FmAlts')==pair[1].get('FmAlts')==0 or pending[0]\",\"pair[0].get('FmAlts')==pair[1].get('FmAlts')==(32 if slot==9 and variant==2 else 0) or pending[0]\")\n"+anchor)
exec(compile(text,__file__,'exec'),globals())
