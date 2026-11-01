"""Build bounded real-host Tank callbacks, without admitting/patching a ROM."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
P=R/'build/menu-wwf-compact-1101-v1';O=R/'build/mario-tank-host-1101-v2'
REF=R/'tools/reference/mario_tank_host_1101_v2.inc'
TERRAIN=R/'tools/reference/mario_tank_terrain_1101_v2.inc'
PIN='e40109ff598e060a4ad384a7cf77bafccfefbe2efa79599f817f832c93fca019'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 O.mkdir(exist_ok=True);b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 text=REF.read_text()+TERRAIN.read_text();names=[]
 for line in text.splitlines():
  if line.startswith('.import '):names+=line[8:].split(',')
 targets=sorted(set(re.findall(r'MtHostFar (\w+)',text)))
 defined=set(re.findall(r'(?m)^(\w+):',text))
 fixtures=dict(MtTerrainSave=0xa880,MtTerrainY=0xa888,MtTerrainA=0xa889,MtRemovedTile=0xa88a,MtTerrainHeadMode=0xa88b)
 names=sorted(set(names+targets+['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon'])-defined-set(fixtures))
 assert address(b,'Sfx_EnemySmack')==8 and address(b,'PiranhaPlant')==13
 assert address(b,'SetPRout')in range(0x8000,0xa000)and address(b,'ChkToStunEnemies')in range(0x8000,0xa000)
 bind='\n'.join(f'{n}=${address(b,n):04x}'for n in names)+'\n'
 bind+='\n'.join(f'{n}=${v:04x}'for n,v in fixtures.items())+'\n'
 bind+='\n'.join(f'{n}_BANK=${((location(b,n)-16)//8192)|128:02x}'for n in targets)+'\n'
 macro='''.macro MtHostFar Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.ident(.concat(.string(Target),"_BANK"))
 jsr FarCallCommon
.endmacro
'''
 # RAM2 D600's A-window alias B600 uses the real FarCallCommon rawbank2.
 # No new mapper thunk or C-window mapping is required by this fixture.
 # Global identity/header admission and authenticated loading are NOT granted.
 source='.setcpu "6502"\n.macpack longbranch\n'+bind+macro+re.sub(r'(?m)^\.import .+\n','',text)
 (O/'host.s').write_text(source);(O/'host.cfg').write_text('MEMORY { A:start=$b600,size=$a00,type=ro,file=%O; } SEGMENTS { MT_HOST:load=A,type=ro; MT_TERRAIN:load=A,type=ro; }\n')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 for cmd in [[str(cc/'ca65.exe'),'-g','-o',str(O/'host.o'),str(O/'host.s')],[str(cc/'ld65.exe'),'-C',str(O/'host.cfg'),'-o',str(O/'host.bin'),'-Ln',str(O/'host.lbl'),'--dbgfile',str(O/'host.dbg'),str(O/'host.o')]]:
  guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
 # Exact owning-source substitutions. No resident growth at these boundaries.
 # Root must fund/place this worker and bind the banked imports before use.
 edits=[
  dict(source='src/collision.s',context='EColl',old='farcall S2BoundaryImmunity',new='farcall MtRomContact',worker='MtHostContact',purpose='Native eligible enemy overlap -> authentic Tank1000point contact defeat.'),
  dict(source='src/collision.s',context='ForceInjury Mario branch',old='farcall CmHostMarioInjury',new='farcall MtRomInjury',worker='MtHostInjury',purpose='Tank boots immunity/native big->small injury; all other variants retain old owner.'),
  dict(source='src/player.s',context='CrossoverMarioMovement',old='farcall BmMarioMovement,jmp',new='farcall MtRomMovement,jmp',worker='MtHostMovement',purpose='Use donor SMB physics through existing CrossoverVanillaMovement.'),
  dict(source='src/player.s',context='PlayerChangeSize',old='farcall MarioSourcePowerupUpdate',new='farcall MtRomGrowthUpdate',worker='MtHostGrowthUpdate',purpose='Native F8/C4 growth milestones; source updater remains otherMario owner.'),
  dict(source='src/mario_source.s',context='MarioSourcePowerupCollision Mario branch',old='farcall MarioSourceBeginPowerup',new='farcall MtRomBeginPowerup',worker='MtHostBeginPowerup',purpose='Native small/big/boots progression independent of Easy/Hard Flash pickup rules.'),
 ]
 sourcebase=R/'build/bt-ready-menu-1031-v2/joint'
 witnesses=[]
 for e in edits:
  path=sourcebase/e['source'];data=path.read_text();assert data.count(e['old'])==1,(e,data.count(e['old']))
  at=data.index(e['old']);witnesses.append(dict(e,path=str(path),sha256=sha(path.read_bytes()),line=data[:at].count('\n')+1,clause=data[max(0,at-100):at+len(e['old'])+100]))
 (O/'owning-source-edits.json').write_text(json.dumps(dict(edits=witnesses,applied_to_shared=False,menu_admission=False,resident_farcall_spans_unchanged=True,ROM_gate_implemented=False,ROM_gate_funded=False,required_gate_contract='Each MtRom entry must admit exact Mario0/variant7 AND a complete authenticated RAM2 header before rawbank2 transfer. Foreign identities tail-call the exact old native owner. Cold loading is forced blank only. Never point a shared call directly at the conditional unloaded worker; compiled-call-map is a preloaded in-memory test only.'),indent=2)+'\n')
 (O/'host-assembly.json').write_text(json.dumps(dict(passed=True,base_ROM_sha256=PIN,component_bytes=(O/'host.bin').stat().st_size,preloaded_RAM2_fixture=True,actual_A2_farcall_transport=True,code_runtime_alias=0xb600,code_physical_offset=0x1600,code_C2_alias=0xd600,code_lease_granted=False,RAM_allocated=0,conditional_RAM_fixture=dict(A2_start=0xa880,C2_start=0xc880,physical_offset=0x880,bytes=12,lease_granted=False,fields=fixtures),commands=commands,source_bindings={str(REF.relative_to(R)):sha(REF.read_bytes()),str(TERRAIN.relative_to(R)):sha(TERRAIN.read_bytes()),str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())},native_imports={n:address(b,n)for n in names}),indent=2)+'\n')
 print(json.dumps(dict(passed=True,component_bytes=(O/'host.bin').stat().st_size,menu_admission=False,code_lease_granted=False)))

if __name__=='__main__':main()
