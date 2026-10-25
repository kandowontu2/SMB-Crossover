from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'build/verification/bill-green-native-i';P=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=(O/'trace.csv').read_bytes();b=b''.join((P/'trace.csv').read_bytes().splitlines(keepends=True)[:15001]);assert a==b
result=json.loads((O/'result.json').read_text());assert result['frames']==15000 and result['failure']=='frame limit'
def rows(p):
 with p.open(newline='')as f:return list(csv.DictReader(f))
changed=[];last=None
for z in rows(O/'attributes.csv'):
 aa=bytes.fromhex(z['attributes']);target=tuple(aa[n]for n in [11,19,27,35,43,51,59])
 if target!=last:changed.append(dict(frame=int(z['frame']),camera=int(z['camera']),column3_attributes=list(target)));last=target
summary=dict(rom_sha256=sha(P/'smb-crossover-mmc3.nes'),input_sha256=sha(P/'inputs.csv'),exit=1,result=result,trace_literal_to_movie_prefix=True,trace_sha256=sha(O/'trace.csv'),initial_assertion_negative='I compared actual CRLF bytes to a reference that its own expression had normalized to LF. J compares the untouched CRLF byte prefix; all 15000 rows and cycle counts are literally identical. No emulator rerun or evidence rewrite.',native_observation='Read-only power-on fixed-controller replay; frame-limit stop is expected and is not a clear.',attribute_column3_changes=changed)
(O/'summary-j.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))
