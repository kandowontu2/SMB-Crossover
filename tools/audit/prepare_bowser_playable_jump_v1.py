"""Own one-operand injury admission and lives-only portrait anchor successor."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/bowser-current64-v3';O=R/'build/bowser-playable-jump-v1';J=O/'joint';D=J/'bowser'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,s):write(p,json.dumps(s,indent=2)+'\n')

def main():
 assert not O.exists();h=json.loads((P/'handoff.json').read_text())
 for p,v in h['bindings'].items():assert sha(p)==v,p
 shutil.copytree(P/'joint',J)
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.inc','.cfg']:
   write(p,p.read_text(encoding='utf-8').replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
 s=(D/'host.s').read_text();assert s.count('BwStatus:\n lda BwTier\n tax\n rts')==1
 write(D/'host.s',s.replace(' lda #90\n sta InjuryTimer',' lda #8                     ; genuine native interval duration, not90frames\n sta InjuryTimer').replace('BwStatus:\n lda BwTier\n tax\n rts','; Native ForceInjury uses zero as immediate death, not power tier.\nBwStatus:\n lda BwHP\n tax\n rts'))
 core=(D/'core.s').read_text();assert core.count('lda #$fe                   ; original source1 Bowser -2px jump')==1
 write(D/'core.s',core.replace('lda #$fe                   ; original source1 Bowser -2px jump','lda #$fd                   ; authored playable A-edge -3; original falling arithmetic below unchanged'))
 s=(D/'cold.s').read_text();s=s.replace('.export BwScene', '.importzp Player_Y_Position\n.export BwScene',1)
 marker=' lda #.lobyte(.bank(BwPortrait1Right)|$80)\n sta CurrentBankC\n sta $5116\n lda #$e9'
 assert s.count(marker)==1;s=s.replace(marker,'BwColdMap:\n'+marker,1)
 a=s.index('BwColdDraw:');z=s.index('.assert *<=$b600',a)
 s=s[:a]+'''BwColdDraw:
 php
 pha
 lda OperMode
 cmp #1
 bne BwColdNoLifeOffset
 lda Player_Y_Position
 adc #7                    ; exact CMP#1 path already hasC1: +8
 sta Player_Y_Position
BwColdNoLifeOffset:
 jsr BwColdMap
 pla
 plp
 BwFar DrawMetasprite,jsr
 php
 pha
 lda OperMode
 cmp #1
 bne BwColdDrawRestore
 lda Player_Y_Position
 sbc #8                    ; exact CMP#1 path still hasC1
 sta Player_Y_Position
BwColdDrawRestore:
 pla
 plp
 rts
'''+s[z:];write(D/'cold.s',s)
 cc=R/'tools/Windows/cc65/bin'
 def run(name,c):
  guard=validate(c,J,cwd=R);r=subprocess.run(c,cwd=R,text=True,capture_output=True)
  save(O/(name+'.json'),dict(command=c,validation=guard,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,(name,r.stderr)
 def asm(name):run('bowser-'+name+'-build',[str(cc/'ca65.exe'),'--cpu','6502x','-g','-I',str(D),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(D/(name+'.dep')),'-o',str(D/(name+'.o')),str(D/(name+'.s'))])
 for name in ['host','core','cold']:asm(name)
 c=json.loads((P/'final-link.json').read_text())['command'][:]
 for i,x in enumerate(c):
  if x.startswith(str(P/'joint')):c[i]=x.replace(str(P/'joint'),str(J))
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 if '--ld-args'in c:
  i=c.index('--ld-args')+1;v=c[i].split(',')
  for k in range(1,len(v),2):v[k]=str(J/Path(v[k]).name)
  c[i]=','.join(v)
 run('initial-link',c)
 (D/'cookie.bin').write_bytes(bytes([167,27,0,5])+hashlib.sha256((J/'bowser.bin').read_bytes()).digest()[:12])
 for name in ['check','load','stream']:asm(name)
 run('final-link',c);prepare(R,J/'candidate.nes')
 b=load(J/'candidate.nes');old=load(P/'joint/candidate.nes')
 for name in ['BwColdPrepare','BwColdDraw','BwStatus','BwMovement','BwGraphics','BwScene','BwMenuResolve','BwServiceVeneers']:
  assert address(b,name)==address(old,name)and location(b,name)==location(old,name),name
 for name in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:
  assert sha(J/name)==sha(P/'joint'/name),name
 s=next(v for v in b['segs'].values()if v['name']=='"BW_ROM_PREVIEW"')
 assert int(s['size'],0)==203 and int(s['start'],0)+int(s['size'],0)<=0xb600
 allowed=[(16+83*8192+0x1534,16+83*8192+0x1600),
          (16+68*8192+0x1f20,16+69*8192),
          (16+84*8192+0x1529,16+84*8192+0x1600),
          (16+128*8192+927*1024,16+128*8192+935*1024)]
 diffs=[i for i,(a,z)in enumerate(zip(old['raw'],b['raw']))if a!=z]
 assert all(any(lo<=i<hi for lo,hi in allowed)for i in diffs)
 q=dict(source=True,status='OWN_CONTACT_AND_LIVES_SOURCE_TARGETED_CONTROLS_PENDING',native=False,installed=False,admitted=False,
  candidate=sha(J/'candidate.nes'),parent=h['candidate'],parent_handoff=sha(P/'handoff.json'),joint=str(J),ready=66,
  gameplay_change='Status reads HP; normal native8-interval protection; authored playable source1 A-edge -3, retaining original fraction/gravity/fall arithmetic.',
  lives_change='OperMode1 portrait-only PlayerY+8 during genuine DrawMetasprite, restored afterward; select positions/CHR/palettes unchanged.',
  resident_used=1223,resident_granted=1281,resident_headroom=58,portrait_used=203,portrait_granted=204,
  public_PCs_preserved=True,changed_ROM_bytes=len(diffs),
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'handoff.json',D/'host.s',D/'cold.s',D/'cookie.bin',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'bowser.bin']})
 save(O/'source-stage.json',q);save(J/'source-stage.json',q);print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
