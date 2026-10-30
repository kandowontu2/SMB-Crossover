"""Copy immutable FF palette evidence into a compact docs checkpoint only."""
from pathlib import Path
import gzip,hashlib,json
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-30/ff-fx-palette-audit'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
    O.mkdir(exist_ok=False)
    pairs=[('build/ff-fx-palette-closure-v1/handoff.json','source-handoff.json',False),
      ('build/ff-fx-palette-closure-v1/README.md','README.md',False),
      ('build/ff-fx-palette-closure-v1/controls.json','closure-controls.json.gz',True),
      ('build/ff-fx-palette-audit-v2/audit.json','palette-positive-v2.json.gz',True),
      ('build/ff-fx-mask-feasibility-v2/audit.json','mask-positive-v2.json.gz',True),
      ('build/ff-fx-palette-audit-v1/negative-v1.json','palette-negative-v1.json.gz',True),
      ('build/ff-fx-mask-feasibility-v1/negative-v1.json','mask-negative-v1.json.gz',True)]
    members=[]
    for source,name,compressed in pairs:
        raw=(R/source).read_bytes();data=gzip.compress(raw,mtime=0)if compressed else raw
        (O/name).write_bytes(data)
        assert (gzip.decompress((O/name).read_bytes())if compressed else(O/name).read_bytes())==raw
        members.append(dict(file=name,bytes=len(data),sha256=sha(data),source=source,
          uncompressed_sha256=sha(raw),compressed=compressed))
    tools=['ff_fx_palette_audit_v1.py','ff_fx_palette_audit_v2.py',
      'ff_fx_mask_feasibility_v1.py','ff_fx_mask_feasibility_v2.py',
      'ff_fx_palette_closure_v1.py','stage_ff_fx_palette_checkpoint_v1.py']
    p=dict(passed=True,files_only=True,Git_index_touched=False,native=False,admitted=False,
      original_cart='c1aeff70d438788c1abbe542186c59ac10c5a7bac0f60fd53b0718b44d3d0a79',
      members=members,tools={str(R/'tools/audit'/f):sha((R/'tools/audit'/f).read_bytes())for f in tools})
    (O/'manifest.json').write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(path=str(O),files=len(members)+1,total_bytes=sum(m['bytes']for m in members),
      manifest_sha256=sha((O/'manifest.json').read_bytes()))),flush=True)


if __name__=='__main__':main()
