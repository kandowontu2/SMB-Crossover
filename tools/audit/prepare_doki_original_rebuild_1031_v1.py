"""Private guarded original FDS-file source reproduction; never game/native edits."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from private_build_outputs_v1 import validate
P=R/'build/doki-original-research-1031-v1/source';O=R/'build/doki-original-rebuild-1031-v1';S=O/'source';B=O/'assembled'
FDS=Path('C:/NES/fds/Yume Koujou - Doki Doki Panic (Japan) (DV 1).fds')
COMMIT='1c7327e4a0c800ff695293eb755cab0812738f69'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf8',newline='\n')
def run(cmd,cwd):
 proof=validate(cmd,O,cwd=cwd)
 for p in proof['outputs']:Path(p['path']).parent.mkdir(parents=True,exist_ok=True)
 q=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);row=dict(command=cmd,cwd=str(cwd),guard=proof,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr);logs.append(row)
 assert q.returncode==0,row
def main():
 global logs;logs=[];assert not O.exists();O.mkdir();S.mkdir();B.mkdir()
 try:
  assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()==COMMIT
  assert not subprocess.check_output(['git','diff','--name-only'],cwd=P,text=True).strip()
  tracked=subprocess.check_output(['git','ls-files'],cwd=P,text=True).splitlines()
  for rel in tracked:
   src=P/rel;dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(src.read_bytes())
  raw=FDS.read_bytes();assert len(raw)==131000 and sha(FDS)=='937894f56890d4c90d63037b656b9aede82f913c8eb1411511b6f7d52594192a'
  files=[]
  for side in range(2):
   p=side*65500+56;assert raw[p]==2;declared=raw[p+1];p+=2;count=0
   while raw[p]==3:
    h=raw[p:p+16];n=h[3:11].rstrip(b'\x00').decode('ascii');load=int.from_bytes(h[11:13],'little');size=int.from_bytes(h[13:15],'little');assert raw[p+16]==4
    data=raw[p+17:p+17+size];dst=O/'original-files'/(n.replace('-','_').lower()+'.bin');dst.parent.mkdir(exist_ok=True);dst.write_bytes(data)
    files.append(dict(side=side,declared_files=declared,ordinal=count,name=n,file_header_offset=p,data_offset=p+17,CPU=load,bytes=size,type=h[15],sha256=sha(dst),extracted=str(dst)));count+=1;p+=17+size
   assert count==declared
  # Exact equivalent of the primary author's extractor, whose constants
  # include a16-byte fwNES header. The local authoritative donor is headerless.
  assets=[]
  def asset(rel,offset,size):
   dst=S/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw[offset:offset+size]);assets.append(dict(path=str(dst),donor_offset=offset,bytes=size,sha256=sha(dst)))
  for rel,off,size in [('sdisk_chr.bin',3924,32),('waterfall/tile_00.bin',26035,15),('waterfall/tile_01.bin',26050,15),('waterfall/tile_02.bin',26065,2),('waterfall/tile_03.bin',26067,2),('waterfall/tile_04.bin',26069,2),('waterfall/tile_05.bin',26071,2),('sand/tile_00.bin',66047,15),('castle/tile_00.bin',66552,12),('castle/tile_01.bin',66564,12)]:asset('data/chr/'+rel,off-16,size)
  for folder,headerbase,length,start in [('title_c',41087,8176,0),('ending_c',49280,3072,224),('imajin_c',101620,832,0),('lina_c',102469,832,0),('mama_c',103318,832,0),('papa_c',104167,832,0),('bg_chr_1',105545,2560,224),('bg_chr_2',108122,2560,224),('bg_chr_3',110699,2560,224),('bg_chr_4',113276,2560,224)]:
   for i in range(length//16):
    obj=i+start<256;idx=i+start if obj else i-(256-start);kind='obj'if obj else'bg';asset(f'data/chr/{folder}/tile_{kind}_{idx:02X}.bin',headerbase-16+i*16,16)
  for i in range(32):asset(f'data/chr/bg_chr_c/tile_bg_{128+i:02X}.bin',105016-16+i*16,16)
  make=(S/'Makefile').read_text();vars={}
  for line in make.replace('\\\n',' ').splitlines():
   m=re.match(r'^(\w+)\s*(?:\?=|=)\s*(.*)',line)
   if m:vars[m[1]]=m[2]
  def expand(n):
   s=vars[n]
   for _ in range(30):
    if '$('not in s:return s
    s=re.sub(r'\$\((\w+)\)',lambda m:vars[m[1]],s)
   raise AssertionError('Recursive Make variable')
  objects=list(dict.fromkeys(expand('OBJS_FDS').split()));assert all(x.endswith('.o')for x in objects)
  for rel in objects:
   src=S/Path(rel).with_suffix('.s');obj=B/'objects'/rel;dep=obj.with_suffix('.dep')
   cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-U','-g','-I',str(S),'-I',str(S/'include'),'-DFDS','-DCONS','-DOG_PAD','-DOG_FALL','--create-full-dep',str(dep),'-o',str(obj),str(src)]
   run(cmd,S)
  cfg=(S/'link.fds.ld').read_text();cfg=re.sub(r'file\s*=\s*"([^"\n]*)"',lambda m:'file = "'+((B/m[1]).as_posix()if m[1]else'')+'"',cfg);(B/'original.cfg').write_text(cfg,encoding='utf8',newline='\n')
  run([str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(B/'original.cfg'),'-o',str(B/'unused.bin'),'--dbgfile',str(B/'original.dbg'),'-Ln',str(B/'original.lbl'),'-m',str(B/'original.map'),*[str(B/'objects'/p)for p in objects]],S)
  pairs=[]
  names={'KYODAKU-':'kyodaku_','TITLE-C':'title_c','SAVE-DAT':'save_dat','MAIN-PRO':'main_pro','EN-SND-D':'en_snd_d','ENDING-2':'ending_2','ENDING-C':'ending_c'}
  for f in files:
   stem=names.get(f['name'],f['name'].replace('-','_').lower());p=B/(stem+'.bin');assert p.exists(),p
   old=Path(f['extracted']).read_bytes();new=p.read_bytes();diff=[i for i,(a,b)in enumerate(zip(old,new))if a!=b]
   pairs.append(dict(name=f['name'],source_output=str(p),bytes=len(new),original_bytes=len(old),exact=new==old,differences=len(diff),first_differences=[dict(file_offset=i,CPU=f['CPU']+i,original=old[i],assembled=new[i])for i in diff[:24]],original_sha256=f['sha256'],assembled_sha256=sha(p)))
  refs=[Path(__file__),FDS,*[P/p for p in tracked],*[S/p for p in tracked],B/'original.cfg',B/'original.dbg',B/'original.lbl']
  save(O/'reproduction.json',dict(passed=all(q['exact']for q in pairs),source=True,native=False,git_commit=COMMIT,origin='https://gitlab.com/segaloco/doki',donor=dict(path=str(FDS),bytes=len(raw),sha256=sha(FDS)),default_original_flags=['FDS','CONS','OG_PAD','OG_FALL'],disk_files=files,assembled_files=pairs,objects=len(objects),assets=assets,bindings={str(p.resolve()):sha(p)for p in refs}))
  print(json.dumps(dict(path=str(O/'reproduction.json'),sha256=sha(O/'reproduction.json'),files=[{k:v for k,v in q.items()if k in('name','exact','differences','first_differences')}for q in pairs]),indent=2),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
 finally:save(O/'build-log.json',logs)
if __name__=='__main__':main()
