"""Bind the audit to authored original streams and both current cartridges."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess
from level_layout_inventory_agent import R,O,record
sp=importlib.util.spec_from_file_location('audit_image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
def streams(p):
 out={};name=None
 for line in p.read_text().splitlines():
  m=re.match(r'^([LE]_(?:Castle|Ground|Underground|Water)Area\d+):',line)
  if m:name=m[1];out[name]=[];continue
  if name and re.match(r'^\w',line):name=None
  if name and '.byte'in line:out[name].extend(int(v,16)for v in re.findall(r'\$([0-9a-fA-F]{2})',line.split(';')[0]))
 return{k:bytes(v)for k,v in out.items()}
def main():
 src=R/'src/level_tiles.s';up=R/'.upstream/smb1base/src/level_tiles.s';a,b=streams(src),streams(up);assert set(a)==set(b)and len(a)==68
 records=[]
 for role,path in [('baseline_mmc3',R/'build/smb-crossover-mmc3-baseline.nes'),('current_mmc3',R/'build/smb-crossover-mmc3.nes'),('current_mmc5',R/'build/smb-crossover-mmc5.nes')]:
  image=im.Image(path);rows=[]
  for name,raw in a.items():
   h=image.hook(name);actual=image.raw[h['rom_offset']:h['rom_offset']+len(raw)];assert actual==raw,(role,name)
   rows.append(dict(name=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),ROM_offset=h['rom_offset'],matches_upstream=raw==b[name]))
  records.append(dict(role=role,image=record(path),streams=rows))
 assert all(a[k]==b[k]for k in a)
 result=dict(upstream_commit=subprocess.check_output(['git','-C',str(R/'.upstream/smb1base'),'rev-parse','HEAD'],text=True).strip(),source=record(src),upstream_source=record(up),all_68_current_level_and_enemy_streams_equal_upstream=True,compiled_images=records,scope='Exact authored level/enemy stream bytes. Runtime code can alter object admission, motion, collision and hazards; equality does not establish complete gameplay equivalence.')
 (O/'source-binding.json').write_text(json.dumps(result,indent=2)+'\n')
 print(dict(streams=len(a),images=len(records),all_streams_equal=True))
if __name__=='__main__':main()
