"""Preserve only the five small historical inputs needed by the bbox recipe."""
import hashlib,json,shutil,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/shinobi-bbox-source-freeze-1101-v30'
D=R/'docs/qa/checkpoints/2026-11-01/shinobi-bbox-source-v30'
INPUTS=['shinobi-menu-1101-v13/resident.s','shinobi-menu-1101-v13/shinobi_damage_1101_v10.inc','shinobi-chr-owner-1101-v18/owner.s','shinobi-hurt-layout-1101-v5/component.lbl','shinobi-hurt-layout-1101-v5/pose-packets.json']
def main():
 O.mkdir(exist_ok=True);D.mkdir(parents=True,exist_ok=True);rows=[]
 with zipfile.ZipFile(O/'inputs.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for name in INPUTS:
   p=R/'build'/name;data=p.read_bytes();assert len(data)<60_000
   rows.append(dict(path='build/'+name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()));z.writestr(name,data)
 assert len(rows)==5 and sum(r['bytes']for r in rows)<75_000
 with zipfile.ZipFile(O/'inputs.zip')as z:
  for row in rows:assert hashlib.sha256(z.read(row['path'][6:])).hexdigest()==row['sha256']
 q=dict(passed=True,source_only=True,ROM_included=False,files=rows,archive_sha256=sha(O/'inputs.zip'),scope='Five exact retained source/label/pose inputs, no historical dependency tree or ROM. Rebuild bbox proposal with committed tools/reference includes and current ROM preimage; restore these exact small inputs on demand if build cleanup removes them.')
 (O/'manifest.json').write_text(json.dumps(q,indent=2)+'\n')
 for name in ['inputs.zip','manifest.json']:shutil.copyfile(O/name,D/name)
 print(json.dumps(dict(passed=True,files=5,source_bytes=sum(r['bytes']for r in rows),archive_bytes=(D/'inputs.zip').stat().st_size,checkpoint=str(D.relative_to(R)))))
if __name__=='__main__':main()
