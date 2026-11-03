"""Pin only active old collision header and actual origin/bounds migration."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys
from zipfile import ZipFile,ZIP_DEFLATED
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
INPUTS=[('Mico27/SuperMarioBrosMini','56d5a30ff8f58096c074ca59656efc5f787d0edb','plugins/DynamicMapPlugin/engine/include/collision.h','7f3641ac094cd2483b7c55a85b46196c4ee5a7dd'),('chrismaltby/gb-studio',W.CORE,'src/lib/project/migration/versions/410to420.ts','cb74b50a886c0d24779659ce02a80d1c594b3553'),('chrismaltby/gb-studio',W.CORE,'src/lib/compiler/generateGBVMData.ts','10e277eb9b95740d56db17cec80dff8bc3c97170'),('chrismaltby/gb-studio',W.CORE,'src/shared/lib/resources/types.ts','d1052cac3e451696a798c7dd820bffc62e3f017c'),('chrismaltby/gb-studio',W.CORE,'src/lib/project/migration/legacy/migrateLegacyProjectVersions.ts','0e0d25e740332940fea08ba84831c2f0c645d90f'),('chrismaltby/gb-studio',W.CORE,'src/lib/project/migration/migrateProjectResources.ts','7f5f1ecccd9178823e10f06e1aefa8bd77f889db')]
def main():
 d={};b={}
 for repo,commit,path,blob in INPUTS:
  q=W.api(repo,'git/blobs/'+blob);v=base64.b64decode(q['content']);assert hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()==blob
  k=repo+'/'+path;d[k]=v;b[k]=dict(commit=commit,blob=blob,SHA256=W.sha(v))
 with ZipFile(W.O/'anchor-inputs-v17.zip','w',ZIP_DEFLATED,compresslevel=9)as z:
  for k,v in d.items():z.writestr(k,v)
 (W.O/'anchor-inputs-v17.json').write_text(json.dumps(b,indent=2)+'\n')
 for k,v in d.items():
  s=v.decode().splitlines();hits=[i for i,l in enumerate(s)if any(t in l for t in ['canvasOrigin','compileBounds =','COLLISION_','bounding_box_t'])]
  print(k)
  keep=set(j for i in hits for j in range(max(0,i-3),min(len(s),i+5)))
  for i in sorted(keep):print(f'{i+1}: {s[i]}')
if __name__=='__main__':main()
