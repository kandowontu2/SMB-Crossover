"""Finite immutable source/receipt checkpoint with bounded CSV/CMakelists; excludes ROMs/debug/runtime."""
from pathlib import Path
import argparse,hashlib,json,zipfile
from checkpoint_roster_packets_v1 import ROOT,DEST,verify
def binding(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--handoff',type=Path,required=True);ap.add_argument('--name',required=True);ap.add_argument('--extra',type=Path,action='append',default=[]);a=ap.parse_args()
 hp=a.handoff.resolve();h=json.loads(hp.read_text());seen={};verify(h,seen)
 for key in ['bindings','actual_ASM_dependencies','actual_dependencies']:
  group=h.get(key,{})
  if not isinstance(group,dict):continue
  for p,v in group.items():
   if not isinstance(v,str):continue
   assert binding(p)['sha256']==v,p;seen[str(Path(p).resolve())]=v
 allowed={'.s','.inc','.c','.cfg','.json','.jsonl','.txt','.d','.dep','.patch','.log','.py','.lua','.chr','.png','.csv','.cmake'}
 files=[Path(p)for p in seen if Path(p).is_relative_to(hp.parent)and Path(p).suffix in allowed]
 for key in ['owned_tools','owned_new_tools','owned_files','owned_publication_files']:
  for row in h.get(key,[]):
   p=Path(row['path']if isinstance(row,dict)else row)
   assert p.is_relative_to(ROOT)and p.suffix in allowed,p;files.append(p)
 for key in ['report']:
  if key in h:files.append(Path(h[key]['path']))
 files += [hp,Path(__file__)]+[p.resolve()for p in a.extra]
 for p in a.extra:
  if p.suffix=='.json':verify(json.loads(p.read_text()),seen)
 target=DEST/a.name;assert not target.exists();target.mkdir()
 members={};archive=target/'frozen-source-packet.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in dict.fromkeys(files):
   content=p.read_bytes();name=p.resolve().relative_to(ROOT).as_posix();info=zipfile.ZipInfo(name,(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content);members[name]=hashlib.sha256(content).hexdigest()
 with zipfile.ZipFile(archive)as z:assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
 out=dict(status=h['status'],handoff=binding(hp),candidate=h.get('candidate'),verified_unique_bindings=len(seen),actual_ASM_dependencies=len(h.get('actual_ASM_dependencies',{})),original_bound_files=seen,archive=binding(archive),archive_members=members,explicit_limits=h.get('limits'))
 (target/'root-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checkpoint=str(target.relative_to(ROOT)),files=len(members),bindings=len(seen))))
if __name__=='__main__':main()
