"""Owned nine-item Samus fixture extension: a real HUD-overlap jump, no launch."""
from pathlib import Path
import argparse,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from current_samus_powerups_prepare_v1 import main as base_prepare
from observe_chip_committed_write import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')

SETUP=""" elseif phase=='jump-setup'then
  assert(caseIndex==9 and index==254 and rec.native_refill and #records==9,'All nine original earned components completed')
  assert(stock()==8 and r('InvOwnedLo',2)==247 and r('InvOwnedHi',2)==0 and r('InvSelected',2)==2,'Earned final stock/ownership/selection before HUD setup')
  transaction(function()
   arena()
   for col=6,14 do tile(0,col,7,0x54);w('Block_Buffer_1',0x54,5*16+col)end
   w('Player_X_Position',184);w('MmOldX',184);w('Player_Y_Position',80)
  end)
  jump={start_update=updates,setup_dma=dmas,min_y=255,air=false,a_updates=0,ground_sample=false,apex_sample=false,land_sample=false}
  change('jump-settle')
 elseif phase=='use'then controlledTarget()end
"""
FINISH=""" elseif phase:sub(1,5)=='jump-'and phase~='jump-setup'then
  assert(updates-jump.start_update<160,'160 native-update HUD jump bound')
  assert(stock()==8 and r('InvOwnedLo',2)==247 and r('InvOwnedHi',2)==0 and r('InvSelected',2)==2,'HUD jump retains all earned inventory and exact stock8')
  assert(r('Player_X_Position')==184 and r('Player_PageLoc')==0 and r('Player_Y_HighPos')==1,'A-only native jump stays over staged platform')
  assert(r('GuestPowerupActive')==0 and r('SmBall')==0 and r('SmCrouch')==0 and pool()==0,'No transform/form/projectile outcome substituted for jump')
  jump.min_y=math.min(jump.min_y,r('Player_Y_Position'))
  if phase=='jump-settle'then
   if age>=10 then
    assert(r('Player_State')==0 and r('Player_Y_Position')==80,'Ten genuine ground-settle updates on visible/logical platform')
    jump.ground_ready=true
   end
  elseif phase=='jump-air'then
   assert(r('SavedJoypadBits')&127==0,'Only genuine A input during HUD jump')
   if r('A_B_Buttons')&128~=0 then jump.a_updates=jump.a_updates+1 end
   if r('Player_State')~=0 then
    assert(r('SmJumpStartY')==80,'Actual native Samus launch recorded platform origin')
    jump.air=true
    if r('Player_Y_Position')<=28 and jump.apex_dma==nil then jump.apex_dma=dmas end
   elseif jump.air then
    assert(age>=18 and jump.a_updates==18 and r('Player_Y_Position')==80 and jump.min_y<=28,'Actual18-update A jump reaches HUD and lands natively')
    assert(jump.apex_sample,'Real HUD-overlap image after two complete DMAs, no stale fallback')
    jump.land_dma=dmas;jump.land_update=updates;change('jump-land')
   end
  elseif phase=='jump-land'then assert(r('Player_State')==0 and r('Player_Y_Position')==80,'Native landing remains grounded')end
"""
SAMPLES=""" if jump then
  if phase=='jump-settle'and jump.ground_ready and dmas>=jump.setup_dma+2 then
   assert(not screenshot,'Original refill sample cannot be replaced');screenshot='samus-hud-ground.png';jump.ground_sample=true;change('jump-air')
  elseif phase=='jump-air'and not jump.apex_sample and jump.apex_dma~=nil and dmas>=jump.apex_dma+2 then
   assert(r('Player_State')~=0 and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<=28,'Intended HUD-overlap jump remains active two actual DMAs later')
   assert(not screenshot,'Original attack image cannot be replaced');screenshot='samus-hud-apex.png';jump.apex_sample=true;jump.apex_sample_y=r('Player_Y_Position');jump.apex_sample_dma=dmas
  elseif phase=='jump-land'and dmas>=jump.land_dma+2 then
   assert(r('Player_State')==0 and r('Player_Y_Position')==80 and stock()==8 and r('InvOwnedLo',2)==247,'Actual committed grounded landing/earned inventory')
   assert(not screenshot,'Selected image not overwritten');screenshot='samus-hud-land.png';jump.land_sample=true
   assert(jump.ground_sample and jump.apex_sample and jump.land_sample,'All three genuine HUD jump views')
   done=true;change('complete')
  end
 end
"""

