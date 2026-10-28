"""Sparse independent Dragon Power component build; no shared/canonical build."""
from pathlib import Path
import json,re,subprocess,sys
import dragon_power_map_v1 as D
ROOT=D.ROOT;OUT=ROOT/'build/dragon-power-component-v1'
HOST=ROOT/'build/celeste-host-final'
EXPECTED={'nes':'83db8bdf74dddc4055a52f5ec12526dcddc7a2fe418f24c3e9e1d5252fb6c9e0',
          'dbg':'88b90d2c46d0741fd064f3f72986c4a387d576b3b8aab6592163451f1f02bc8f',
          'lbl':'8613a3e99fac81e831daa10776b89c40ae5ba268e591d34b2a4d47d839c9c7a3'}
NAMES='''SelectedCharacter NumberofLives AreaAddrsLOffset AreaType WorldNumber SavedJoypadBits GamePauseStatus
GameEngineSubroutine TimerControl Player_Rel_XPos Player_Y_Position Player_Y_HighPos ScreenLeft_X_Pos
ScreenLeft_PageLoc GetBlockBufferAddr MmSolidTerrain Block_Buffer_1 MTileAttribute R0 R1 R2 R3 R4 R5 R6 R7
Player_X_Position Player_X_Scroll Player_PageLoc Player_Y_Speed Player_X_Speed Player_XSpeedAbsolute
PlayerFacingDir Player_State PlayerSize PlayerStatus CrouchingFlag CrossoverBehaviorVersion
CurrentBankC Player_SprAttrib Player_Pos_ForScroll SmPosePtr SmChrBank ObjectMetasprite
SafecallA_SMC FarcallJmpTarget_SMC FarCallCommon X5SetPhysicalChr MetaspriteRenderLoop'''.split()
def labels(p):
 out={}
 for line in p.read_text().splitlines():
  m=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
  if m:out[m[2]]=int(m[1],16)
 return out
def build():
 OUT.mkdir(exist_ok=True)
 for ext,h in EXPECTED.items():assert D.digest(HOST.with_suffix('.'+ext).read_bytes())==h
 s=labels(HOST.with_suffix('.lbl'));dbg=HOST.with_suffix('.dbg').read_text()
 for n in ['MTILE_SOLID','METASPRITE_SAMUS_BODY']:
  m=re.search(r'^sym[^\n]*name="'+n+r'"[^\n]*val=0x([0-9A-Fa-f]+)',dbg,re.M);assert m,n
  s[n]=int(m[1],16)
 pre='\n'.join(f'{n}=${s[n]:04x}'for n in NAMES+['MTILE_SOLID','METASPRITE_SAMUS_BODY'])+'\n.macpack longbranch\nDP_CHR_PUBLISH_BANK=62\nDP_RENDER_BANK=4\n'
 (OUT/'component.s').write_text(pre+'.include "dragon_power.s"\n')
 art=str((OUT/'art.bin').resolve()).replace('\\','/');chr=str((OUT/'chr.bin').resolve()).replace('\\','/')
 (OUT/'component.cfg').write_text('MEMORY { K:start=$A800,size=$1800,bank=86,file=%O; A:start=$C900,size=$1000,bank=85,file="'+art+'"; C:start=$C5000,size=$2000,file="'+chr+'"; }\nSEGMENTS { DRAGON_POWER_CORE:load=K,type=ro; DRAGON_POWER_ART:load=A,type=ro; DRAGON_POWER_CHR:load=C,type=ro; }\n')
 cc=ROOT/'tools/Windows/cc65/bin'
 commands=[[str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(OUT/'component.s'),'-o',str(OUT/'component.o')],
 [str(cc/'ld65.exe'),'-C',str(OUT/'component.cfg'),'-o',str(OUT/'component.bin'),'-Ln',str(OUT/'component.lbl'),
 '--dbgfile',str(OUT/'component.dbg'),str(OUT/'component.o')]]
 for cmd in commands:
  q=subprocess.run(cmd,capture_output=True,text=True)
  if q.returncode:
   p=OUT/'first-build-failure.txt'
   if not p.exists():p.write_text(q.stdout+q.stderr)
   raise RuntimeError(q.stdout+q.stderr)
 s.update(labels(OUT/'component.lbl'))
 for line in (OUT/'component.dbg').read_text().splitlines():
  if not line.startswith('sym\t'):continue
  n=re.search(r'name="(Dp[^"]+)"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
  if n and v:s[n[1]]=int(v[1],16)
 code=(OUT/'component.bin').read_bytes()
 assert len(code)<=6144
 print(json.dumps(dict(core_bytes=len(code),core_end=f'{0xa800+len(code):04X}',sha256=D.digest(code)),indent=2))
 return code,s
def overlay():
 code,s=build();base=HOST.with_suffix('.nes').read_bytes();candidate=bytearray(base)
 prg=((base[4]|((base[9]&15)<<8))*16384)
 spans=[('CORE86/A800',16+86*8192+0x800,code,0xff),
        ('ART85/C900',16+85*8192+0x900,(OUT/'art.bin').read_bytes(),0xff),
        ('CHR788..795',16+prg+788*1024,(OUT/'chr.bin').read_bytes(),0)]
 facts=[];allowed=set()
 for name,start,data,fill in spans:
  assert base[start:start+len(data)]==bytes([fill])*len(data),('occupiedApprovedSpan',name)
  candidate[start:start+len(data)]=data;allowed.update(range(start,start+len(data)))
  facts.append(dict(name=name,file_offset=start,bytes=len(data),sha256=D.digest(data)))
 changed=[i for i,(a,b)in enumerate(zip(base,candidate))if a!=b]
 assert len(base)==len(candidate)and set(changed)<=allowed
 assert base[:16]==candidate[:16]
 p=OUT/'candidate.nes';p.write_bytes(candidate)
 proof=dict(status='PRIVATE_SPARSE_COMPONENT_ONLY_NOT_PLAYABLE_OR_NATIVE_QUALIFIED',
  parent=D.binding(HOST.with_suffix('.nes')),candidate=D.binding(p),spans=facts,
  changed_bytes=len(changed),all_other_bytes_exact=True,core_end=f'{0xa800+len(code)-1:04X}',
  component_debug=D.binding(OUT/'component.dbg'),parent_debug=D.binding(HOST.with_suffix('.dbg')),
  debug_contract='Separate genuine component labels plus unchanged parent labels; no relabeled whole-candidate DBG or fake hook aliases',
  limits='No shared menu/dispatch/ABI/lifecycle/audio/collision consumer integration; never launch this sparse ROM as a playable candidate')
 q=OUT/'layout-controls.json';q.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(layout=D.binding(q),candidate=D.binding(p)),indent=2))
if __name__=='__main__':overlay()if '--overlay'in sys.argv else build()
