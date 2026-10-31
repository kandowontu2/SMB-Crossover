"""Source-authentic CF projectile-radius overlap with typed native body targets."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
from prepare_cv3_dmc_mirror import prepare
P=R/'build/contra-force-world-chr-publisher-1031-v1';K=P/'kernel';PJ=P/'joint'
H=R/'docs/qa/checkpoints/2026-10-31/contra-force-world-chr-source-v1/handoff.json'
BASEK=R/'build/contra-force-p1-kernel-v1'
O=R/'build/contra-force-projectile-contact-1031-v3';J=O/'joint';N=O/'kernel'
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
  assert sha(PJ/'candidate.nes')=='a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
  b=qualified(PJ/'candidate.nes');imports=native_abi(b);oldlabels=labels(K/'runtime.lbl')
  old3=(K/'ram3.bin').read_bytes()
  assert old3[0x1fda:0x1fe0]==bytes([255])*6
  assert (K/'ram1.bin').read_bytes()[0x1f8c:0x1fe0]==bytes([255])*84
  assert len((K/'ram2.bin').read_bytes())==0x1fe0
  original=(BASEK/'component.s').read_text();write(N/'component.s','.export tbl_F94A\n'+original)
  (N/'state.inc').write_bytes((BASEK/'state.inc').read_bytes())
  source=(R/'build/contra-force-world-roles-1031-v2/kernel/boundaries.s').read_text()
  source=source.replace('.import CfState,CfNativeShot,CfNativeShotWorld,CfHostCallAdvance','.import CfContactAxisGate,CfNativeTargetTop,tbl_F94A\n.import CfState,CfNativeShot,CfNativeShotWorld,CfHostCallAdvance')
  at=source.index('CfHostShotContacts:');end=source.index('CfHostCollect:',at)
  part=source[at:end]
  part=part.replace(' lda #0\n sta CfEnemySlot','''
 ldx CfShotSlot
 lda CfState+$0420,x
 jeq CfContactDone
 cmp #29
 jcs CfContactDone
 asl
 tay
 lda tbl_F94A,y
 sta R5                    ; genuine original half-width
 lda tbl_F94A+1,y
 sta R6                    ; genuine original half-height
 lda #0
 sta CfEnemySlot''')
  old=''' cmp #BuzzyBeetle
 jeq CfContactAdvance
 cmp #Podoboo
 jeq CfContactAdvance
 cmp #BulletBill_FrenzyVar
 jeq CfContactAdvance'''
  assert part.count(old)==1
  part=part.replace(old,''' tay
 lda CfNativeTargetTop,y
 jeq CfContactAdvance       ; preserves hazards + rejects native no-op IDs''')
  p=part.index('CfContactGeometry:');q=part.index(' stx ObjectOffset',p)
  part=part[:p]+'''CfContactGeometry:
 lda Enemy_ID,x
 cmp #Bowser
 beq CfBossTargetX
 lda #0
 sta R0
 lda #15
 sta R1
 bne CfContactTargetX
CfBossTargetX:
 lda Enemy_BoundBoxCtrl,x
 cmp #21
 jcs CfContactAdvance
 asl
 asl
 tay
 lda BoundBoxCtrlData,y
 sta R0
 lda BoundBoxCtrlData+2,y
 sta R1
CfContactTargetX:
 lda R5
 sta R4
 lda ScreenLeft_X_Pos
 ldx CfShotSlot
 clc
 adc CfState+$034e,x
 sta R2
 lda ScreenLeft_PageLoc
 adc #0
 sta R3
 ldx CfEnemySlot
 lda R2
 sec
 sbc Enemy_X_Position,x
 sta R2
 lda R3
 sbc Enemy_PageLoc,x
 sta R3
 jsr CfContactAxisGate
 bcc CfContactAdvance
 lda Enemy_ID,x
 cmp #Bowser
 beq CfBossTargetY
 tay
 lda CfNativeTargetTop,y
 sec
 sbc #1
 sta R0
 lda #23
 sta R1
 bne CfContactTargetY
CfBossTargetY:
 lda Enemy_BoundBoxCtrl,x
 asl
 asl
 tay
 lda BoundBoxCtrlData+1,y
 sta R0
 lda BoundBoxCtrlData+3,y
 sta R1
CfContactTargetY:
 lda R6
 sta R4
 ldx CfShotSlot
 lda CfState+$0368,x
 ldx CfEnemySlot
 sec
 sbc Enemy_Y_Position,x
 sta R2
 lda #0
 sbc #0
 sta R3
 jsr CfContactAxisGate
 bcc CfContactAdvance
'''+part[q:]
  p1=(BASEK/'p1-runtime.s').read_text().replace('CfNativeP1Mask','CfNativeP1MaskTail')
  a=' lda CfNativeP1MaskTail,y\n sta CfP1Temp';assert p1.count(a)==1
  p1=p1.replace(a,'\n.export CfNativeP1MaskRead,CfNativeP1MaskReadEnd\nCfNativeP1MaskRead:\n php\n cpy #64\n bcs NativeMaskTail\n lda #2\n cpy #0\n bne NativeMaskReady\n lda #0\n beq NativeMaskReady\nNativeMaskTail:\n lda CfNativeP1MaskTail-64,y\nNativeMaskReady:\n sta CfP1Temp\n plp\n lda CfP1Temp\nCfNativeP1MaskReadEnd:')
  write(N/'p1-runtime.s',p1)
  mask=(BASEK/'native-mask.s').read_text();values=[]
  for line in mask.splitlines():
   if '.byte'in line:values.extend(int(v.strip().replace('$','0x'),0)for v in line.split('.byte')[1].split(','))
  assert values[:64]==[0]+[2]*63 and len(values)==145
  write(N/'native-mask.s','.export CfNativeP1MaskTail\n.segment "CF_P1_NATIVE_MASK"\nCfNativeP1MaskTail:\n .byte '+','.join(str(v)for v in values[64:])+'\n')
  prefix='''CfHostShotContacts:
 lda CfState+$0382,x
 jeq CfNoContact
 lda CfState+$0300,x
 and #$f0
 jne CfNoContact
 lda CfState+$0334,x
 cmp #28
 jne CfNoContact
 txa'''
  compact='''CfHostShotContacts:
 lda CfState+$0382,x
 beq CfContactReturnEarly
 lda CfState+$0300,x
 and #$f0
 bne CfContactReturnEarly
 lda CfState+$0334,x
 cmp #28
 beq CfContactValid
CfContactReturnEarly:rts
CfContactValid:
 txa'''
  assert part.count(prefix)==1;part=part.replace(prefix,compact)
  assert part.count(' beq CfContactGeometry')==1;part=part.replace(' beq CfContactGeometry',' beq CfBossTargetX')
  part=part.replace('CfContactGeometry:\n lda Enemy_ID,x\n cmp #Bowser\n beq CfBossTargetX','CfContactGeometry:')
  write(N/'boundaries.s',source[:at]+part+source[end:])
  runtime=R/'tools/reference/contra_force_projectile_contact_1031_v1.s';write(N/'contact-runtime.s',runtime.read_text())
  logs=json.loads((BASEK/'build-log.json').read_text())
  for name in('component','boundaries','contact-runtime','p1-runtime','native-mask'):
   recipe_name='boundaries'if name=='contact-runtime'else name
   cmd=next(q['command']for q in logs if q['command'][-1]==str(BASEK/(recipe_name+'.s')))[:]
   for flag,path in[('--create-full-dep',N/(name+'.dep')),('-o',N/(name+'.o'))]:cmd[cmd.index(flag)+1]=str(path)
   cmd[-1]=str(N/(name+'.s'));run('kernel-'+name+'-build',cmd,N)
  cfg=(K/'runtime.cfg').read_text().replace('CF_SCROLL_PUBLISHER:load=A3,type=ro,start=$bfba;', 'CF_SCROLL_PUBLISHER:load=A3,type=ro;')
  cfg=cfg.replace(' CF_SCROLL_PUBLISHER:', ' CF_CONTACT_AXIS:load=A1,type=ro,start=$bf8c;\n CF_CONTACT_GATE:load=C2,type=ro;\n CF_CONTACT_TARGET:load=C2,type=ro;\n CF_SCROLL_PUBLISHER:')
  write(N/'runtime.cfg',cfg)
  cmd=json.loads((P/'kernel-link.json').read_text())['command'][:]
  for flag,path in[('-C',N/'runtime.cfg'),('-o',N/'unused.bin'),('--dbgfile',N/'runtime.dbg'),('-Ln',N/'runtime.lbl'),('-m',N/'runtime.map')]:cmd[cmd.index(flag)+1]=str(path)
  for i,x in enumerate(cmd):
   if Path(x).name in('component.o','boundaries.o','p1-runtime.o','native-mask.o'):cmd[i]=str(N/Path(x).name)
  cmd.append(str(N/'contact-runtime.o'));run('kernel-link',cmd,N)
  newlabels=labels(N/'runtime.lbl');new3=(N/'ram3.bin').read_bytes();helper=bytes()
  assert newlabels['CfContactAxis']>=0xbf8c and newlabels['CfContactAxisEnd']<=0xbfe0
  assert newlabels['CfNativeTargetTop']>=0xddd2 and newlabels['CfNativeTargetTopEnd']<=0xde00
  assert newlabels['CfHostScrollPublishEnd']<=0xbfe0
  images=[]
  for i in(1,2,3):
   image=bytearray((N/f'ram{i}.bin').read_bytes());image.extend(bytes(8192-len(image)))
   if i in(2,3):image[0x1fe0:]=bytes(32)
   images.append(image)
  stream=b''.join(images);cookie=bytes([167,31,0,5])+hashlib.sha256(stream).digest()[:12]
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
  refs=[Path(__file__),runtime,H,P/'source-stage.json',P/'kernel-link.json',P/'final-link.json',PJ/'candidate.nes',PJ/'candidate.dbg',BASEK/'build-log.json',BASEK/'component.s',BASEK/'state.inc',K/'runtime.cfg',K/'runtime.lbl',K/'ram3.bin',R/'tools/audit/private_build_outputs_v1.py',Path(sys.modules[prepare.__module__].__file__),
    *[p for p in N.iterdir()if p.is_file()],*[p for p in J.iterdir()if p.is_file()and p.suffix in('.s','.o','.dep','.bin','.cfg','.nes','.dbg','.lbl')],*O.glob('*-build.json'),O/'kernel-link.json',O/'final-link.json']
  save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,parent=sha(PJ/'candidate.nes'),candidate=sha(J/'candidate.nes'),cookie=cookie.hex(),
    semantics='Genuine source radius/comparator with intentional static native ordinary-body targets; native player/stomp boxes and original shot motion/art unchanged.',
    helper=dict(A1=[newlabels['CfContactAxis'],newlabels['CfContactAxisEnd']],C2=[newlabels['CfContactAxisGate'],newlabels['CfNativeTargetTopEnd']],A3_end=newlabels['CfHostScrollPublishEnd']),
    all_native_matched_PC_locations_preserved=count,all_other_ROM_CHR_header_BT_menu_Start_exact=True,
    original_donor_component_bytes_exact_except_zero_byte_export=True,native_imports=imports,bindings={str(p.resolve()):sha(p)for p in refs}))
  print(json.dumps(dict(candidate=sha(J/'candidate.nes'),stage=str(O/'source-stage.json'),sha256=sha(O/'source-stage.json'),cookie=cookie.hex()),indent=2),flush=True)
 except Exception as e:save(O/'negative.json',dict(passed=False,error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
