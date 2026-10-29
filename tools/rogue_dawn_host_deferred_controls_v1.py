"""Queue-lifetime/callback equivalence and real192 source caller stress."""
from pathlib import Path
import itertools,json,sys,time
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_transactions_controls_v1 as old
import rogue_dawn_host_services_controls_v1 as service
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address,location
O=R/'build/rogue-dawn-host-deferred-v1';B=O/'candidate.nes'

def call(m,name,sp=192,**kw):
 pc=address(m.bundle,name);bank=(location(m.bundle,name)-16)//8192 if 0xa000<=pc<0xc000 else m.banks[1]
 m.page(1,bank);m[address(m.bundle,'CurrentBank')]=bank|128
 return service.invoke(m,pc,sp=sp,**kw)

def setup(b,action=2,pad=128,gear=0,face=0,wx=128,tile=0x55):
 m=old.make(b);m[0x5fb4]=0x99;m[0x5fb5]=9;m[0x5fb0]=gear;m[0x5c00]=action;m[0x5c2c]=face
 m[0x5c08]=0xfd;m[0x5c14]=0x1a;m[0x5c29]=pad;m[0x5c28]=pad;m[0x5c34]=pad
 m[0x5c03]=27 if action==3 else 12;m[0x5c01]=8 if action==3 else 15;m[0x5c05]=22 if action==3 else 12;m[0x5c06]=m[0x5c05]
 m[0x5c0d]=184 if action==3 else 191;m[0x5c0c],m[0x5c0e]=divmod(wx,256)
 m[address(b,'Player_PageLoc')]=(wx-8)//256;m[address(b,'Player_X_Position')]=(wx-8)&255;m[address(b,'Player_Y_Position')]=m[0x5c0d]-16
 for x in range(max(0,wx-32),min(512,wx+48),16):old.tile(m,x,175,tile)
 return m

