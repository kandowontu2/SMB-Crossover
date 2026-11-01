"""Compact freeze of admitted loader bounds; no CHR allocation grant."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-carrier-loader-bounds-1101-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 q=json.loads((O/'loader-bounds.json').read_text())
 assert q['passed'] and not q['carrier_granted']
 assert q['actual_complete_cold_loader_cases']==20 and q['negative_cases']==15
 for p,h in q['bindings'].items():assert sha(p)==h,p
 text='''# High3 forced-blank loader row bounds v5

**Carrier remains ungranted. No ROM/nightly or current host build changed.**
This resolves the five named admitted loader-row bounds left by v4 using the
actual frozen executable and exact indexed source. It does not resolve the
ordinary retained-window/compiled-indirect writer or actual Main/ISR gates.

| Original loader | Real mapper input sequence | Source pages |
|---|---|---|
| QwLoad | QuickManWork_00=0..8 |884..892|
| FwLoad |R1=C0,C4,C8,CC,D0,D4,D8,DC|893..900|
| BwLoad |R1=C0,C4,C8,CC,D0,D4,D8,DC|927..934|
| BtLoad |R1=C0,C4,C8,CC,D0,D4,D8,DC|919..926|
| CfLoaderProposal |R2=0..23|935..958|

All20 complete cold CPU loader runs observed each mapper input exactly twice,
once for copy and once for genuine readback verification. Fixtures cover
legacy/direct prior mappings and PPUCTRL160/164. Every source512B write matches
the expected physical page set; all restore writes avoid1019/1020.

Another15 negative cases cover visible-screen rejection, PRG-RAM protection
and first-row readback corruption for every loader. Each returns failure;
source map calls form only a bounded prefix of the admitted sequence. Visible
rejection performs no source reads or mapper calls. No negative case reaches
the proposed pages.

Tests execute original machine code, real FarCallCommon/nested mapper owners,
buffered PPUDATA and RAM write/readback checks. No copy-loop or map arithmetic
is substituted into the cartridge. Rows and results are aggregated into one
receipt; no ROM, per-frame fixture or dependency tree is copied. Exact original
source paths/hashes are retained in loader-bounds.json.

CPU input: frozen85 f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1.
Carrier design/sources: frozen v3 packet e5f8074e35b2dcdd1388f99aa88408a8e5ed45c7d4bb1fd3774cc230bfc98b8c.
V4 remains frozen unchanged. No current root integration output was read.
The final candidate still needs ordinary-window ownership, every relevant
Main/NMI/IRQ seam and exact integrated source/resource binding before allocation.
'''
 (O/'HANDOFF.md').write_text(text,encoding='utf-8')
 source=[R/'tools/audit/audit_karnov_loader_bounds_1101_v5.py',Path(__file__).resolve()]
 files=source+[O/'loader-bounds.json',O/'HANDOFF.md']
 save(O/'handoff.json',dict(passed=True,frozen=True,carrier_granted=False,root_modified=False,installed=False,
  resolved='Five admitted forced-blank high3 copy/verify/restore row bounds',cold_CPU_cases=20,negative_CPU_cases=15,
  remaining=['Ordinary CurrentCHRBank/X5ChrMode compiled/indirect and scene ownership proof','Actual Main/NMI/IRQ publication seams','Final integrated source/ROM resource binding'],
  bindings={str(p.resolve()):sha(p)for p in files}))
 files.append(O/'handoff.json');z=O/'source-and-proof.zip'
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as out:
  for p in files:out.write(p,p.relative_to(R).as_posix())
 result=dict(passed=True,carrier_granted=False,path=z.as_posix(),sha256=sha(z),bytes=z.stat().st_size,members=len(files),source_files={p.relative_to(R).as_posix():sha(p)for p in source},root_modified=False,installed=False)
 save(O/'publication.json',result);print(json.dumps(result))

if __name__=='__main__':main()
