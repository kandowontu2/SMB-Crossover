"""Route raw36 through its authenticated resident services; menu stays locked."""
import json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
R=S.R;BASE=R/'build/shinobi-scene-1101-v7';O=R/'build/shinobi-route-1101-v8'


def main():
 assert S.sha(BASE/'candidate.nes')=='249d9a7159048ea995b097df7d03f7d3b1182fc460d39fea5f66914e248c704d'
 O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 labels=S.labels(BASE/'resident.lbl')
 assert labels['ShServiceVeneers']==0xaa88 and labels['ShServiceVeneers']+108<0xab00
 names=['SelectedCharacter','FarcallJmpTarget_SMC','NextBank_SMC','HuCommonRestore','HuNativeWorldPalette']
 source=''.join(f'{n}=${address(b,n):04x}\n' for n in names)+f'ShServiceVeneers=${labels["ShServiceVeneers"]:04x}\n'
 source+=(R/'tools/reference/shinobi_route_1101_v8.s').read_text()
 (O/'route.s').write_text(source)
 (O/'route.cfg').write_text('MEMORY { A:start=$a707,size=48,file="'+(O/'gate.bin').as_posix()+'"; B:start=$bfb3,size=26,file="'+(O/'route.bin').as_posix()+'"; } SEGMENTS { GATE:load=A,type=ro; ROUTE:load=B,type=ro; }')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'route.s','-o',O/'route.o'],[cc/'ld65.exe','-C',O/'route.cfg',O/'route.o','-o',O/'unused.bin']]:subprocess.run(list(map(str,cmd)),check=True)
 # Source-defined unreachable HUD padding, already owned by Metal's gate.
 receipt=json.loads((R/'build/metal-storm-palette-1101-v18/assembly.json').read_text())
 gate=next(p for p in receipt['patches'] if p['role']=='Source-explicit unreachable Chip HUD padding')
 at=16+79*8192+0x707;old=bytes.fromhex(gate['new'])
 assert raw[at:at+48]==old+bytes([234])*(48-len(old))
 data=(O/'gate.bin').read_bytes();raw[at:at+48]=data+bytes([234])*(48-len(data))
 at=16+79*8192+0x1fb0
 assert raw[at:at+29]==bytes.fromhex('4c07a76d01988d6c010a6d6c01696d8d6c01a9ce8d62014cb2b8ffffff')
 data=(O/'route.bin').read_bytes();assert len(data)==26
 raw[at+3:at+29]=data
 # Graphics service uses the authenticated ROM-only CHR requester.
 at=16+65*8192+(labels['ShServiceVeneers']-0xa000)+3
 assert raw[at:at+3]==bytes([76,labels['ShDispatch']&255,labels['ShDispatch']>>8])
 raw[at:at+3]=bytes([76,labels['ShChr']&255,labels['ShChr']>>8])
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes')
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in labels.items():
  if n.startswith('Sh') and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 seed=M.fresh(b);M.put(seed,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
 M.invoke(seed,'ShScene')
 g=M.invoke(seed,'HuGraphics');assert g['P']&1
 assert [M.get(seed,'CurrentCHRBank',i) for i in range(4,8)]==[247,248,249,5]
 M.put(seed,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,Player_SprAttrib=0)
 seed.ram[2][0x379]=128;seed.ram[2][0x38f]=224
 draw=M.invoke(seed,'HuDraw');assert draw['P']&1 and M.get(seed,'CurrentOAMOffset')>0
 # Movement's real guard declines outside active gameplay without executing
 # donor callbacks; actual active movement remains a separate integration test.
 M.put(seed,GameEngineSubroutine=0)
 move=M.invoke(seed,'HuMovement')
 # Observe the actual native router's selected bank/target before executing
 # each owner's service. This checks all public rows without manufacturing
 # legal gameplay state for unrelated owners.
 class Routed(Exception):pass
 cpu=M.NesMPU
 class Trace(cpu):
  def step(self):
   if self.pc==address(self.memory.bundle,'HuNativeWorldPalette') and self.memory.rawtags[1]==207:
    raise Routed((207,self.pc))
   if self.pc==address(self.memory.bundle,'FarCallCommon')+3 and self.memory.rawtags[1]==207:
    mem=self.memory
    raise Routed((mem[address(mem.bundle,'NextBank_SMC')+1],mem[address(mem.bundle,'FarcallJmpTarget_SMC')+1]+256*mem[address(mem.bundle,'FarcallJmpTarget_SMC')+2]))
   return super().step()
 def route(bundle,char,row):
  bundle['syms']['ShProbeEntry']=dict(bundle['syms']['HuMovement'],val=str(0xb600+16*row))
  mem=M.fresh(bundle);M.put(mem,SelectedCharacter=char)
  M.NesMPU=Trace
  try:M.invoke(mem,'ShProbeEntry')
  except Routed as result:return result.args[0]
  finally:M.NesMPU=cpu
  raise AssertionError(('Router did not tail-dispatch',char,row))
 prior=scoped_load(BASE/'candidate.nes');routing=0
 for char in [34,35]:
  for row in range(36):
   assert route(prior,char,row)==route(b,char,row),(char,row)
   routing+=1
 for row in range(36):
  assert route(b,36,row)==(193,labels['ShServiceVeneers']+3*row),row
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),gate_bytes=len((O/'gate.bin').read_bytes()),route_bytes=26,
        graphics=g,draw=draw,guarded_movement=move,native_sprites=M.get(seed,'CurrentOAMOffset')//4,
        unchanged_Karnov_Metal_routes=routing,Shinobi_public_routes=36,
        installed=False,menu_unlocked=False,scope='Real HuGraphics/HuDraw/HuMovement routing. Draw executes native renderer; movement only guarded inactive case. All36 Karnov/Metal service routing targets preserved; not a gameplay regression pass.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
