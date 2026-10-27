"""Finite seven-common-special MegaHard source/module preparation; no emulator."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,re,sys
from final_item_abilities_run import lua
from final_samus_hard_gallery_source_v1 import TraceArena,OWNER_NAMES
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'mm-proto-construction-pivot-candidate-v9'
OLD=D/'current3b112-bass-semantic-cleanup-ready-v1'
SHA='0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def source_cpu(b):
 rows=[]
 for n in ['SpecialWeapons','SpecialWeapons::MegaAttack','SpecialWeapons::Spawn','SpecialWeapons::ReleaseBalloon','MegaManSuperArmThrow','MegaManMovement','PlayerMovementSubs','InventoryUiTick','InventoryIndex']:
  if n not in OWNER_NAMES:OWNER_NAMES.append(n)
 for variant in[0,1]:
  for face in[1,2]:
   for item,cost,typ in[(1,8,9),(2,4,10),(3,8,11),(4,4,12),(5,4,19),(6,4,15),(7,16,17)]:
    for kind in['funded','underfunded','fullpool']:
     q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=variant,CrossoverBehaviorVersion=1,PlayerStatus=1,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,PlayerFacingDir=face,TimerControl=0)
     q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);q.set('InvSelected',item,1);stock=12 if item==4 and kind=='funded'else cost if kind=='funded'else cost-1 if kind=='underfunded'else 112;q.set('InvAmmo',stock,16+item)
     col=(112+8+(10 if face==1 else-10))//16
     if item==1:q.set('Block_Buffer_1',0x51,160+col)
     if kind=='fullpool':
      for i in range(10):
       for name,v in [('RgShotType',10),('RgShotX',70+i*5),('RgShotPage',0),('RgShotY',72),('RgShotYHigh',1),('RgShotDir',face)]:q.set(name,v,i)
     def actual_input(bits,slide=False):
      q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits,A_B_Buttons=bits&192,PreviousA_B_Buttons=0,InvPrevious=0)
      q.invoke('RlUiDispatch')
      if slide:q.invoke('PlayerMovementSubs')
      q.invoke('ProcFireball_Bubble')
     actual_input(132 if item==5 else 64,item==5)
     first=q.get('InvAmmo',16+item);held=q.get('SsHeld');slide=q.get('MmSliding');kick=q.get('SsKick');types=[q.get('RgShotType',i)for i in range(10)]
     if item==1 and kind=='funded':
      assert first==stock and held>0 and q.get('Block_Buffer_1',160+col)==0;actual_input(0);actual_input(64);assert q.get('SsHeld')==0
     expected=stock-(cost if kind=='funded'else cost if kind=='fullpool'and item in[5,7]else 0)
     assert q.get('InvAmmo',16+item)==expected,(variant,face,item,kind,stock,q.get('InvAmmo',16+item),types)
     if kind=='funded':assert typ in types and all(q.get('RgShotDir',i)==face for i,t in enumerate(types)if t)
     if kind=='underfunded':assert not any(types)and q.get('SsHeld')==0
     if kind=='fullpool':assert types==[10]*10
     if item==5:assert slide==1 and kick==(1 if kind!='underfunded'else 2)
     names={z['owner']for c in q.calls for z in c['entries']};assert {'ProcFireball_Bubble','SpecialWeapons','InventoryUiTick'}<=names
     if item==5:assert 'MegaManMovement'in names and 'PlayerMovementSubs'in names
     rows.append(dict(variant=variant,face=face,item=item,index=16+item,kind=kind,before=stock,after=q.get('InvAmmo',16+item),free_lift_stock=first if item==1 else None,held_initial=held,slide=slide,kick=kick,initial_types=types,calls=q.calls))
   # Full real selection owner excludes absent Rush and unselectable passives.
   q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=variant,CrossoverBehaviorVersion=1);q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);choices=[]
   for wanted in[1,2,3,4,5,6,7,0]:q.invoke('InventoryCycle');choices.append(q.get('InvSelected',1));assert choices[-1]==wanted
   rows.append(dict(kind='complete-InventoryCycle-common-only',variant=variant,face=face,choices=choices,calls=q.calls))
 return dict(passed=True,source_only=True,ROM_sha256=SHA,complete_UI_primary_Special_cells=84,selection_sequences=4,rows=rows,scope='Both presentation variants/source owners are CPU evidence only. Fourteen native plans target MegaHard/variant0 first; no Proto/native/acquisition/timing proof. ARM free real block lift then paid real throw and KICK actual PlayerMovementSubs/MegaManMovement activation are observed, not directly seeded effect outcomes.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(B/'candidate.nes')==SHA
 manifest=json.loads((B/'source-manifest.json').read_text())
 for name,h in manifest.items():assert sha(B/'source'/name)==h
 assert len(manifest)==869;b=scoped_load(B/'candidate.nes');old=OLD/'profiles/bass-hard/native';cfg=json.loads((old/'config.json').read_text());original=(old/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert original.startswith(prefix);body=original[len(prefix):];first=body.index('-- Controlled B-only gallery.');last=body.index('\nlocal saved=nil',first);before=body[first:last];after=before;substitutions=[]
 def replace(u,v,count):
  nonlocal after
  assert after.count(u)==count,(u,after.count(u),count);after=after.replace(u,v);substitutions.append(dict(before=u,after=v,occurrences=count))
 replace('local current=nil','local current=nil\nlocal function owner()return C.identity.owner end\nlocal function ammoIndex(item)return C.identity.ammo_indices[item+1]end',1)
 replace('144+current.q.item','ammoIndex(current.q.item)',5);replace('144+item','ammoIndex(item)',2);replace("r('InvSelected',9)","r('InvSelected',owner())",6)
 replace("w('InvOwnedLo',255,9)","w('InvOwnedLo',255,owner())",1);replace("w('InvOwnedHi',0,9)","w('InvOwnedHi',0,owner())",1);replace("['cpu.x']==9","['cpu.x']==owner()",1)
 replace("r('SelectedCharacter')==9 and r('RlVariant')==0","r('SelectedCharacter')==owner() and r(C.identity.variant_ram)==C.identity.variant",2)
 replace("if r('SsKick')~=1 or r('XgDash')==0 then return end","if r('SsKick')~=1 or r('MmSliding')==0 then return end",1)
 replace("current.q.item==5 and(r('XgDash')==0 or r('SsKick')~=0)","current.q.item==5 and(r('MmSliding')==0 or r('SsKick')~=0)",1)
 replace("r('SsHeld')==0 and r('XgDash')==0 then","r('SsHeld')==0 and r('MmSliding')==0 then",1)
 replace("q.item==5 and r('SsKick')==1 and r('XgDash')~=0","q.item==5 and r('SsKick')==1 and r('MmSliding')~=0",1)
 replace("dash=r('XgDash')","slide=r('MmSliding')",1)
 reverse=after
 for z in reversed(substitutions):reverse=reverse.replace(z['after'],z['before'])
 assert reverse==before
 (a.output/'mechanics.lua').write_text(after,encoding='utf-8');(a.output/'mechanics.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='qualified-Bass-semantic-mechanics.lua',tofile='Mega-common-owner-mechanics.lua')),encoding='utf-8')
 cfg.update(family='megaman',character=1,slot=1,hard=True,mode_value=1,ROM_sha256=SHA);indices=list(b['raw'][location(b,'InvAmmoIndex')+16:location(b,'InvAmmoIndex')+25]);assert indices==[255,17,18,19,20,21,22,23,24];cfg['identity']=dict(owner=1,variant_ram='ProtoVariant',variant=0,ammo_indices=indices,inventory_base=16,unowned_Rush=8,passive_balance=9,passive_charge=10)
 slots=list(b['raw'][location(b,'X5MenuCharacters'):location(b,'X5MenuCharacters')+19]);assert slots[cfg['slot']]==1
 plans=[]
 for q in cfg['cases']:
  if q['item']==0:continue
  z=copy.deepcopy(q);index=16+q['item'];ptr=b['raw'][location(b,'InvNameLo')+index]+256*b['raw'][location(b,'InvNameHi')+index];bank=(location(b,'InvNameLo')-16)//8192;off=16+bank*8192+ptr%8192;z.update(hud_name=list(b['raw'][off:off+7]),source_cost=b['raw'][location(b,'InvCosts')+index],icon_bank=b['raw'][location(b,'InvHudPhysicalBanks')+q['item']-1]);plans.append(z)
 assert len(plans)==14;cfg['cases']=plans
 for name,h in list(cfg['hooks'].items()):
  target='GameLoop'if name=='finish'else'NonMaskableInterrupt'if name=='NmiReturn'else name;delta=int(b['syms'][target]['size'],0)-1 if name in['finish','NmiReturn']else 0;pos=location(b,target)+delta;cfg['hooks'][name]=dict(address=address(b,target)+delta,physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+len(h['bytes'])]))
 for name in cfg['ram']:cfg['ram'][name]=address(b,name)
 cfg['ram']['ProtoVariant']=address(b,'ProtoVariant')
 head=body[:first];tail=body[last:];assert head.count("if r('RlVariant')~=0 then return{select=true}end")==1;head=head.replace("if r('RlVariant')~=0 then return{select=true}end","if r(C.identity.variant_ram)~=C.identity.variant then return{select=true}end");assert head.count("string.format('%q',k)")==1;head=head.replace("string.format('%q',k)","string.format('%q',tostring(k))");tail=tail.replace('native-bass-gallery.json','native-megaproto-common.json')
 script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+head+after+tail;assert "w('InvSelected'"not in script and "w('CrossoverBehaviorVersion'"not in script and "w('ProtoVariant'"not in script
 put(a.output/'config.json',cfg);(a.output/'run.lua').write_text(script,encoding='utf-8');put(a.output/'plans.json',plans);put(a.output/'mechanics-delta.json',dict(passed=True,exact_reverse_to_qualified_Bass_mechanics=True,substitutions=substitutions,unchanged=['Direct fullReleaseBalloon8/clamp observer','Funded0witness/exactnativecredits','Complete4drop/refill isolation eachdeclaredcomponent','Semantic cancelledSsKick2 predicate','WATERfreshBage125','Allfunded420/empty25/pool15/selection/cleanupcaps and strictguards'],changed='Owner1/ammo17..23/ProtoVariant0 and sourceMmSliding KICK; no defaultbusterplans; actual linked hook/address/name/icon metadata refreshed.'))
 cpu=source_cpu(b);put(a.output/'assembled-owner-controls.json',cpu)
 from final_item_abilities_current731_prepare_v1 import protocol
 assert cfg['dma_protocol']==protocol(b)
 oldsource=D/'root-current-roster-composition-v1/source';shared=[]
 for name in ['special_weapons.s','inventory_drops.s','megaman_super_arm.s','guest_body_contact.s']:
  x=B/'source/src'/name;y=oldsource/'src'/name;assert x.read_bytes()==y.read_bytes();shared.append(dict(path=name,sha256=sha(x),source_equivalent_only=True))
 put(a.output/'source-sharing.json',dict(passed=True,files=shared,warning='Identical shared source reduces duplicate CPU study, never grants native coverage to anotheridentity/ROM/physical renderer.0a changed renderer data/hooks are freshlybound; Proto0ba startup/deadline and ROOT9c composition remainseparate.'))
 report=R/'docs/qa/final-megaproto-common-source-2026-10-26.txt';report.write_text('Mega/Proto common-special first source unit\n26 October2026. Private0a '+SHA+'. Installed3b unchanged.\n\nFirstproposednativeprofile is MegaMan/owner1/ProtoVariant0/numericHard1,14cases:ARM/METAL/KNUCKLE/PHARAOH/KICK/FLAME/WATERbothfacings. No defaultbuster/Rush/Balancer/charge duplication ofA sixcaseprimary. SourceCPUcoversbothvariantvaluesonly; Proto native remainsheldfor0ba deadline378, not inferredfromMega. No nativegrant/run here.\n\nReuse exactcorrectedBasssemanticmachinery: complete nativeboundary setup/dropisolation, actual Select selection, fundedsource0witness/exactcredits, separateempty/fullpool, directfullPharaohReleaseBalloon8/clamp observer, semantic cancelledkick2, WATERsecondBage125, actualeffectcontact/art/HUD/cleanup andstrictE008/IRQ/stack/banks/5SMC/fullPPU/caps. Explicit typedadaptation maps owner9→genuine1, stock144+item→actualtable17..23 andvariant0readback. KICK sourceaccepts XgDash|MmSliding; thisprofile requiresactualMmSliding producedbyPlayerMovementSubs→MegaManMovement underDown+freshA, notrawdashseed. No gamecodechange.\n\n84completeUI→Proc/Specialsource cells (2variants×2facings×7specials×funded/underfunded/fullpool) plus4completecommon-onlyselectioncycles qualifyactualdispatch/index/cost. ARMrealmap51liftfree thenfreshBthrow8, KICKactualmovementactivation and4paymentevenfullpool, WATER16paymentevenfullpool, otherfunded/refusalpolicies exact. Sourceequivalence ofspecial/drops/ARM/bodyownersisexplicit,butno nativeidentity/graphics/timingcoverage inferred. Actual0a hooks refreshedincludingmovedrenderer/Rosterready; no fakealiases.\n\nSeeds: tier1/ownedlow255,hi0; declaredammo8/4/8/12/4/4/16, cleanempty0/fullpool112, complete10METALrecords, actualfront51brick andonelegalfallingGoombaalignedtoliveeffect/body afteractivation. No InvSelected/mode/variant/outcome writes; selectionnative. These areBuse,notacquisition. ARMquestionblock regressionalreadyseparate; allotheritem/acquisition/Easy/Proto/campaign/audio/FPS/flickerclosure remainsopen.\n\nThispacket freezes source/config/module/ownerCPUpreparation only. FurtheractualLua phase/startup/seed/decoder/physicalartmetadata controls and freshone-shotruntime readiness are required before a grant. No emulator/default/settings/Git writes.\n',encoding='utf-8')
 refs=[Path(__file__),B/'candidate.nes',B/'candidate.dbg',B/'proof.json',B/'source-manifest.json',OLD/'proof.json',OLD/'manifest.json',old/'config.json',old/'run.lua',report];refs+=[B/'source'/name for name in manifest];refs+=list(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(set(refs),key=str)]));put(a.output/'proof.json',dict(passed=True,source_only=True,native_ready=False,native_run=False,native_grant=False,ROM_sha256=SHA,profile='mega-hard-common',mode=1,variant=0,cases=14,CPU_cells=84,selection_sequences=4,manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),report_sha256=sha(report),next_required='ActualLua mechanics/seed/phase/startup mocks and fresh runtime/command readiness; do not launch this source-only packet.'));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),report_sha256=sha(report)),indent=2))
if __name__=='__main__':main()
