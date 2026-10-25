"""Keep RGB through caption composition; preserve the prior YUV edit."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
s=(R/'build/verification/bill-easy-showcase-ad/executed-source.py.txt').read_text(encoding='utf-8')
old="O=R/'Playthrough Videos/Showcases/Verified'";assert s.count(old)==1;s=s.replace(old,"O=R/'Playthrough Videos/Showcases/Ready'")
assert s.count('overlay=0:0:shortest=1')==3;s=s.replace('overlay=0:0:shortest=1','overlay=0:0:format=rgb:shortest=1')
assert s.count('pad=768:768:0:48:black[v]')==1;s=s.replace('pad=768:768:0:48:black[v]','pad=768:768:0:48:black,format=rgb24[v]')
O=R/'build/verification/bill-easy-showcase-ai';assert not O.exists();O.mkdir();(O/'executed-source.py.txt').write_text(s,encoding='utf-8')
exec(compile(s,str(R/'tools/audit/encode_bill_showcase_ac.py'),'exec'),{'__name__':'__main__','__file__':str(R/'tools/audit/encode_bill_showcase_ac.py')})
