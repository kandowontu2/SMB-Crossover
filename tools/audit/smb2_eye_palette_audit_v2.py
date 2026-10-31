"""Repeat native area donors through genuine selected25 constructor ingress."""
from pathlib import Path
P=Path(__file__).with_name('smb2_eye_palette_audit_v1.py');s=P.read_text()
s=s.replace('build/smb2-eye-role-audit-v1','build/smb2-eye-role-audit-v2')
a="m=fresh(0);M.put(m,AreaType=area);C.invoke(m,'GetAreaPalette');A.interrupt(m,0)"
b="m=fresh(0);C.invoke(m,'MenuResolveCharacter');assert m.get('SelectedCharacter')==25 and m.get('S2Ready')==178;M.put(m,AreaType=area);C.invoke(m,'GetAreaPalette');A.interrupt(m,0)"
assert s.count(a)==1;s=s.replace(a,b)
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
