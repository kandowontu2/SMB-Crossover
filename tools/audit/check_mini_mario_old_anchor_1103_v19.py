"""Source-era pixel bounds/origin proof, distinct from incompatible new API."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import base64,hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W

def main():
 repo='chrismaltby/gb-studio';commit='6009ffa7e11de0d1e856b34ebda3477141c1a9bb'
 tree=W.api(repo,'git/trees/'+commit+'?recursive=1');assert not tree.get('truncated');T={r['path']:r for r in tree['tree']};d={};bind={}
 for path in ['src/lib/compiler/compileSprites.ts','src/lib/compiler/generateGBVMData.ts']:
  blob=T[path]['sha'];q=W.api(repo,'git/blobs/'+blob);v=base64.b64decode(q['content']);assert hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()==blob
  k=repo+'/'+path;d[k]=v;bind[k]=dict(commit=commit,blob=blob,SHA256=W.sha(v))
 with ZipFile(W.REF)as z:
  for p in ['plugins/GameSpecific/engine/src/core/actor.c','plugins/GameSpecific/engine/include/actor.h']:
   d['Mini/'+p]=z.read(p)
 with ZipFile(W.O/'anchor-old-inputs-v19.zip','w',ZIP_DEFLATED,compresslevel=9)as z:
  for p,v in d.items():z.writestr(p,v)
 for p,v in d.items():
  s=v.decode().splitlines();words=['fixedXOffset','fixedYOffset','currentX =','currentY =','bounds =','boundsX','boundsY','boundsHeight','screen_x =','screen_y =','move_metasprite(']
  I=set(j for i,l in enumerate(s)if any(t in l for t in words)for j in range(max(0,i-2),min(len(s),i+4)))
  print(p)
  for i in sorted(I):print(f'{i+1}: {s[i]}')
 (W.O/'anchor-old-inputs-v19.json').write_text(json.dumps(bind,indent=2)+'\n')
if __name__=='__main__':main()