def item_preflight(items):
 fields=('id','cost','selectable','auto_equip','sm_type','rg_type','damage_type','expected_owned')
 assert set(items)==set(range(8))
 lines=['local C=assert(CURRENT_SAMUS_POWERUPS)',
        'assert(type(C.items)=="table","Numeric source item table before fixture load")']
 checks=1
 for item in range(8):
  row=items[item];assert set(row)==set(fields)|{'hud_name'}
  assert row['id']==item and len(row['hud_name'])==7
  ref='C.items['+str(item)+']'
  lines.append('assert(type('+ref+')=="table","Numeric source item '+str(item)+' before fixture load")')
  lines.append('assert(C.items['+lua(str(item))+']==nil,"No string-key source item '+str(item)+'")')
  checks+=2
  for field in fields:
   value=row[field];assert type(value)is int
   expr=ref+'['+lua(field)+']'
   lines.append('assert(type('+expr+')=="number"and '+expr+'=='+str(value)+',"Source item '+str(item)+' '+field+'")')
   checks+=1
  expr=ref+'["hud_name"]'
  lines.append('assert(type('+expr+')=="table"and #'+expr+'==7,"Source item '+str(item)+' seven HUD glyphs")');checks+=1
  for index,value in enumerate(row['hud_name'],1):
   assert type(value)is int
   at=expr+'['+str(index)+']'
   lines.append('assert(type('+at+')=="number"and '+at+'=='+str(value)+',"Source item '+str(item)+' HUD glyph '+str(index)+'")');checks+=1
 lines.append('for key in pairs(C.items)do assert(type(key)=="number"and key%1==0 and key>=0 and key<=7,"Only eight numeric source items")end')
 checks+=1
 return '\n'.join(lines)+'\n',checks

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve()
 assert sha(a.rom)==a.expected_sha256 and not a.output.exists()
 original=R/'tests/current-samus-powerups.lua';raw=original.read_bytes();text=raw.decode();assert '\r'not in text
 substitutions=[]
 def replace(old,new):
  nonlocal text
  assert text.count(old)==1,('Unique source substitution',old[:100]);text=text.replace(old,new);substitutions.append((old,new))
 replace('local ctrl=0\n','local ctrl=0\nlocal jump=nil\n')
 replace(" elseif phase=='use'then controlledTarget()end\n",SETUP)
 replace("rec.native_refill=true;rec.completed=wall;screenshot='samus-refill.png';done=true;change('complete')","rec.native_refill=true;rec.completed=wall;screenshot='samus-refill.png';change('jump-setup')")
 replace("  assert(age<480,'Bounded real action/cleanup')\n end\nend)\n-- All callback registration", "  assert(age<480,'Bounded real action/cleanup')\n"+FINISH+" end\nend)\n-- All callback registration")
 replace(" local input={}\n if phase=='use'then", " local input={}\n if phase=='jump-air'then input.a=age<18 end\n if phase=='use'then")
 replace(" if screenshot then\n  assert(images<8,'Eight selected PNGs max')",SAMPLES+" if screenshot then\n  assert(images<11,'Eleven selected PNGs max')")
 replace('  samples[#samples+1]=sample\n','  if jump then sample.hud_jump={min_y=jump.min_y,air=jump.air,a_updates=jump.a_updates,phase=phase,state=r(\'Player_State\'),native_start_y=r(\'SmJumpStartY\'),ground_sample=jump.ground_sample,apex_sample=jump.apex_sample,land_sample=jump.land_sample}end\n  samples[#samples+1]=sample\n')
 replace('cases=records,wall=wall','cases=records,hud_jump=jump,wall=wall')
 restored=text
 for old,new in reversed(substitutions):assert restored.count(new)==1;restored=restored.replace(new,old,1)
 assert restored.encode()==raw,'Exact reverse substitution recovers whole original fixture'
 begin='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered then emu.setInput(menu(),0);return end'
 guard=lambda t:t[t.index(begin):t.index(end,t.index(begin))]
 assert guard(text)==guard(raw.decode()),'Complete full-DMA/NMI/IRQ/CHR/deadline guard block byteexact'
 forbidden=lambda t:t[t.index('local forbidden='):t.index('local function transaction')]
 assert forbidden(text)==forbidden(raw.decode()),'Forbidden writes and safe transaction boundary byteexact'
 assert text.count('emu.write(')==raw.decode().count('emu.write(')==2 and text.count('emu.takeScreenshot(')==1
 assert 'removeMemoryCallback'not in text and 'loadSavestate'not in text and 'setState('not in text
 # Base producer rebinds every existing hook/RAM/metatile/table against the
 # new ROM and executes its genuine original source component controls.
 saved=sys.argv[:];sys.argv=[str(Path(__file__)),'--rom',str(a.rom),'--expected-sha256',a.expected_sha256,'--output',str(a.output)]
 try:base_prepare()
 finally:sys.argv=saved
 b=scoped_load(a.rom);cfg=json.loads((a.output/'config.json').read_text());base_manifest=json.loads((a.output/'prepared-not-run.json').read_text())
 cfg['items']={int(k):v for k,v in cfg['items'].items()}
 item_guard,item_guard_checks=item_preflight(cfg['items'])
 assert lua({0:{'id':0},7:{'id':7}})=='{[0]={["id"]=0},[7]={["id"]=7}}'
 assert lua({'flag':True,'absent':None})=='{["flag"]=true,["absent"]=nil}'
 cfg['limits']+=' Added HUD jump is one staged visible/logical platform component after all nine earned rewards; not natural platform traversal. Ground/apex/land images require full visual review. Three additional PNGs explicitly raise cap8->11, within64files; no container or per-frame images.'
 cfg['hud_jump']=dict(platform=dict(visible_row=7,logical_row=5,columns=list(range(6,15)),metatile=84),start=dict(x=184,y=80),ground_settle=10,A_updates=18,min_y_max=28,update_cap=160,screenshots=11)
 old_ram=set(cfg['ram']);refs=set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'",text))
 for n in refs:cfg['ram'][n]=address(b,n)
 for n,v in cfg['ram'].items():assert address(b,n)==v,('Genuine RAM address',n)
 for k,h in cfg['hooks'].items():
  off=location(b,h['source_symbol'])+h['source_delta'];assert address(b,h['source_symbol'])+h['source_delta']==h['pc']
  for bank in h['banks']:assert list(b['raw'][16+bank*8192+h['pc']%8192:16+bank*8192+h['pc']%8192+len(h['bytes'])])==h['bytes'],('Actual hook bytes',k,bank)
 for name,h in cfg['metatiles'].items():assert (location(b,name)-16)//8192==h['bank'] and(location(b,name)-16)%8192==h['offset']
 solid=address(b,'MTILE_SOLID');assert b['raw'][location(b,'MTileAttribute')+84]&solid
 assert all(n in cfg['setup_allowed']for n in['Player_X_Position','Player_Y_Position','MmOldX','Block_Buffer_1'])
 assert not set(re.findall(r"\bw\('([A-Za-z_][A-Za-z_0-9]*)'",SETUP))-set(cfg['setup_allowed'])
 fixture=a.output/'current-samus-hud-jump.lua';fixture.write_bytes(text.encode());put(a.output/'config.json',cfg)
 item_literal=lua(cfg['items'])
 assert all(('['+str(i)+']=')in item_literal and ('["'+str(i)+'"]=')not in item_literal for i in range(8))
 run_text='CURRENT_SAMUS_POWERUPS='+lua(cfg)+'\n'+item_guard+'for name,value in pairs(CURRENT_SAMUS_POWERUPS.ram)do assert(type(value)=="number"and value>=0 and value<=65535,"ActualRAMaddress:"..name)end\ndofile([=['+fixture.as_posix()+']=])\n'
 assert run_text.index(item_guard)<run_text.index('dofile(') and '["items"]='+item_literal in run_text
 (a.output/'run.lua').write_text(run_text,newline='\n')
 old=R/'build/current-6be-samus-hud-jump-v1'
 original_tool=R/'tools/audit/current_samus_hud_jump_prepare_v1.py'
 assert sha(original_tool)=='9aab3ed53a8e2179754e24212c7189f9fc1c6b782d482c4336c029c47805c75f'
 assert sha(fixture)==sha(old/'current-samus-hud-jump.lua'),'All nine component and jump mechanics byteexact to original v1'
 assert json.loads((a.output/'config.json').read_text())==json.loads((old/'config.json').read_text()),'All actual config values identical; only emitted Lua key types corrected'
 launch=json.loads((old/'launch.json').read_text())
 log=old/'native/samus_fixed_hud_current4a-run.log'
 assert launch['exit_code']==1 and launch['changed_inputs']==[] and 'current-samus-hud-jump.lua:267: attempt to index a nil value' in log.read_text()
 negative_paths=[original_tool]+[old/n for n in ['prepared-not-run.json','config.json','run.lua','current-samus-hud-jump.lua','launch.json','native/samus_fixed_hud_current4a-run.log','native/samus-inventory.csv']]
 put(a.output/'v1-serialization-failure.json',dict(original_outcome=False,game_failure=False,originals_unchanged=True,first_failure='wall463/update90, first mushroom: generated fixture line267 C.items[index].expected_owned has numeric index0 but launcher emitted only string key0.',cause='JSON-load stringifies item keys; v1 current_roster serializer also forced all dictionary keys to strings. Both must be corrected.',correction='Only normalize cfg.items keys0..7 to integers and use existing numeric-key/bool-aware serializer. Execute strict item record/type/values/HUD-glyph checks before fixture load.',new_native_run=False,emitted_preflight_assertions=item_guard_checks,source_configuration_equal=True,generated_fixture_byte_identical=True,retained=[dict(path=str(x.resolve()),sha256=sha(x),bytes=x.stat().st_size)for x in negative_paths]))
 proof=dict(passed=True,SOURCE_ONLY=True,native_run=False,ROM_sha256=a.expected_sha256,original_fixture=dict(path=str(original),sha256=sha(original)),generated_fixture_sha256=sha(fixture),exact_reverse_to_original=True,full_hardware_guard_bytes_equal=True,full_hardware_guard_sha256=hashlib.sha256(guard(text).encode()).hexdigest(),forbidden_and_safe_transaction_bytes_equal=True,original_nine_action_controller_inputs_unchanged=True,original_nine_pickup_property_ammo_assertions_retained=True,new_jump_INPUT_ONLY=True,staged_scene='Only actualGameLoop+5/NmiDisableFF/noIRQ/NMI transaction: existingarena then nine0x54 visible+logical tiles at row7/logical5 cols6..14; position184/80 and originalarena initial zero motion. No ownership/ammo/form/outcome/invulnerability writes.',expected_native='All9 original real components; stock8/owned247/selected2;10settle->A18->minY<=28->nativeground80,160updates; three selected images with actual2DMA delay, no stale substitute.',new_RAM_resolved=sorted(refs-old_ram),emitted_numeric_item_keys=list(range(8)),emitted_preflight_before_fixture=True,emitted_preflight_assertions=item_guard_checks,all_item_record_scalar_and_seven_glyph_values_checked=True,generated_fixture_byte_identical_to_failed_v1=True,CPU_jump_or_native_claim=False,substitution_count=len(substitutions),limitations='Source generator and original source components only. No native jump/timing/image qualification until ROOT runs. Exact18 actual A updates intentionally asserted; lag-induced extra A update is not silently accepted.')
 put(a.output/'extension-source-controls.json',proof)
 paths={str(Path(v['path'])):v for v in base_manifest['bindings']if Path(v['path']).is_file()and Path(v['path']).name not in['source-controls.json','prepared-not-run.json']}
 for f in[Path(__file__).resolve(),R/'tools/audit/observe_chip_committed_write.py',original,fixture,a.output/'source-controls.json',a.output/'extension-source-controls.json',a.output/'v1-serialization-failure.json',a.output/'config.json',a.output/'run.lua',a.output/'command.json']+negative_paths:
  paths[str(f)]=dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)
 for v in paths.values():assert sha(v['path'])==v['sha256'],v['path']
 final=dict(status='PREPARED_DO_NOT_RUN',native_run=False,ROM_sha256=a.expected_sha256,original_fixture_sha256=sha(original),original_v1_failure_preserved=True,configuration_key_typing_only_correction=True,emitted_item_preflight_before_fixture=True,all_nine_components_retained=True,physical_mature_only=True,no_block_emergence_claim=True,no_tested_outcomes_seeded=True,caps=dict(frames=16000,jump_updates=160,bytes=2000000000,files=64,screenshots=11),outputs='OneCSV +result/metadata +original8 and3newselected PNGs max; no container/per-frame images or source/runtime/ROM copies.',source_controls=str(a.output/'extension-source-controls.json'),base_source_controls=str(a.output/'source-controls.json'),ROOT_native_lease_required=True,bindings=list(paths.values()))
 put(a.output/'prepared-not-run.json',final)
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),ROM_sha256=a.expected_sha256,generated_fixture_sha256=sha(fixture),screenshots=11)))
if __name__=='__main__':main()
