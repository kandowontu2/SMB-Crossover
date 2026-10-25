"""Keep the initial cut and remove the shortest-stream truncation on a successor."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
source=(R/'tools/audit/encode_bill_showcase_ac.py').read_text(encoding='utf-8')
old="O=R/'Playthrough Videos/Showcases';assert not O.exists();O.mkdir()"
new="O=R/'Playthrough Videos/Showcases/Verified';assert not O.exists();O.mkdir()"
assert source.count(old)==1;source=source.replace(old,new)
old="'-c:a','pcm_s16le','-t',str((2999-start)/float(fps)),'-shortest',str(master)"
new="'-c:a','pcm_s16le',str(master)"
assert source.count(old)==1;source=source.replace(old,new)
O=R/'build/verification/bill-easy-showcase-ad';assert not O.exists();O.mkdir()
(O/'executed-source.py.txt').write_text(source,encoding='utf-8')
exec(compile(source,str(R/'tools/audit/encode_bill_showcase_ac.py'),'exec'),{'__name__':'__main__','__file__':str(R/'tools/audit/encode_bill_showcase_ac.py')})
