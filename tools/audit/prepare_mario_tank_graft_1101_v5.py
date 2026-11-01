"""Measure complete current Tank ROM loader/gate/layout without admission."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN,V2,labels
from prepare_mario_tank_loader_1101_v4 import LOANS as OLD,CONTACT
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
sha=lambda b:hashlib.sha256(b).hexdigest()
LOANS=dict(OLD,MT_LOAD_COPY=(32,0x1e98,104),MT_G37=(58,0x1faa,86),MT_G25=(35,0x1eb6,74),MT_CONTACT=CONTACT,MT_DRAW_GATE=(86,0x7b4,76),MT_NAMES=(81,0x10d0,48))
REF=R/'tools/reference/mario_tank_graft_1101_v5.inc';GATES=R/'tools/reference/mario_tank_shared_gates_1101_v3.inc';LOADER=R/'tools/reference/mario_tank_loader_1101_v4.inc'
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 from check_pending_roster_allocations_1101_v1 import verify_tank_tail_baseline
 grant_root=R/'docs/qa/checkpoints/2026-11-01';granted={};grant_bindings={}
 for name in ['mario-tank-prg31-grant.json','mario-tank-prg32-33-grant.json','mario-tank-prg35-81-86-grant.json','mario-tank-code-tail-grant.json','mario-tank-art-tail-grant.json','mario-tank-music-tail-grant.json']:
  path=grant_root/name;grant=json.loads(path.read_text());assert grant['grant'];grant_bindings[str(path.relative_to(R))]=sha(path.read_bytes())
  if name in ['mario-tank-code-tail-grant.json','mario-tank-art-tail-grant.json','mario-tank-music-tail-grant.json']:verify_tank_tail_baseline(grant)
  for row in grant.get('intervals',[grant]):
   bank=row['physical_PRG_bank'];lo,hi=row['physical_offsets_half_open'];expected=row.get('bank_sha256',row.get('PRG_bank_sha256'))
   assert sha(b['raw'][16+bank*8192:16+(bank+1)*8192])==expected
   granted[bank,lo,hi-lo]=name
 assert all(tuple(v)in granted for v in LOANS.values()) and len(LOANS)==18
 image=(O/'code501.bin').read_bytes()+(O/'art-code502.bin').read_bytes();assert len(image)==2048
 cookie=bytes([0xa7,0xf7,5,1])+hashlib.sha256(image+REF.read_bytes()+GATES.read_bytes()+LOADER.read_bytes()+json.dumps(LOANS,sort_keys=True).encode()).digest()[:12]
 names=['SelectedCharacter','MarioVariant','PlayerStatus','CurrentBankC','ReloadCHRBank','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','R0','R1','OperMode','FamilyMainCommit','DisableScreenFlag','Mirror_PPUMASK','Mirror_PPUCTRL','NmiDisable','HorizontalScroll','VerticalScroll','GbPitRenderEnd']
 targets=['X5PublishChr','KrRetire','KrMenuResolve','BmMarioMovement','S2BoundaryImmunity','CmHostMarioInjury','MarioSourceBeginPowerup','MarioSourcePowerupUpdate','MaaHead','ThSceneInit','MaaReservation','HuDrawAll']
 source='.setcpu "6502"\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in sorted(set(names+targets)))+''.join(f'{n}_BANK={128|((location(b,n)-16)//8192)}\n'for n in targets)
 ls=labels(O/'visible.lbl');source+=''.join(f'{n}=${v:04x}\n'for n,v in ls.items()if n.startswith('Mt'))
 banks=dict(MT_READY_BANK='MT_READY',MT_SIDE_BANK='MT_G21',MT_PRECHECK_BANK='MT_LOAD_PRECHECK',MT_INIT_BANK='MT_LOAD_INIT',MT_COPY_BANK='MT_LOAD_COPY',MT_MAP_BANK='MT_LOAD_MAP',MT_PUBLISH_BANK='MT_LOAD_PUBLISH',MT_RETIRE_BANK='MT_LOAD_RETIRE')
 source+=''.join(f'{n}={128|LOANS[seg][0]}\n'for n,seg in banks.items())
 source+='''.macro MtV4Far Target,RawBank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #RawBank
 jsr FarCallCommon
.endmacro
.macro MtV4FarTail Target,RawBank
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #RawBank
 jmp FarCallCommon
.endmacro
.macro MtGateRawFar Target,RawBank
 MtV4Far Target,RawBank
.endmacro
'''
 gates=GATES.read_text().replace('MT_COOKIE_BYTES',','.join('$%02x'%v for v in cookie)).replace(' txa\n pha\n lda CurrentBankC','MtRomHeaderOnlyV4:\n txa\n pha\n lda CurrentBankC',1).replace('MtRomContactV3,"MT_G31"','MtRomContactV3,"MT_CONTACT"')
 shortcut=next(p for p in json.loads((V2/'compiled-call-map.json').read_text())['patches']if p['old_owner']=='MmNativeSideShortcut');side=bytes.fromhex(shortcut['old_hex']);assert b['raw'][shortcut['file_offset']:shortcut['file_offset']+27]==side;gates=gates.replace('MT_SIDE_BYTES',','.join('$%02x'%v for v in side))
 loader=LOADER.read_text().replace('MT_COOKIE_BYTES',','.join('$%02x'%v for v in cookie))
 loader=loader.replace(' lda #0\n sta R0\n lda #$d6\n sta R1\n MtV4Far MtMapCodeV4',' lda #$d6\n sta R1\nMtTwoRowV5:\n lda #0\n sta R0\n MtV4Far MtMapCodeV4',1)
 loader=loader.replace(' lda #$d6\n sta R1\n MtV4Far MtMapCodeV4',' lda R1\n sec\n sbc #4\n sta R1\n MtV4Far MtMapCodeV4',1)
 loader=loader.replace(' dex\n bne MtVerifyByteV4\n sec',' dex\n bne MtVerifyByteV4\n lda R1\n cmp #$de\n bne MtTwoRowV5\n sec',1)
 loader=loader.replace(' lda #245\n sta $512b',' lda R1\n cmp #$da\n lda #245\n adc #0\n sta $512b',1)
 source+=gates+'\n'+loader+'\n.charmap $20,$24\n.repeat 26,I\n.charmap $41+I,10+I\n.endrepeat\n'+REF.read_text()
 exports=['MtColdLoadV4','MtColdAllowedV4','MtLoadWorkerV4','MtCopyRowV4','MtMapCodeV4','MtPublishHeaderV4','MtRetireV4','MtMenuResolveV4','MtRomHeaderOnlyV4','MtRomReadyV3','MtRomMovementAllV3','MtRomContactV3','MtRomSideV3','MtRomInjuryV3','MtRomBeginPowerupV3','MtRomGrowthV3','MtRomHeadV3','MtFreshV5','MtDrawAllV5','MtReservationV5','MtMarioNamesV5']
 source+='\n.export '+','.join(exports)+'\n.assert GbPitRenderEnd<=$df69,lderror,"OldPit cap"\n.assert MtColdLoadV4=$bf69,lderror,"Granted31 source start"\n.assert MtColdLoadEndV4<=$c000,lderror,"Granted31 source end"\n'
 (O/'graft.s').write_text(source);mem=[];segments=[]
 for n,(bank,off,size)in LOANS.items():mem.append(f'{n}_M:start=${0xa000+off:04x},size={size},type=ro,file="{(O/(n+".bin")).as_posix()}";');segments.append(f'{n}:load={n}_M,type=ro;')
 (O/'graft.cfg').write_text('MEMORY {\n'+'\n'.join(mem)+'\n} SEGMENTS {\n'+'\n'.join(segments)+'\n}\n')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 for cmd in [[str(cc/'ca65.exe'),'-g','-o',str(O/'graft.o'),str(O/'graft.s')],[str(cc/'ld65.exe'),'-C',str(O/'graft.cfg'),'-o',str(O/'unused-graft.bin'),'-Ln',str(O/'graft.lbl'),str(O/'graft.o')]]:
  guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
 spans=[]
 for s in b['segs'].values():
  if 'ooffs'in s and Path(s['oname'].strip('"')).resolve()==(P/'candidate.nes').resolve():spans.append((int(s['ooffs'],0),int(s['ooffs'],0)+int(s['size'],0),s['name'].strip('"')))
 rows=[]
 for name,(bank,off,size)in LOANS.items():
  at=16+8192*bank+off;inter=[n for a,z,n in spans if a<at+size and z>at];assert not inter,(name,inter);assert b['raw'][at:at+size]==bytes([255])*size
  blob=(O/(name+'.bin')).read_bytes();assert len(blob)<=size
  rows.append(dict(name=name,bank=bank,physical_offset=off,run_PC=0xa000+off,used=len(blob),requested_bytes=size,remaining=size-len(blob),sha256=sha(blob),ROM_preimage_sha256=sha(b['raw'][at:at+size]),PRG_bank_sha256=sha(b['raw'][16+8192*bank:16+8192*(bank+1)]),formal_grant=True,grant=granted[bank,off,size]))
 (O/'cookie.bin').write_bytes(cookie)
 result=dict(passed=True,current_ROM_sha256=PIN,source_owner_intervals=rows,all_fragment_bytes=sum(r['used']for r in rows),loader_bytes=sum(r['used']for r in rows if r['name'].startswith('MT_LOAD_')),all_guards_bytes=sum(r['used']for r in rows if not r['name'].startswith('MT_LOAD_')and r['name']not in['MT_NAMES','MT_MENU_RESOLVE']),menu_resolve_bytes=79,code_image_bytes=2048,conditional_RAM2=dict(context=[0x880,0x88c],code_metadata_art=[0x1600,0x1e00],cookie=[0x1fe0,0x1ff0],lease_granted=False),all_PRG_granted=False,owning_link=False,native=False,installed=False,commands=commands,bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in[REF,GATES,LOADER,Path(__file__)]})
 result['all_PRG_granted']=True;result['conditional_RAM2']['lease_granted']=True
 result['bindings'].update(grant_bindings)
 ram=grant_root/'mario-tank-ram-grant.json';assert json.loads(ram.read_text())['grant'];result['bindings'][str(ram.relative_to(R))]=sha(ram.read_bytes())
 (O/'graft-assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,bytes=result['all_fragment_bytes'],granted_regions=len(rows))))
if __name__=='__main__':main()
