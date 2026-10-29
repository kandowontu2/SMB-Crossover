"""Deferred/native equivalence at adjacent cells and real world/page seams."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_deferred_controls_v1 as d
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/rogue-dawn-host-pipeline-v2'

def main():
 new=d.old.scoped_load(O/'candidate.nes');old=d.old.scoped_load(R/'build/rogue-dawn-host-transactions-v3/candidate.nes')
 rows=[];pending_queries=0;pending_cases=0
 for action,face,wx,vx,tiles in itertools.product([2,3],[0,1],[12,252,256,260,263,264,508],[-3,0,3],[(0x55,0x60),(0x60,0x55),(0x5f,0x51)]):
  pair=[];case_queries=[]
  for b,deferred in [(old,False),(new,True)]:
   m=d.setup(b,action=action,face=face,wx=wx,pad=128|(1 if face==0 else 2))
   m[address(b,'SavedJoypadBits')]=128|(1 if face==0 else 2)
   m[0x5c09]=vx&255;m[0x5c13]=128;m[0x5c16]=3
   for xx in range(0,512,16):d.old.tile(m,xx,175,tiles[(xx//16)&1])
   saved=NesMPU.step
   def observe(c):
    if deferred and c.pc==address(b,'RdHsReadCell') and m.banks[1]==95 and m[0x5c0b]!=255 and m[0x5c17]:
     page,y,x=m[0x5c31],m[0x5c32],m[0x5c33]
     cell=((y&240)-32)|(x>>4)
     case_queries.append(dict(page=page,cell=cell,pending_page=m[0x5c3b],pending_cell=m[0x5c0b]))
     assert (page,cell)!=(m[0x5c3b],m[0x5c0b]),('later source query sees queued cell',action,face,wx,vx,tiles,page,cell)
    saved(c)
   NesMPU.step=observe
   try:
    if deferred:
     c,low,tr=d.call(m,'RdTxMovement',sp=216)
     n=len([v for a,v in m.writes if a==0x5c0b and v!=255]);assert n<=1
     pending_cases+=bool(n)
    else:
     for name in ['RdHsImportPosition','RdHsClockBefore','RdControlStep','RdHsExportPosition','RdTxAfterMovement','RdHsClockAfter']:d.call(m,name,sp=248)
   finally:NesMPU.step=saved
   pair.append(m)
  a,m=pair
  assert all(a[k]==m[k]for k in range(0x5c00,0x5c80) if k not in [0x5c0b,0x5c3b]),(action,face,wx,vx,tiles,'source body/state')
  assert bytes(a[0x5fb0:0x5fb6])==bytes(m[0x5fb0:0x5fb6])
  for name,size in [('Block_Buffer_1',208),('Block_Buffer_2',208),('Block_State',2),('Block_Orig_YPos',2),('Block_PageLoc',2),('Block_X_Position',2),('Block_Y_Position',2),('Block_Metatile',2),('InvPickup',6),('InvPickupOwner',6),('PowerUpType',6),('Enemy_Flag',6),('Enemy_ID',6),('Enemy_State',6),('Player_X_Position',1),('Player_PageLoc',1),('Player_Y_Position',1),('Player_Y_Speed',1),('VRAM_Buffer1',84)]:
   aa,bb=address(old,name),address(new,name)
   assert bytes(a[aa:aa+size])==bytes(m[bb:bb+size]),(action,face,wx,vx,tiles,name,list(a[aa:aa+size]),list(m[bb:bb+size]))
  pending_queries+=len(case_queries);rows.append(dict(action=action,facing=face,world_centerX=wx,VX=vx,adjacent_tiles=list(tiles),later_geometry_queries=len(case_queries),world_X_after=m[address(new,'Player_PageLoc')]*256+m[address(new,'Player_X_Position')]))
 assert pending_cases>0 and pending_queries>0
 proof=dict(passed=True,native_run=False,source_CPU_only=True,ROM_sha256=ref.digest((O/'candidate.nes').read_bytes()),cases=len(rows),queued_cases=pending_cases,actual_later_geometry_queries=pending_queries,matching_queued_cell_queries=0,max_distinct_queued_cells=1,rows=rows,reference_scope='Preserved unsafe immediate transaction25f5 runs at safeSP248 only as behavioral reference, never as an admissible public contract. New actual movement wrapper enters216. All world resources/tile effects are genuine native consumers in authored source arenas.',bindings=[ref.binding(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',R/'build/rogue-dawn-host-transactions-v3/candidate.nes',R/'src/rogue_dawn_control.s',R/'src/rogue_dawn_host_deferred.s']])
 (O/'geometry-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),queued=pending_cases,later_queries=pending_queries)))
if __name__=='__main__':main()
