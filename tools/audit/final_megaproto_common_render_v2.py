"""Current0a common-special immediate art owner proof; source/Lua only."""
from pathlib import Path
import argparse,copy,hashlib,json,sys
import final_samus_hard_gallery_source_v1 as source
from final_samus_hard_gallery_source_v1 import TraceArena,OWNER_NAMES
from final_megaproto_common_source_v2 import D,R,B,SHA
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def records(b):
 def record(ptr,bank):
  off=16+bank*8192+ptr%8192;n=b['raw'][off];assert n%4==0 and n<=252;return dict(address=ptr,bank=bank,bytes=list(b['raw'][off:off+1+n]))
 def named(n):return record(address(b,n),(location(b,n)-16)//8192)
 effects=[]
 for i in range(address(b,'SsArtRightHi')-address(b,'SsArtRightLo')):
  effects.append([record(b['raw'][location(b,'SsArt'+side+'Lo')+i]+256*b['raw'][location(b,'SsArt'+side+'Hi')+i],b['raw'][location(b,'SsArtBanks')+i]&127)for side in['Right','Left']])
 return dict(effect_records=effects,native_brick=named('SsNativeBrick'),native_chunk=named('SsNativeChunk'),buster_record=named('XgBASSWeapon0Right'))
def compiled(b,cfg):
 active=None;wanted=['SpecialDrawShots','SpecialDrawShots::Coordinates','SpecialDrawWaterShot','MetaspriteRenderLoop','RemainingDraw','RemainingDraw::Shot'];pcs={n:(address(b,n),(location(b,n)-16)//8192)for n in wanted}
 for n in wanted:
  if n not in OWNER_NAMES:OWNER_NAMES.append(n)
 class Spy(NesMPU):
  def step(c):
   q=active;bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;here=(c.pc,bank,c.sp)
   for z in list(q.pending_water):
    if here==tuple(z['endpoint']):z['after']=q.get('CurrentOAMOffset');z['returned']=dict(pc=c.pc,bank=bank,sp=c.sp);q.pending_water.remove(z)
   if(c.pc,bank)==pcs['SpecialDrawShots::Coordinates']:
    slot=q.get('RgSlot');typ=q.get('RgShotType',slot);art=q.get('SsArt',slot);face=q.get('RgShotDir',slot);ptr=q.get('R0')+256*q.get('R1');cb=q.m.banks[2];expected=(cfg['native_chunk']if typ==21 else cfg['native_brick'])if art==0 else cfg['effect_records'][art][face==2]
    assert typ>=9 and typ<32 and q.get('SsHidden',slot)==0 and ptr==expected['address']and cb==expected['bank'];actual=[q.m[ptr+i]for i in range(len(expected['bytes']))];assert actual==expected['bytes'];q.coords.append(dict(slot=slot,type=typ,art=art,face=face,pointer=ptr,C_bank=cb,bytes=actual,pc=c.pc,A_bank=bank,sp=c.sp,x=c.x,y=c.y))
   if(c.pc,bank)==pcs['SpecialDrawWaterShot']:
    sp=c.sp;ret=(q.m[256+((sp+1)&255)]+256*q.m[256+((sp+2)&255)]+1)&65535;rb=q.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1;slot=q.get('RgSlot');assert slot==c.x;z=dict(slot=slot,type=q.get('RgShotType',slot),art=q.get('SsArt',slot),hidden=q.get('SsHidden',slot),face=q.get('RgShotDir',slot),before=q.get('CurrentOAMOffset'),endpoint=[ret,rb,(sp+2)&255],pc=c.pc,A_bank=bank,C_bank=q.m.banks[2],sp=sp);q.water.append(z);q.pending_water.append(z)
   # Shot's first genuine instruction is STX AvSlot (three bytes). Observe
   # after that store rather than misreading the old value at EXEC entry.
   if(c.pc,bank)==(pcs['RemainingDraw::Shot'][0]+3,pcs['RemainingDraw::Shot'][1]):q.advanced.append(dict(AvSlot=q.get('AvSlot'),RgSlot=q.get('RgSlot'),pc=c.pc,bank=bank))
   return super().step()
 saved=source.NesMPU;source.NesMPU=Spy;rows=[]
 try:
  for face in[1,2]:
   for item,stock in[(1,8),(2,4),(3,8),(4,12),(5,4),(6,4),(7,16)]:
    q=TraceArena(b);active=q;q.coords=[];q.water=[];q.pending_water=[];q.advanced=[];q.put(SelectedCharacter=1,ProtoVariant=0,CrossoverBehaviorVersion=1,PlayerStatus=1,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,PlayerFacingDir=face,TimerControl=0,CurrentOAMOffset=0,FrameCounter=1);q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);q.set('InvSelected',item,1);q.set('InvAmmo',stock,16+item)
    for col in range(16):q.set('Block_Buffer_1',0x54,176+col)
    if item==1:q.set('Block_Buffer_1',0x51,160+(112+8+(10 if face==1 else-10))//16)
    for age in range(141):
     if item==5:bits=132 if age==5 else 4 if age==4 else 0
     elif item==1:bits=64 if age in[5,6,7,8,16,17,18,19]else 0
     elif item==4:bits=64 if 5<=age<84 else 0
     elif item==7:bits=64 if age in[5,6,7,125,126,127]else 0
     else:bits=64 if age in[5,6,7]else 0
     q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits,A_B_Buttons=bits&192,PreviousA_B_Buttons=prior_bits&192 if age else 0,InvPrevious=prior_bits if age else 0,FrameCounter=age);prior_bits=bits;q.invoke('RlUiDispatch')
     if item==5:q.invoke('PlayerMovementSubs')
     q.invoke('ProcFireball_Bubble')
     if age in[6,10,20,65,85,100,130]:q.put(CurrentOAMOffset=0);q.invoke('SpecialDrawShots')
    assert not q.pending_water and not q.advanced
    if item==7:assert any(z.get('after')!=z['before']for z in q.water)
    else:assert q.coords,(item,face)
    rows.append(dict(item=item,face=face,coords=q.coords,water=q.water,calls=q.calls))
  # The advanced route owns AvSlot and must never hit the commonSS emitter.
  q=TraceArena(b);active=q;q.coords=[];q.water=[];q.pending_water=[];q.advanced=[];q.put(SelectedCharacter=4,Player_X_Position=112,Player_PageLoc=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,FrameCounter=1,RgSlot=7);q.set('RgShotType',42,3);q.set('RgShotX',120,3);q.set('RgShotPage',0,3);q.set('RgShotY',144,3);q.set('RgShotYHigh',1,3);q.set('RgShotDir',1,3);q.invoke('SpecialDrawShots');assert not q.coords and not q.water and q.advanced and any(z['AvSlot']==3 and z['RgSlot']==7 for z in q.advanced);foreign=dict(selected=4,type=42,stale_RgSlot=7,actual_advanced=q.advanced,calls=q.calls)
 finally:source.NesMPU=saved
 return dict(passed=True,source_only=True,ROM_sha256=SHA,components=rows,foreign_advanced=foreign,limits='Actual full UI/primary/Special then fullSpecialDrawShots/Cbank/directrender paths. CPU scene/stock seeds, no PPU/NMI/native/pixels/performance verdict. CommonSS uses genuine RgSlot; foreignRemainingDraw owns AvSlot and reaches no commonSS callback.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=D/'current0a-mega-common-source-v2';assert sha(B/'candidate.nes')==SHA;b=scoped_load(B/'candidate.nes');cfg=json.loads((old/'config.json').read_text());before=copy.deepcopy(cfg);cfg.update(records(b));put(a.output/'art-metadata-refresh.json',dict(passed=True,old={n:before[n]for n in records(b)},current={n:cfg[n]for n in records(b)},fresh_genuine_pointer_tables=True));put(a.output/'config.json',cfg);script=(old/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(before)+'\n';assert script.startswith(prefix);(a.output/'run.lua').write_text('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+script[len(prefix):],encoding='utf-8');z=compiled(b,cfg);put(a.output/'compiled-render-controls.json',z)
 refs=[Path(__file__),old/'proof.json',old/'manifest.json',old/'mechanics.lua',B/'candidate.nes',B/'candidate.dbg'];refs+=list(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in refs]));put(a.output/'proof.json',dict(passed=True,source_only=True,native_ready=False,native_run=False,ROM_sha256=SHA,components=14,manifest_sha256=sha(a.output/'manifest.json'),remaining='Feed actual immediate emitter observations through actualLua callbacks, negative skip/body/HUD/slot/return mocks, then final seed/startup/runtime readiness.'));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),coordinate_observations=sum(len(z['coords'])for z in z['components']),water_returns=sum(len(z['water'])for z in z['components'])),indent=2))
if __name__=='__main__':main()