def main():
 b=old.scoped_load(B);reference=old.scoped_load(R/'build/rogue-dawn-host-transactions-v3/candidate.nes');counts={};minsp=255
 text=(R/'src/rogue_dawn_control.s').read_text()
 assert text.count('JSR RdControlPhysics')==1
 assert 'Up:jsr RdHostMoveUp\n bcs NextUp\n sec\n ror RdVY\n ror RdVerticalFraction\n jmp Horizontal' in text
 # Once the first leading-edge pixel is blocked, actual compiled Physics
 # immediately leaves Up. All action chains funnel their sole draw/physics
 # invocation through CD6D/CD81; Stand/Aim FOLLOW tails only initialize the
 # new action. D9FE's JSR D144 returns to DA01/RTS, not a second Physics.
 static=dict(only_physics_JSR='RdC_CD81',blocked_branch='Up Cclear ->RORVY/RORfraction/JMPHorizontal',standing='CC70->CD6D; subsequent StandFollow only state initialization',running='DA25->CCC2/CD21->CD6D, or SpringCC36, or WallCD40/CD6B',jumping='DA0A->D015/D052->CD6D, Spring redirects CC36',morph='D144->CD6D, or unmorphD9FE->D144 thenDA01/RTS',aim='D1CE->CD6D; AimFollow only state initialization',dead='D41A->CD6D or D41F countdown only',no_later_queued_cell_probe='At blocked-up current leading top is tileBottom+1. Later horizontal upper probe is current top, strictly below queued row; moveDown cannot be visited after Up in the same Physics. Subsequent original source draw/health/Follow tails do not query that cell.')
 # Complete real action calls across ALL256fresh/held input combinations,
 # admitted actions, facings and gear branch classes. Geometry varies by the
 # cell-boundary proof; this finite campaign supplements, not replaces, CFG.
 n=0;maxwrites=0;maxphysics=0;queues=0
 for action,pad,face,gear in itertools.product([0,1,2,3,4,6,7,8,255],range(256),[0,1],[0,4,16,255]):
  m=setup(b,action,pad,gear,face,wx=128)
  call(m,'RdTxMovementBegin')
  c,l,tr=call(m,'RdControlStep');minsp=min(minsp,l)
  writes=[v for a,v in m.writes if a==0x5c0b]
  physics=sum(pc==address(b,'RdControlPhysics')and bank==124 for pc,bank in tr)
  assert len(writes)<=1 and physics<=1,(action,pad,face,gear,writes,physics)
  assert not any(pc==address(b,'PlayerHeadCollision')for pc,bank in tr)
  maxwrites=max(maxwrites,len(writes));maxphysics=max(maxphysics,physics);queues+=bool(writes);n+=1
 counts.update(exhaustive_action_pad_gear_facing_cells=n,queued_head_cells=queues,max_distinct_pending_writes=maxwrites,max_Physics_calls=maxphysics)
 # Actual source/native final-state equivalence against preserved immediate
 # reference at safe highSP, while the successor admits original192 again.
 comparisons=[]
 for face,wx,tile in itertools.product([0,1],[4,128,252,260,384],[0x51,0x55,0x5f,0x60]):
  pair=[]
  for bundle,sp,deferred in [(reference,248,False),(b,192,True)]:
   m=setup(bundle,face=face,wx=wx,tile=tile)
   if deferred:call(m,'RdTxMovementBegin',sp=sp)
   call(m,'RdControlStep',sp=sp);before=bytes(m[0x5c00:0x5c80])
   call(m,'RdHsExportPosition',sp=sp);c,l,tr=call(m,'RdTxAfterMovement',sp=sp);minsp=min(minsp,l)
   pair.append((m,before))
  a,before0=pair[0];m,before1=pair[1]
  assert all(before0[k]==before1[k]for k in range(128)if k not in[11,59]),(face,wx,tile,'source immediate response')
  assert all(a[k]==m[k]for k in range(0x5c00,0x5c80)if k not in[0x5c0b,0x5c3b]),(face,wx,tile,'source final')
  for name,size in [('Block_Buffer_1',208),('Block_Buffer_2',208),('Block_State',2),('Block_Orig_YPos',2),('Block_PageLoc',2),('Block_X_Position',2),('Block_Y_Position',2),('Block_Metatile',2),('InvPickup',6),('InvPickupOwner',6),('PowerUpType',6),('Enemy_Flag',6),('Enemy_ID',6),('Enemy_State',6),('Player_X_Position',1),('Player_PageLoc',1),('Player_Y_Position',1),('Player_Y_Speed',1),('VRAM_Buffer1',84)]:
   aa=address(reference,name);ma=address(m.bundle,name)
   assert bytes(a[aa:aa+size])==bytes(m[ma:ma+size]),(face,wx,tile,name,list(a[aa:aa+size]),list(m[ma:ma+size]))
  assert m[0x5c0b]==255 and m[0x5c3b]==0
  comparisons.append(dict(facing=face,worldX=wx,tile=tile))
 counts['source_response_native_effect_final_comparisons']=len(comparisons)
 # True source/bridge/constructor IRQ and lagNMI, no fake callbacks. Native
 # transaction is now outside ControlStep and at its real aftermovement entry.
 seams=[]
 for name,bank in [('NativeRarePlayerHeadCollisionCore',9),('SetupPowerUp',9),('NrPrepare',124),('RdNrPrepare',124),('RdTxPrepareActor',95),('RdHsPrepareActor',95)]:
  for kind in ['IRQ','lagNMI']:
   m=setup(b,tile=0x60);call(m,'RdTxMovementBegin');call(m,'RdControlStep');call(m,'RdHsExportPosition')
   c,l,tr=call(m,'RdTxAfterMovement',seam=(address(b,name),bank,kind));minsp=min(minsp,l)
   assert m[0x5c0b]==255 and m[0x5c3b]==0
   seams.append(dict(phase='flush',entry=name,kind=kind,minimum_SP=l))
 for name,bank in [('RdHostCall95',124),('RdHsGeometry',95),('RdTxHead',95),('RdHsDraw',95)]:
  for kind in ['IRQ','lagNMI']:
   m=setup(b);call(m,'RdTxMovementBegin');c,l,tr=call(m,'RdControlStep',seam=(address(b,name),bank,kind));minsp=min(minsp,l)
   seams.append(dict(phase='source_ControlStep',entry=name,kind=kind,minimum_SP=l))
 counts['actual_original192_ISR_seams']=seams
 # Scene/pause/early-return owners must clear both borrowed cells; no native
 # block effect may survive an invalid engine/highY transaction boundary.
 clears=0
 for engine,high in itertools.product([0,3,7,8,11],[0,1,2]):
  m=setup(b);m[0x5c0b]=0x87;m[0x5c3b]=1;call(m,'RdTxMovementBegin');assert m[0x5c0b]==255 and m[0x5c3b]==0
  m[address(b,'GameEngineSubroutine')]=engine;m[address(b,'Player_Y_HighPos')]=high
  call(m,'RdTxAfterMovement');assert m[0x5c0b]==255 and m[0x5c3b]==0;clears+=1
 counts['movement_early_return_clears']=clears
 proof=dict(passed=True,native_run=False,source_only=True,ROM_sha256=ref.digest(B.read_bytes()),entry_SP=192,minimum_SP=minsp,counts=counts,structural_maxone_proof=static,full_GameLoop_admission='OPEN, this is complete ControlStep plus native flush; actual host hook/schedule proof comes next',borrowed_fields={'5C0B':'movement-only cell index; no admitted frozen player read/write','5C3B':'movement-only page; cleared before any bomb/weapon step'},preserved_unsafe_reference='build/rogue-dawn-host-transactions-v3/control-SP192-negative.json',bindings=[ref.binding(p)for p in[Path(__file__),B,B.with_suffix('.dbg'),O/'build.json',R/'src/rogue_dawn_host_deferred.s',R/'src/rogue_dawn_control.s',R/'src/rogue_dawn_weapons.s']])
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cells=n,comparisons=len(comparisons),ISR=len(seams),minimum_SP=minsp)))
if __name__=='__main__':main()
