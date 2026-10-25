
from pathlib import Path
import hashlib,json
def apply(source,assets):
 source=Path(source);assets=Path(assets)
 sha=lambda b:hashlib.sha256(b).hexdigest()
 m=json.loads((assets/'repairs.json').read_text())
 for row in m['text_repairs']:
  p=source/row['path'];t=p.read_text()
  for q in row['chunks']:
   assert t.count(q['old'])==1,('Current MMC3 repair context changed',row['path'],q['old'][:120])
   t=t.replace(q['old'],q['new'],1)
  p.write_text(t)
 a=m['atlas'];atlas=(assets/a['path']).read_bytes();assert sha(atlas)==a['sha256']and len(atlas)==a['length']
 p=source/'chr/characters/oversized-raw.chr';raw=bytearray(p.read_bytes());offset=a['raw_offset'];assert sha(raw[offset:offset+len(atlas)])==a['raw_replaced_sha256'],'Current atlas packing overlaps changed source art'
 raw[offset:offset+len(atlas)]=atlas;p.write_bytes(raw)
 p=source/'chr/characters/mmc3-menu-previews.chr';assert sha(p.read_bytes())==a['old_preview_sha256'];p.write_bytes(atlas)
 return m
