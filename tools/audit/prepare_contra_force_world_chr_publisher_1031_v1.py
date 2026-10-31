"""Restore genuine native world sprite windows1..3 inside the CF graphics publisher."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
from prepare_cv3_dmc_mirror import prepare
P=R/'build/contra-force-scroll-publisher-1031-v2';K=P/'kernel';PJ=P/'joint'
H=R/'docs/qa/checkpoints/2026-10-31/contra-force-scroll-source-v1/handoff.json'
BASEK=R/'build/contra-force-p1-kernel-v1'
O=R/'build/contra-force-world-chr-publisher-1031-v1';J=O/'joint';N=O/'kernel'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def bound(p):
 q=json.loads(p.read_text())
 for f,h in q['bindings'].items():assert sha(f)==h,('Frozen dependency changed',f)
 return q
def run(name,cmd,cwd):
 g=validate(cmd,O,cwd=cwd)
 for p in g['outputs']:Path(p['path']).parent.mkdir(parents=True,exist_ok=True)
 z=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True)
 save(O/(name+'.json'),dict(command=cmd,cwd=str(cwd),output_guard=g,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr))
 assert z.returncode==0,(name,z.stderr)
def labels(p):return{n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',p.read_text())}
def main():
 assert not O.exists();O.mkdir();J.mkdir();N.mkdir()
 try:
  bound(H);bound(P/'source-stage.json');bound(BASEK/'build-proof.json')
  assert sha(PJ/'candidate.nes')=='1cbbd1ccfb22614b206d2e6fe75c55795f31bd47c2bbeda127f0b1645baf9b7d'
  b=qualified(PJ/'candidate.nes');imports=native_abi(b);oldlabels=labels(K/'runtime.lbl')
  old3=(K/'ram3.bin').read_bytes();assert old3[0x1fc6:0x1fda]==bytes([255])*20
  table=address(b,'CHRBankInitValues');assert table>=0xe000
  off=location(b,'CHRBankInitValues');assert b['raw'][off:off+12]==bytes([18,20,21,22,23,24,25,26,4,5,6,7])
  expected=(K/'ram3.bin').read_bytes()[0x1fba:0x1fc6]
  rel,pos,obj=[address(b,n)for n in['Player_Rel_XPos','Player_Pos_ForScroll','ObjectMetasprite']]
  write(N/'native-imports.s',(K/'native-imports.s').read_text()+f'\n.export CHRBankInitValues\nCHRBankInitValues=${table:04x}\n')
  helper_source=(K/'scroll-publisher.s').read_text().replace('.export CfHostScrollPublish,CfHostScrollPublishEnd','.import CHRBankInitValues,CurrentCHRBank,X5ChrMode\n.export CfHostScrollPublish,CfHostScrollPublishEnd')
  helper_source=helper_source.replace(' lda #0\n sta ObjectMetasprite','''
 ; Native portrait mapped1..3 directly. Restore exact ordinary native shadows
 ; and their legacy interpretation before the existing completed publisher.
 ; Body0, own shots6, special4 and all backgrounds remain unchanged.
 txa
 pha
 ldx #3
RestoreNativeWorld:
 lda CHRBankInitValues,x
 sta CurrentCHRBank,x
 lda #0
 sta X5ChrMode,x
 dex
 bne RestoreNativeWorld
 pla
 tax
 lda #0
 sta ObjectMetasprite''').replace('=12,error,"own12B native publisher"','=32,error,"own32B native and world publisher"')
  write(N/'scroll-publisher.s',helper_source)
  for name in('native-imports','scroll-publisher'):
   cmd=json.loads((P/('kernel-'+name+'-build.json')).read_text())['command'][:]
   for flag,path in[('--create-full-dep',N/(name+'.dep')),('-o',N/(name+'.o'))]:cmd[cmd.index(flag)+1]=str(path)
   cmd[-1]=str(N/(name+'.s'));run('kernel-'+name+'-build',cmd,N)
  write(N/'runtime.cfg',(K/'runtime.cfg').read_text())
  cmd=json.loads((P/'kernel-link.json').read_text())['command'][:]
  for flag,path in[('-C',N/'runtime.cfg'),('-o',N/'unused.bin'),('--dbgfile',N/'runtime.dbg'),('-Ln',N/'runtime.lbl'),('-m',N/'runtime.map')]:cmd[cmd.index(flag)+1]=str(path)
  for i,x in enumerate(cmd):
   if x.endswith('native-imports.o'):cmd[i]=str(N/'native-imports.o')
   elif x.endswith('scroll-publisher.o'):cmd[i]=str(N/'scroll-publisher.o')
  run('kernel-link',cmd,N)
  newlabels=labels(N/'runtime.lbl')
  assert all(newlabels[n]==v for n,v in oldlabels.items()if n!='CfHostScrollPublishEnd'),'Old private entry PCs changed'
  assert newlabels['CfHostScrollPublish']==0xbfba and newlabels['CfHostScrollPublishEnd']==0xbfda
  assert(N/'ram1.bin').read_bytes()==(K/'ram1.bin').read_bytes()and(N/'ram2.bin').read_bytes()==(K/'ram2.bin').read_bytes()
  new3=(N/'ram3.bin').read_bytes();oracle=bytearray(old3)
  helper=new3[0x1fba:0x1fda];assert helper[:6]==expected[:6]and helper[-6:]==expected[-6:]
  oracle[0x1fba:0x1fda]=helper;assert new3==oracle
  images=[]
  for i in(1,2,3):
   image=bytearray((N/f'ram{i}.bin').read_bytes());image.extend(bytes(8192-len(image)))
   if i in(2,3):image[0x1fe0:]=bytes(32)
   images.append(image)
  stream=b''.join(images);cookie=bytes([167,31,0,4])+hashlib.sha256(stream).digest()[:12]
  (J/'cf-stream.bin').write_bytes(stream);(J/'cf-cookie.bin').write_bytes(cookie)
  for name in('cf-loader','cf-guard','cf-carrier'):
   text=(PJ/(name+'.s')).read_text()
   for asset in('cf-cookie.bin','cf-stream.bin'):
    text=re.sub(r'\.incbin\s+"[^\"]*'+re.escape(asset)+'"',lambda m:'.incbin "'+(J/asset).as_posix()+'"',text)
   write(J/(name+'.s'),text)
   cmd=json.loads((P/(name+'-build.json')).read_text())['command'][:]
   for flag,path in[('--create-full-dep',J/(name+'.dep')),('-o',J/(name+'.o'))]:cmd[cmd.index(flag)+1]=str(path)
   cmd[-1]=str(J/(name+'.s'));run(name+'-build',cmd,R)
  cfg=(PJ/'candidate.cfg').read_text();cfg=re.sub(r'file="([^\"]+)"',lambda m:'file="'+(J/'sideoutputs'/Path(m[1]).name).as_posix()+'"',cfg);write(J/'candidate.cfg',cfg)
  cmd=json.loads((P/'final-link.json').read_text())['command'][:]
  for flag,path in[('-C',J/'candidate.cfg'),('-Ln',J/'candidate.lbl'),('-o',J/'candidate.nes'),('-m',J/'candidate.map')]:cmd[cmd.index(flag)+1]=str(path)
  cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(J/'candidate.dbg')
  for i,x in enumerate(cmd):
   if Path(x).name in('cf-loader.o','cf-guard.o','cf-carrier.o'):cmd[i]=str(J/Path(x).name)
  run('final-link',cmd,R);prepare(R,J/'candidate.nes')
  n=qualified(J/'candidate.nes');raw=n['raw'];base=b['raw'];oracle=bytearray(base);cs=16+128*8192+935*1024;oracle[cs:cs+24576]=stream
  for name in('CfExternalCookie','CfLoaderExpectedCookie'):
   p=location(b,name);oracle[p:p+16]=cookie
  assert raw==oracle,'Product differs from exact own source-only delta'
  count=0
  for name,s in b['syms'].items():
   if s.get('type')=='lab'and'seg'in s and name in n['syms']:
    assert address(b,name)==address(n,name),name
    if'ooffs'in b['segs'][s['seg']]:assert location(b,name)==location(n,name),name
    count+=1
  refs=[Path(__file__),H,P/'source-stage.json',P/'kernel-link.json',P/'final-link.json',PJ/'candidate.nes',PJ/'candidate.dbg',BASEK/'build-log.json',BASEK/'native-imports.s',K/'scroll-publisher.s',K/'runtime.cfg',K/'runtime.lbl',K/'ram3.bin',R/'tools/audit/private_build_outputs_v1.py',Path(sys.modules[prepare.__module__].__file__),
    *[p for p in N.iterdir()if p.is_file()],*[p for p in J.iterdir()if p.is_file()and p.suffix in('.s','.o','.dep','.bin','.cfg','.nes','.dbg','.lbl')],*O.glob('*-build.json'),O/'kernel-link.json',O/'final-link.json',R/'build/contra-force-11-native-1031-v5/burns/capture/result.json']
  save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,parent=sha(PJ/'candidate.nes'),candidate=sha(J/'candidate.nes'),cookie=cookie.hex(),
    only_semantic_change='CF graphics publishes exact native Player_Rel_XPosÃ¢â€ â€™Player_Pos_ForScroll; original native scroll/parser/donor movement unchanged',
    own_helper=dict(start=0xbfba,end=0xbfda,bytes=list(helper),original_native_publisher=list(expected)),
    private_entry_delta=dict(label='CfHostScrollPublish',start=0xbfba,old=list(expected),new=list(helper)),
    all_old_private_entry_labels_preserved=len(oldlabels)-1,diagnostic_end_relocated=['CfHostScrollPublishEnd',0xbfc6,0xbfda],all_native_matched_PC_locations_preserved=count,all_other_ROM_CHR_header_BT_menu_Start_exact=True,
    native_imports=imports,bindings={str(p.resolve()):sha(p)for p in refs}))
  print(json.dumps(dict(candidate=sha(J/'candidate.nes'),stage=str(O/'source-stage.json'),sha256=sha(O/'source-stage.json'),cookie=cookie.hex()),indent=2),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
