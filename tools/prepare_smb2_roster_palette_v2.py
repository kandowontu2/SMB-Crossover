"""Small C-window pointer successor; frozen v1's64 bindings stay exact."""
from pathlib import Path
import json,re,subprocess
import prepare_smb2_roster_native_v1 as D
import prepare_smb2_roster_component_v1 as B
import smb2_roster_component_controls_v1 as C
OUT=D.ROOT/'build/smb2-roster-palette-v2'
V1=D.OUT/'handoff.json'
EXPECTED='7c0a857e0bb1f61790df9631b0603cac6ba64df78dfe3a6cb04a87c8f81b1d54'


def main():
 assert D.digest(V1.read_bytes())==EXPECTED
 h=json.loads(V1.read_text());records=h['owned_files']+h['input_bindings']+h['output_bindings']
 for v in records:assert D.binding(v['path'])==v,v['path']
 OUT.mkdir(exist_ok=True)
 s=B.labels(B.HOST.with_suffix('.lbl'));s.update(B.labels(D.OUT/'component.lbl'))
 for line in (D.OUT/'component.dbg').read_text().splitlines():
  if not line.startswith('sym\t'):continue
  n=re.search(r'name="(S2[^"]+)"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
  if n and v:s[n[1]]=int(v[1],16)
 start=int(h['extent']['core_end'],16)+1;artstart=int(h['extent']['art_end'],16)+1
 assert start==0xb89e and artstart==0xd573
 (OUT/'additive.s').write_text('\n'.join(f'{n}=${s[n]:04x}'for n in ['SelectedCharacter','S2NativeCharacter','S2GraphicsBank','R0','R1','R2','R3'])+'\n.include "smb2_roster_palette_v2.s"\n')
 target=str((OUT/'palette.bin').resolve()).replace('\\','/')
 (OUT/'additive.cfg').write_text('MEMORY { K:start=$B89E,size=$0762,bank=118,file=%O; A:start=$D573,size=$008D,bank=80,file="'+target+'"; }\nSEGMENTS { PARODIUS_BELLS:load=K,type=ro; CD_GFX:load=A,type=ro; }\n')
 cc=D.ROOT/'tools/Windows/cc65/bin'
 commands=[[str(cc/'ca65.exe'),'-g','-I',str(D.ROOT/'src'),str(OUT/'additive.s'),'-o',str(OUT/'additive.o')],
  [str(cc/'ld65.exe'),'-C',str(OUT/'additive.cfg'),'-o',str(OUT/'additive.bin'),'-Ln',str(OUT/'additive.lbl'),'--dbgfile',str(OUT/'additive.dbg'),str(OUT/'additive.o')]]
 for command in commands:
  q=subprocess.run(command,capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
 s.update(B.labels(OUT/'additive.lbl'))
 code=(OUT/'additive.bin').read_bytes();data=(OUT/'palette.bin').read_bytes()
 expected=D.original(5)[D.labels()['CharacterPalette']:D.labels()['CharacterPalette']+16]
 assert data==expected+bytes([15,48,22,15])and len(data)==20
 base=Path(h['candidate']['path']).read_bytes();candidate=bytearray(base)
 spans=[(16+118*8192+start-0xa000,code),(16+80*8192+artstart-0xc000,data)]
 allowed=set()
 for p,blob in spans:
  assert base[p:p+len(blob)]==bytes([255])*len(blob)
  candidate[p:p+len(blob)]=blob;allowed.update(range(p,p+len(blob)))
 changed=[i for i,(a,b)in enumerate(zip(base,candidate))if a!=b]
 assert set(changed)<=allowed and base[:16]==candidate[:16]
 dest=OUT/'candidate.nes';dest.write_bytes(candidate)

 def setup(variant=0,bankA=99,bankC=99):
  m=C.init(s,variant=variant);m.rom=bytes(candidate)
  m.bank[1]=bankA;m[s['CurrentBank']]=bankA|128
  m.bank[2]=bankC;m[s['CurrentBankC']]=bankC|128
  m[s['SafecallA_SMC']+1]=0x65
  m[s['FarcallJmpTarget_SMC']+1]=s['S2PalettePointerC']&255
  m[s['FarcallJmpTarget_SMC']+2]=s['S2PalettePointerC']>>8
  m.executions=[]
  return m
 calls=[]
 for variant in range(4):
  for ba in [4,62,99,118]:
   for bc in [4,80,93,99]:
    m=setup(variant,ba,bc);c,_,_=C.execute(m,s['FarCallCommon'],a=246)
    assert c.p&1 and m.bank==[126,ba,80,127]
    assert m[s['CurrentBank']]==ba|128 and m[s['CurrentBankC']]==208
    p=m[s['R0']]|m[s['R1']]<<8;q=m[s['R2']]|m[s['R3']]<<8
    native=[0,3,2,1][variant]
    assert m[p:p+4]==expected[native*4:native*4+4]and m[q:q+4]==bytes([15,48,22,15])
    assert 0xc000<=p<0xe000 and 0xc000<=q<0xe000
    calls.append([variant,ba,bc,c.processorCycles,c.lowest_sp])
 foreign=0
 for char in range(256):
  if char==25:continue
  m=setup();m.bank[1]=118;m[s['CurrentBank']]=246;m[s['SelectedCharacter']]=char;before=bytes(m.ram)
  c,_,_=C.execute(m,s['S2PalettePointerC'])
  assert not c.p&1 and m.bank==[126,118,99,127]
  assert m.ram[:0x100]==before[:0x100]and m.ram[0x200:]==before[0x200:]
  foreign+=1
 baseline=setup();end,_,_=C.execute(baseline,s['FarCallCommon'],a=246,p=0x20)
 points=sorted({p for p,b in baseline.executions if b==118})
 irq=[]
 for pc in points:
  m=setup();c,_,q=C.execute(m,s['FarCallCommon'],a=246,p=0x20,inject=(pc,118))
  assert q is not None
  assert(c.a,c.x,c.y,c.p&0xcf,c.sp)==(end.a,end.x,end.y,end.p&0xcf,end.sp)
  assert m.bank==baseline.bank and m[s['CurrentBank']]==baseline[s['CurrentBank']]and m[s['CurrentBankC']]==baseline[s['CurrentBankC']]
  assert m.ram[0x5c00:0x5c80]==baseline.ram[0x5c00:0x5c80]
  irq.append(hex(pc))
 for v in records:assert D.binding(v['path'])==v,('v1changed',v['path'])
 report=dict(status='PASS_ADDITIVE_SOURCE_CPU_C80_POINTER_NO_NATIVE',frozen_v1=D.binding(V1),all64_v1_bindings_unchanged=True,
  candidate=D.binding(dest),core=[hex(start),hex(start+len(code)-1),len(code)],ART=[hex(artstart),hex(artstart+19),20],
  combined_CORE_bytes=h['extent']['core_bytes']+len(code),combined_ART_bytes=h['extent']['art_bytes']+20,
  API='S2PalettePointerC replaces v1 A-window-pointer interface for ordinary farcall consumers; C80 lease stays intentional, A hardware+shadow return restored.',
  genuine_farcall_readback_cases=calls,foreign_cases=foreign,actual_parent_IRQ_points=irq,
  exact_source_P0=True,eye_object_role='Original world1 role only; no whole-palette publication/all-areaRGB claim',
  limits='No root menu/routing/NMI/audio/PPU/native composition; v1 evidence unchanged, not retagged.',
  owned_files=[D.binding(D.ROOT/p)for p in ['src/smb2_roster_palette_v2.s','tools/prepare_smb2_roster_palette_v2.py','docs/qa/smb2-roster-palette-c80-2026-10-28.txt']],
  outputs=[D.binding(OUT/n)for n in ['candidate.nes','additive.s','additive.cfg','additive.bin','palette.bin','additive.lbl','additive.dbg']])
 p=OUT/'handoff.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(handoff=D.binding(p),core=report['core'],ART=report['ART'],readbacks=len(calls),IRQ=len(irq)),indent=2))


if __name__=='__main__':main()
