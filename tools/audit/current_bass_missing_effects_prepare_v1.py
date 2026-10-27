"""Prepare Bass Hard's two missing effect images; no emulator or game changes."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_inventory_powerups_prepare_v1 import main as base_prepare
from observe_chip_committed_write import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
EXPECTED='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
GATE=" if(index==2 or index==4)and(rec.allocation_dma==nil or dmas<rec.allocation_dma+2 or not rec.sampled)then return end\n"

def item_preflight(items):
 fields=('id','cost','initial_ammo','max_ammo','selectable','auto_equip','contact_type','damage_type','sfx')
 assert set(items)==set(range(9))
 lines=['local C=assert(CURRENT_INVENTORY_POWERUPS)',
        'assert(type(C.items)=="table","Numeric source item table before fixture load")']
 for item in range(9):
  row=items[item];assert set(row)==set(fields)|{'hud_name'} and row['id']==item and len(row['hud_name'])==7
  ref='C.items['+str(item)+']'
  lines.append('assert(type('+ref+')=="table","Numeric source item '+str(item)+' before fixture load")')
  lines.append('assert(C.items['+lua(str(item))+']==nil,"No string-key source item '+str(item)+'")')
  for field in fields:
   value=row[field];assert type(value)is int
   expr=ref+'['+lua(field)+']'
   lines.append('assert(type('+expr+')=="number"and '+expr+'=='+str(value)+',"Source item '+str(item)+' '+field+'")')
  expr=ref+'["hud_name"]'
  lines.append('assert(type('+expr+')=="table"and #'+expr+'==7,"Source item '+str(item)+' seven HUD glyphs")')
  for index,value in enumerate(row['hud_name'],1):
   assert type(value)is int
   at=expr+'['+str(index)+']'
   lines.append('assert(type('+at+')=="number"and '+at+'=='+str(value)+',"Source item '+str(item)+' HUD glyph '+str(index)+'")')
 lines.append('for key in pairs(C.items)do assert(type(key)=="number"and key%1==0 and key>=0 and key<=8,"Only nine numeric source items")end')
 return '\n'.join(lines)+'\n'

def source_lifetime(b,cfg):
 rows=[]
 for item in [2,4]:
  q=Arena(b,9);q.invoke('InventoryInit')
  q.put(PlayerStatus=0,OperMode_Task=3,CrossoverBehaviorVersion=1,Player_X_Position=64,Player_PageLoc=0,MmOldX=64,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255)
  # Source-only isolated legal acquisition and native selection; no PPU/NMI.
  for reward in [0,item]:
   q.put(InvObject=5);q.set('InvPickupOwner',9,5);q.set('InvPickup',reward,5);q.invoke('InventoryCollect',x=5)
   if reward==0:
    for _ in range(60):q.invoke('GuestPowerupUpdate')
  for _ in range(9):
   if q.get('InvSelected',9)==item:break
   q.invoke('InventoryCycle')
  assert q.get('InvSelected',9)==item
  before=q.get('InvAmmo',144+item);path=[]
  for tick in range(12):
   q.put(InvFresh=64 if tick==0 else 0,SavedJoypadBits=64 if tick<3 else 0,A_B_Buttons=64 if tick<3 else 0)
   q.invoke('SpecialWeapons')
   shots=[i for i in range(10)if q.get('RgShotType',i)==cfg['items'][item]['contact_type'] and q.get('SsHidden',i)==0]
   assert len(shots)==1
   i=shots[0];x=q.get('RgShotX',i);y=q.get('RgShotY',i)
   assert q.get('RgShotPage',i)==0 and q.get('RgShotYHigh',i)==1 and 94<=x<=136 and y==195
   assert q.get('SsArt',i)in ([address(b,'SS_ART_METAL15'),address(b,'SS_ART_METAL15')+1]if item==2 else[address(b,'SS_ART_PHARAOH50')])
   path.append(dict(update=tick+1,type=q.get('RgShotType',i),age=q.get('RgShotAge',i),x=x,y=y,art=q.get('SsArt',i)))
  assert q.get('InvAmmo',144+item)==before-cfg['items'][item]['cost']
  rows.append(dict(item=item,name='METAL'if item==2 else'PHARAOH',contact_type=cfg['items'][item]['contact_type'],before_ammo=before,after_ammo=q.get('InvAmmo',144+item),target_absent=True,live_updates=path))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.rom=a.rom.resolve();a.output=a.output.resolve();assert a.expected_sha256==EXPECTED and sha(a.rom)==EXPECTED and not a.output.exists()
 original=ROOT/'tests/current-inventory-powerups.lua';raw=original.read_bytes();assert sha(original)=='bcc2419a25ecc0d465dddd3f08b96a212d57c38703c61bbd2c2fddbdd5f24fa2'
 text=raw.decode();needle="local function controlledTarget()\n if rec.target then return end\n"
 assert text.count(needle)==1
 derived=text.replace(needle,needle+GATE,1)
 assert derived.replace(GATE,'',1).encode()==raw,'Only one scoped target-admission line added'
 assert derived[derived.index('-- All callback registration is startup-static.'):]==text[text.index('-- All callback registration is startup-static.'):],'Complete hardware/input/sample/final guards byteexact'
 assert derived.count('emu.write(')==text.count('emu.write(')==2 and derived.count('emu.takeScreenshot(')==1
 saved=sys.argv[:];sys.argv=[str(Path(__file__)),'--rom',str(a.rom),'--expected-sha256',EXPECTED,'--mode','hard','--output',str(a.output)]
 try:base_prepare()
 finally:sys.argv=saved
 cfg=json.loads((a.output/'config.json').read_text());base=json.loads((a.output/'prepared-not-run.json').read_text());cfg['items']={int(k):v for k,v in cfg['items'].items()}
 old=ROOT/'build/current-6be-bass-hard-items-v1';prior=json.loads((old/'native/result.json').read_text())
 assert prior['passed'] and prior['ROM_sha256']==EXPECTED and prior['mode']==1
 assert json.loads((old/'config.json').read_text())==json.loads(json.dumps(cfg)),'Frozen6be gameplay/source config values unchanged'
 for item in [2,4]:
  record=next(r for r in prior['cases']if r['item']==item)
  assert 'sample_skipped'in record and not record.get('sampled')and record['native_cleanup']
 # Genuine source type/table bindings, not the unrelated IceSlasher legacy ID.
 b=scoped_load(a.rom)
 assert address(b,'SS_METAL')==10 and address(b,'SS_PHARAOH')==12
 assert b['raw'][location(b,'SpecialWeapons::Types')+1]==10 and b['raw'][location(b,'SpecialWeapons::Types')+3]==12
 lifetimes=source_lifetime(b,cfg)
 fixture=a.output/'current-bass-missing-effects.lua';fixture.write_bytes(derived.encode());put(a.output/'config.json',cfg)
 preflight=item_preflight(cfg['items']);literal=lua(cfg['items'])
 assert all(('['+str(i)+']=')in literal and('["'+str(i)+'"]=')not in literal for i in range(9))
 run='CURRENT_INVENTORY_POWERUPS='+lua(cfg)+'\n'+preflight+'dofile([=['+fixture.as_posix()+']=])\n'
 assert run.index(preflight)<run.index('dofile(')
 (a.output/'run.lua').write_text(run,newline='\n')
 proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=EXPECTED,original_fixture_sha256=sha(original),generated_fixture_sha256=sha(fixture),single_added_line=GATE.strip(),exact_reverse_to_original=True,all_hardware_controller_setup_assertion_and_sample_blocks_unchanged=True,preflight_assertions=preflight.count('assert('),numeric_items=list(range(9)),all_native_config_values_equal_frozen6be=True,source_lifetime_controls=lifetimes,nomenclature='Bass item2 is METAL/type10/MetalArt; not IceSlasher. Item4 is short PHARAOH/type12.',admission='Only IDs2/4 wait for actual allocation+two completed DMAs AND the existing endFrame sample. The sample latch is necessary because a GameLoop can run after the second DMA but before that endFrame capture. Next actual GameLoop can stage the same original live-effect-aligned target; no effect/ownership/ammo/outcome writes added.',limits='Twelve uninterrupted assembled source updates confirm available range/active intended art without a target. This is not twelve native frames or DMA/capture proof. If the live sample cannot occur, target admission stays closed and original bounded contact assertion fails; no stale/fallback image.',caps=dict(frames=16000,bytes=2000000000,files=64,screenshots=8))
 put(a.output/'extension-source-controls.json',proof)
 paths={v['path']:v for v in base['bindings']if Path(v['path']).name!='prepared-not-run.json'}
 for f in [Path(__file__).resolve(),ROOT/'tools/audit/observe_chip_committed_write.py',fixture,a.output/'extension-source-controls.json',a.output/'config.json',a.output/'run.lua',old/'prepared-not-run.json',old/'config.json',old/'native/result.json']:
  paths[str(f.resolve())]=dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)
 for v in paths.values():assert sha(v['path'])==v['sha256'],v['path']
 final={k:v for k,v in base.items()if k!='bindings'}
 final.update(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,missing_samples_only=[2,4],derivative_fixture=str(fixture),original_fixture_sha256=sha(original),source_controls=str(a.output/'extension-source-controls.json'),base_source_controls=str(a.output/'source-controls.json'),all_other_fixture_bytes_unchanged=True,bindings=list(paths.values()))
 put(a.output/'prepared-not-run.json',final)
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),fixture_sha256=sha(fixture),source_lifetime_cases=len(lifetimes),preflight_assertions=proof['preflight_assertions'])))
if __name__=='__main__':main()
