"""Successor of failed v1: use local procedure byte-count labels."""
from pathlib import Path
P=Path(__file__).with_name('prepare_smb2_eye_sky_v1.py')
s=P.read_text(encoding='utf-8').replace("build/smb2-eye-sky-v1'","build/smb2-eye-sky-v2'")
s=s.replace('helper=\'\'\'.proc S2NativePaletteHeader\n','helper=\'\'\'.proc S2NativePaletteHeader\nOwnStart:\n')
s=s.replace('*-S2NativePaletteHeader','*-OwnStart')
s=s.replace("piece=piece.replace(' cpx #78'","piece=piece.replace('.proc S2MainPalette\\n','.proc S2MainPalette\\nOwnStart:\\n').replace(' cpx #78'")
s=s.replace('*-S2MainPalette=74','*-OwnStart=74')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(P)})
