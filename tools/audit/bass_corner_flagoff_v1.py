"""Rebuild both ordinary targets into one reused private output file."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reference=R/'docs/qa/inventory-timing-adoption-2026-10-26.json'
adopted=json.loads(reference.read_text());assert adopted['ROM_sha256']=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
expected={row['target']:row['ROM_sha256']for row in adopted['fresh_primary_source_builds']}
q=json.loads((B/'bass_corner_working_result.json').read_text());original=q['command'];clean=[];i=0
while i<len(original):
 k=original[i]
 if k=='-g':i+=1;continue
 if k in ['--ld-args','-m','-Ln']:i+=2;continue
 clean.append(k);i+=1
rows=[]
for mapper in ['mmc5','mmc3']:
 cmd=[t.replace(str(B/'bass_corner.cfg'),str(R/'smb1base.cfg')).replace(str(B/'bass_corner_private.nes'),str(B/'bass_corner_flagoff.nes'))for t in clean]
 for i,t in enumerate(cmd):
  if t=='ENABLE_MMC5_EXPANDED=1':cmd[i]='ENABLE_MMC5_EXPANDED=0'
  if t.startswith('MAPPER_MMC5='):cmd[i]='MAPPER_MMC5='+str(int(mapper=='mmc5'))
  if t.startswith('MAPPER_MMC3='):cmd[i]='MAPPER_MMC3='+str(int(mapper=='mmc3'))
 p=subprocess.run(cmd,capture_output=True,text=True);(B/'bass_corner_flagoff.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0,(mapper,p.stderr)
 actual=sha(B/'bass_corner_flagoff.nes');want=expected['ordinary'+mapper.upper()]
 rows.append(dict(mapper=mapper,actual=actual,expected=want,exact=actual==want,command=cmd))
 assert actual==want,(mapper,actual,want)
proof=dict(passed=True,native_run=False,reference=str(reference),reference_sha256=sha(reference),rows=rows,
 source_sha256=sha(__file__),extra_output_trees=0,one_reused_output_file=str(B/'bass_corner_flagoff.nes'))
(B/'bass_corner_flagoff_controls.json').write_text(json.dumps(proof,indent=2)+'\n')
print([(x['mapper'],x['actual'])for x in rows])
