"""Read-only current159 native packets; candidate emission remains root-owned."""
from pathlib import Path
import argparse,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as C
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_bub_menu_qualification_1102_v2 import lua
O=C.O


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['controls','contact-death'],default='controls');ap.add_argument('--rom',type=Path,default=O/'prince-private-v175.nes');a=ap.parse_args()
 proposal=json.loads((O/'live-lifetime-proposal-v172.json').read_text());expected=proposal['expected_private_native_with_unchanged_v105_frontend_SHA256'];assert sha(a.rom)==expected
 base,manifest=C.M.image();base=dict(base,raw=a.rom.read_bytes());N=C.N
 L={n:C.I.address(base,n)for n in ['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','NumberofLives']}
 frontend=json.loads((O/'frontend-proposal-v137.json').read_text());steps=[dict(keys=[],slot=0,state=2,kind='observe',wait=40,raw=0,tag='initial-Mario')]
 for key,slot in [('down',8),('down',16),('down',24),('right',25),('right',26),('right',27),('right',28),('right',29)]:
  raw=next(r['raw']for r in frontend['rows']if r['slot']==slot and r['cycle']==0);steps.append(dict(keys=[key],slot=slot,state=2,kind='observe',wait=40,raw=raw,tag=f'initial-slot{slot}'))
 assert steps[-1]['raw']==37
 steps.append(dict(keys=['select'],slot=29,state=2,kind='observe',wait=40,raw=38,name=[36,36,25,27,18,23,12,14,36,25,14,27,28,18,10,36],tag='Prince-authentic-name-no-pending-marker',shot='prince-menu'))
 steps.append(dict(keys=['start'],slot=29,state=2,kind='launch',wait=40,raw=38,tag='confirm-original-Prince'))
 screen=N.fresh(base);N.put(screen,CrossoverMenuState=1,Mirror_PPUMASK=0,DisableScreenFlag=1);N.invoke(screen,'CrossoverMenuInput');silhouette=[[(12+y)*32+25+x,screen.vram[0x2000+(12+y)*32+25+x]]for y in range(4)for x in range(3)]
 assert any(v!=36 for _,v in silhouette)
 labels=json.loads((O/'native-labels-v153.json').read_text());services=(O/'native-services-v157.s').read_text();labels['PpHostUpdate']=int(re.search(r'PpHostUpdate=\$([0-9a-f]+)',services)[1],16)
 runtime,meta,state=C.M.B.images();live=(O/'native-live-v149.bin').read_bytes();hooks={}
 for name in ['PpHostUpdate','PpHostDraw','PpNativeTick','PpNativeContact','PpNativeInit','PpNativeColors','PpLiveName']:
  pc=labels[name];bank=3 if pc<0xc000 else 2;start=0xa000 if bank==3 else 0xc000
  blob=runtime if bank==3 else meta;off=pc-(0xa000 if bank==3 else 0xc800)
  if 0xbfa3<=pc<0xbfd8:blob=live;off=pc-0xbfa3
  hooks[name]=dict(pc=pc,memory='nesWorkRam',physical=bank*8192+pc-start,bytes=list(blob[off:off+4]))
 for name in ['KillPlayer','X5QueueAreaBackdrop']:
  pc=C.I.address(base,name);at=C.I.location(base,name);hooks[name]=dict(pc=pc,memory='nesPrgRom',physical=at-16,bytes=list(base['raw'][at:at+4]))
 at=16+126*8192+0x9af8-0x8000;hooks['NativeDefeat']=dict(pc=0x9af8,memory='nesPrgRom',physical=at-16,bytes=list(base['raw'][at:at+4]))
 q=dict(mode='Prince-live174-'+a.mode,controlMode=a.mode,steps=steps,maxFrames=12000,ROM_sha256=expected,launch=dict(raw=38,groups=0,requiresRestore=False),cookie=list(bytes.fromhex(manifest['Prince_cookie'])),hooks=hooks,silhouette=silhouette)
 source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text();extension=R/'tools/audit/prince_first_native_1103_v139.lua';ext=extension.read_text()
 ext=ext.replace("{name='right',updates=16,keys={'right'}}","{name='right',updates=48,keys={'right'}}").replace("{name='left',updates=16,keys={'left'}}","{name='left',updates=48,keys={'left'}}")
 assert "{name='right',updates=48"in ext and "{name='left',updates=48"in ext
 ext=ext.replace('local profileMinSP=255','local profileMinSP=255\nlocal backdropCalls,statusCalls=0,0')
 needle="elseif name=='PpNativeInit'then initCalls=initCalls+1 end";assert needle in ext
 ext=ext.replace(needle,"elseif name=='PpNativeInit'then initCalls=initCalls+1\n  elseif name=='X5QueueAreaBackdrop'then backdropCalls=backdropCalls+1\n  elseif name=='PpLiveName'then statusCalls=statusCalls+1 end")
 ext=ext.replace("assert(initialLives==2,'Native initial lives2')","assert(initialLives==2,'Native initial lives2');assert(initialY==176 and ram(0xa4)==1,'Native entrance Y176 survives source epoch')")
 ext=ext.replace("assert(sourceDraws>0 and sourceUpdates>0,'Real original source update/render')","assert(sourceDraws>0 and sourceUpdates>0,'Real original source update/render');assert(backdropCalls>0 and statusCalls>0,'Actual native backdrop/status ingresses')")
 ext=ext.replace('"native_init_calls":%d,','"native_init_calls":%d,"native_backdrop_calls":%d,"native_status_calls":%d,').replace('killCalls,initCalls,profileMinSP,','killCalls,initCalls,backdropCalls,statusCalls,profileMinSP,')
 anchor="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert body.count(anchor)==1;body=body.replace(anchor,ext+'\n'+anchor)
 old="  for _,cell in ipairs({{676,245},{677,246},{708,247},{709,248}})do assert(ppu(0x2000+cell[1])==cell[2],'Actual same-span NT copy/icon survives rebuild')end";assert old in body
 body=body.replace(old,"  for _,cell in ipairs(Q.silhouette)do assert(ppu(0x2000+cell[1])==cell[2],'Actual current Battletoads silhouette survives selection')end")
 start=body.index('  if s.slot==32 then');end=body.index("  if s.family=='BT'",start);body=body[:start]+body[end:]
 body=body.replace("assert(n==33,'All33 positions actually visited')","assert(n==32,'All32 positions actually visited')")
 old=" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end";assert old in body
 body=body.replace(old," elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end\n elseif phase=='controls'or phase=='contact-death'then for _,key in ipairs(control_keys())do keys[key]=true end end")
 old="  shot('active-owner');finish()\n end";assert old in body;body=body.replace(old,"  controls_begin()\n elseif phase=='controls'or phase=='contact-death'then controls_tick(finish)\n end")
 # Event-based longcold handoff, with the original strict active-state check.
 old=" elseif phase=='game'and age>=360 then\n";assert old in body
 body=body.replace(old," elseif phase=='game'then\n  assert(age<1200,'Bounded actual Prince cold/native stage handoff')\n  if r('OperMode')==1 and r('OperMode_Task')==3 and r('CrossoverMenuState')==0 and r('SelectedCharacter')==38 and r('GameEngineSubroutine')==8 and ps(0xab)==0xa7 then\n")
 old="  controls_begin()\n elseif phase=='controls'";assert old in body;body=body.replace(old,"  controls_begin()\n  end\n elseif phase=='controls'")
 controller='local L='+lua(L)+'\nlocal Q='+lua(q)+'\n'+body
 for bad in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
 refs={Path(__file__),source,extension,O/'live-lifetime-proposal-v172.json',O/'backdrop-manifest-v159.json',O/'native-labels-v153.json',O/'native-services-v157.s',O/'live-policy-ISR-v170.json',O/'post-return-nested-IRQ-CPU-v171.json',O/'post-return-respawn-CPU-v173.json',R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'}
 prepare(O/f'native-live-{a.mode}-v174',a.rom,controller,refs,expected=expected,timeout=300,scope='Read-only current159 +exact9frontend candidate. Actual initialEx37/SelectPrince38 name/portrait/blankmarker/current32slot silhouette, bounded1200cold handoff, exactnativeentranceY176/high1, sourceidle/right48/left48/originalA-jump and supportedrest; optional earnedcontact/death/fullcold/respawn/right. Actual backdrop/status/draw ingresses required. Maximum3PNGcontrols/4PNGcontact, smallCSV/noactiveRAMwrites. NativecollisionY176/177 andoriginalpose differences retained, no groundedYstability/fullstage/helpers/armedstrike/audio claim.')


if __name__=='__main__':main()
