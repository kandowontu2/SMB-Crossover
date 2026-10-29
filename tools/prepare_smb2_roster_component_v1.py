"""Sparse SMB2 component. Two existing main segments plus separate CHR object."""
from pathlib import Path
import json,re,subprocess
import prepare_smb2_roster_native_v1 as D
ROOT=D.ROOT;OUT=D.OUT
HOST=ROOT/'build/roster-shared-celeste-small-v1'
EXPECTED={'nes':'d52eeefe78c5f050d276a833c651456b717157856d1783b98c131f9da29f8a60',
 'dbg':'30fbabd65c379b48b21b1718f34b1adc8f24338b5dadce679a4e911e34bb9881',
 'lbl':'610836b703b567ef0a0cef4fea974a85278b860a893a94240d4ce43213d03dcb'}
NAMES='''SelectedCharacter NumberofLives AreaAddrsLOffset AreaType WorldNumber SavedJoypadBits GamePauseStatus OperMode
 GameEngineSubroutine TimerControl Player_Rel_XPos Player_Y_Position Player_Y_HighPos ScreenLeft_X_Pos
 ScreenLeft_PageLoc GetBlockBufferAddr MTileAttribute R0 R1 R2 R3 R4 R5 R6 R7
 Player_X_Position Player_X_Scroll Player_PageLoc Player_Y_Speed Player_X_Speed Player_XSpeedAbsolute
 PlayerFacingDir Player_State PlayerSize PlayerStatus CrouchingFlag CrossoverBehaviorVersion
 CurrentBankC Player_SprAttrib Player_Pos_ForScroll SmPosePtr SmChrBank ObjectMetasprite
 SafecallA_SMC FarcallJmpTarget_SMC FarCallCommon X5SetPhysicalChr MetaspriteRenderLoop
 PowerUpType StarInvincibleTimer MmDeathFlag BlockBufferColli_Head BlockBufferColli_Side
 Enemy_Flag Enemy_State Enemy_ID Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos'''.split()


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
 pre='\n'.join(f'{n}=${s[n]:04x}'for n in NAMES+['MTILE_SOLID','METASPRITE_SAMUS_BODY'])+'\n.macpack longbranch\n'
 (OUT/'component.s').write_text(pre+'.include "smb2_roster.s"\n')
 (OUT/'asset.s').write_text('.segment "SMB2_ROSTER_CHR"\n.incbin "chr/characters/smb2-roster.chr"\n')
 art=str((OUT/'art.bin').resolve()).replace('\\','/');ch=str((OUT/'chr.bin').resolve()).replace('\\','/')
 (OUT/'component.cfg').write_text('MEMORY { K:start=$A637,size=$19C9,bank=118,file=%O; A:start=$CD16,size=$08EA,bank=80,file="'+art+'"; C:start=$C7000,size=$3000,file="'+ch+'"; }\nSEGMENTS { PARODIUS_BELLS:load=K,type=ro; CD_GFX:load=A,type=ro; SMB2_ROSTER_CHR:load=C,type=ro; }\n')
 cc=ROOT/'tools/Windows/cc65/bin'
 commands=[[str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(OUT/'component.s'),'-o',str(OUT/'component.o')],
 [str(cc/'ca65.exe'),'-g','-I',str(ROOT),str(OUT/'asset.s'),'-o',str(OUT/'asset.o')],
 [str(cc/'ld65.exe'),'-C',str(OUT/'component.cfg'),'-o',str(OUT/'component.bin'),'-Ln',str(OUT/'component.lbl'),
 '--dbgfile',str(OUT/'component.dbg'),str(OUT/'component.o'),str(OUT/'asset.o')]]
 for cmd in commands:
  q=subprocess.run(cmd,capture_output=True,text=True)
  if q.returncode:
   p=OUT/'first-build-failure.txt'
   if not p.exists():p.write_text(q.stdout+q.stderr)
   raise RuntimeError(q.stdout+q.stderr)
 s.update(labels(OUT/'component.lbl'))
 for line in (OUT/'component.dbg').read_text().splitlines():
  if not line.startswith('sym\t'):continue
  n=re.search(r'name="(S2[^"]+)"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
  if n and v:s[n[1]]=int(v[1],16)
 code=(OUT/'component.bin').read_bytes();art=(OUT/'art.bin').read_bytes();ch=(OUT/'chr.bin').read_bytes()
 assert len(code)<=6601 and len(art)<=2282 and len(ch)==12288
 return s,code,art,ch


def overlay():
 s,code,art,ch=build();base=HOST.with_suffix('.nes').read_bytes();candidate=bytearray(base)
 prg=(base[4]|((base[9]&15)<<8))*16384
 spans=[('CORE118/A637 prefix9FF',16+118*8192+0x637,code,255),
 ('ART80/CD16 prefix234FF',16+80*8192+0xd16,art,255),('CHR796..807',16+prg+796*1024,ch,0)]
 allowed=set();facts=[]
 for name,start,data,fill in spans:
  assert base[start:start+len(data)]==bytes([fill])*len(data),(name,'occupied')
  candidate[start:start+len(data)]=data;allowed.update(range(start,start+len(data)))
  facts.append(dict(name=name,file_offset=start,bytes=len(data),sha256=D.digest(data)))
 changes=[i for i,(a,b)in enumerate(zip(base,candidate))if a!=b]
 assert set(changes)<=allowed and base[:16]==candidate[:16]and len(base)==len(candidate)
 p=OUT/'candidate.nes';p.write_bytes(candidate)
 q=OUT/'layout-controls.json';q.write_text(json.dumps(dict(status='PRIVATE_STANDALONE_NO_SHARED_HOOKS_NO_NATIVE',parent=D.binding(HOST.with_suffix('.nes')),candidate=D.binding(p),
  parent_debug=D.binding(HOST.with_suffix('.dbg')),component_debug=D.binding(OUT/'component.dbg'),
  core_start='A640',core_end='%04X'%(0xa637+len(code)-1),core_bytes=len(code)-9,
  art_start='CE00',art_end='%04X'%(0xcd16+len(art)-1),art_bytes=len(art)-234,
  spans=facts,changed_bytes=len(changes),all_other_bytes_exact=True,separate_CHR_object=True,
  limits='Standalone APIs only. Root owns raw25 dispatch, menu/newgame BEFORE Ready, NMI clock hook, Main-end timers, actor epochs/contact/carry drawing and palette composition. No whole-game/native evidence.'),indent=2)+'\n')
 old=ROOT/'build/roster-shared-rcr-adopted-v8.nes';a=old.read_bytes()
 changed=[i for i,(x,y)in enumerate(zip(a,base))if x!=y]
 assert len(changed)==51 and set((i-16)//8192 for i in changed)=={81,98}
 (D.OUT/'parent-rebase.json').write_text(json.dumps(dict(previous_parent=D.binding(old),new_parent=D.binding(HOST.with_suffix('.nes')),
  changed_bytes=51,changed_banks=[81,98],approved_component_spans_disjoint=True,
  action='Fresh sparse build and all finite CPU controls on actual d52; no source-tree overlay or relabeled old result.'),indent=2)+'\n')
 print(json.dumps(D.binding(q),indent=2))
 return s


if __name__=='__main__':overlay()
