"""Compose source-assembled private Tank candidate; no shared install/admission."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_graft_1101_v5 import O,P,PIN,V2,LOANS
from prepare_mario_tank_visible_1101_v5 import labels
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN;raw=bytearray(b['raw']);ls=labels(O/'graft.lbl');patches=[]
 def patch(at,old,new,owner,source):
  assert len(old)==len(new)and raw[at:at+len(old)]==old,(owner,hex(at));assert not any(q['file_offset']<at+len(old)and q['file_offset']+q['length']>at for q in patches),(owner,'overlapping proposal')
  raw[at:at+len(new)]=new;patches.append(dict(owner=owner,file_offset=at,length=len(new),old_hex=old.hex(),new_hex=new.hex(),source=source))
 def call(pc,bank,tail=False):
  safe=address(b,'SafecallA_SMC')+1;target=address(b,'FarcallJmpTarget_SMC');common=address(b,'FarCallCommon')
  return bytes([0x8d,safe&255,safe>>8,0xa9,pc&255,0x8d,(target+1)&255,(target+1)>>8,0xa9,pc>>8,0x8d,(target+2)&255,(target+2)>>8,0xa9,bank,0x4c if tail else 0x20,common&255,common>>8])
 for row in json.loads((O/'graft-assembly.json').read_text())['source_owner_intervals']:
  blob=(O/(row['name']+'.bin')).read_bytes();at=16+8192*row['bank']+row['physical_offset'];patch(at,bytes([255])*len(blob),blob,row['name'],'source-assembled graft.s / exact named-source caps required')
 for page,file in [(501,'code501.bin'),(502,'art-code502.bin')]:
  at=1048592+1024*page;patch(at,bytes(raw[at:at+1024]),(O/file).read_bytes(),f'CHR{page}','Granted Tank code/shoe carrier; exact consumer closure-v10')
 targetmap=dict(MtHostContact=('MtRomContactV3',78),MtHostInjury=('MtRomInjuryV3',58),MtHostMovement=('MtRomMovementAllV3',73),MtHostBeginPowerup=('MtRomBeginPowerupV3',35),MtHostGrowthUpdate=('MtRomGrowthV3',12),MtTerrainHeadProbe=('MtRomHeadV3',89),MtTerrainSideProbe=('MtRomSideV3',33))
 for row in json.loads((V2/'compiled-call-map.json').read_text())['patches']:
  name,bank=targetmap[row['new_owner']];old=bytes.fromhex(row['old_hex']);tail=old[15]==0x4c or len(old)==27;new=call(ls[name],128|bank,tail)+bytes([0xea])*(len(old)-18)
  patch(row['file_offset'],old,new,name,'Original host owning-source edit / same callback footprint, all fixed head mirrors')
 for oldname,newname,bank,tail,scope in [('ThSceneInit','MtFreshV5',78,False,'KrSceneInit'),('HuDrawAll','MtDrawAllV5',86,False,None),('MaaReservation','MtReservationV5',66,True,'PlayerOAMReservation'),('KrMenuResolve','MtMenuResolveV4',66,True,'FmResolve::Native')]:
  old=call(address(b,oldname),128|((location(b,oldname)-16)//8192),tail)
  if scope:at=location(b,scope);assert b['raw'][at:at+18]==old,(scope,b['raw'][at:at+18].hex(),old.hex())
  else:
   found=[i for i in range(16,1048592)if b['raw'].startswith(old,i)];assert len(found)==1,(oldname,found);at=found[0]
  patch(at,old,call(ls[newname],128|bank,tail),newname,f'{scope or "game.s::NoLagSoDraw"}: replace same18B owning farcall target')
 # Add native alternate7 inside the source-owned existing32B cycle capsule.
 at=location(b,'KmNextVariant');old=bytes(raw[at:at+32]);assert old[4]==7 and old[16:23]==bytes([1,5,3,4,0,6,2])
 new=bytearray(old);new[4]=8;new[16:24]=bytes([1,5,3,4,7,6,2,0]);new[24:]=bytes([0xea])*8
 patch(at,old,bytes(new),'KmNextVariant','kamikaze_mario.s: CPX8; Cycle8; existing padding9→8; public PCs unchanged')
 at=location(b,'BmName');old=bytes(raw[at:at+26]);assert old[12]==0xe0 and old[16]==0xbf;new=bytearray(old);new[12]=ls['MtMarioNamesV5']&255;new[16]=ls['MtMarioNamesV5']>>8
 patch(at,old,bytes(new),'BmName','kamikaze_mario.s: relocate three16B names into granted81 named alignment gap')
 start=location(b,'KmQueueName');end=location(b,'BmName');old=bytes(raw[start:end]);at=old.find(bytes([0xc9,7,0xb0]));assert at>=0 and old.count(bytes([0xc9,7,0xb0]))==1
 patch(start+at+1,bytes([7]),bytes([8]),'KmMarioName','kamikaze_mario.s: admit5/6/7 to same native BmName arithmetic')
 at=location(b,'BmName::Names');old=bytes(raw[at:at+32]);assert old==bytes(36 if c==32 else c-55 for c in b'     TOAD            PEACH      ')
 patch(at,old,bytes([0xea])*32,'BmName::Names retired','kamikaze_mario.s: old two-name32B becomes genuine padding; all old names retained in81 proposal')
 # The existing fixed publication predicate has exactly16B. Its native0/1
 # and Maaa2 behavior remains; all higher Mario variants now retain the last
 # complete sprite/CHR epoch during lag. Public following PCs do not move.
 at=location(b,'MaaLagChrGuard');old=bytes(raw[at:at+16]);assert old==bytes.fromhex('ad0260d007ad0a73c902d00238601860')
 selected=address(b,'SelectedCharacter');variant=address(b,'MarioVariant');new=bytes([0xad,selected&255,selected>>8,0xd0,6,0xad,variant&255,variant>>8,0xc9,2,0x60,0x38,0x60,0xea,0xea,0xea])
 patch(at,old,new,'MaaLagChrGuard','game.s: native0/1 Cclear, guest variants>=2 Cset;16B footprint')
 changed={i for i,(a,z)in enumerate(zip(b['raw'],raw))if a!=z};allowed={i for q in patches for i in range(q['file_offset'],q['file_offset']+q['length'])};assert changed<=allowed
 # No old native changes beyond the explicitly source-sized callbacks;
 # current successor Kirby bytes are not part of any declared patch.
 for row in json.loads((P/'assembly.json').read_text())['patches']:
  at=row['offset'];size=row['size']
  assert b['raw'][at:at+size]==bytes.fromhex(row['new'])
  assert not changed.intersection(range(at,at+size)),('Karnov successor patch overwritten',row['role'])
 inherited=R/'build/kirby-approach-owner-1101-v3/owner-link.json'
 for row in json.loads(inherited.read_text()).get('patches',[]):
  if 'file_offset'in row and 'length'in row:assert not changed.intersection(range(row['file_offset'],row['file_offset']+row['length']))
 (O/'candidate.nes').write_bytes(raw)
 result=dict(passed=True,private_candidate_sha256=sha(raw),base_ROM_sha256=PIN,changed_bytes=len(changed),all_changes_in_declared_source_spans=True,patches=patches,menu_alternates=8,private_admission_only=True,full_owning_relink=False,remaining_resources_ungranted=True,native_Mesen=False,installed=False,scope='Source-assembled fragments plus exact compiler-sized native owning substitutions. Temporary private candidate for full Main checks; source owner grants/caps, conditional RAM lifecycle and final source relink must pass before integration or delivery.',bindings={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'candidate-patches.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['patches','bindings','scope']}))
if __name__=='__main__':main()
