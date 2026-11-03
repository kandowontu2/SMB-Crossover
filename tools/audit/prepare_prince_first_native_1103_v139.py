"""Bind read-only native menu/controls/death packets to the sole approved ROM."""
from pathlib import Path
import argparse,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_bub_menu_qualification_1102_v2 import lua
O=C.O;ROM=O/'prince-private-v140.nes'


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['controls','contact-death'],default='controls');a=ap.parse_args()
 frontend=json.loads((O/'frontend-proposal-v137.json').read_text());assert sha(ROM)==frontend['expected_memory_only_SHA256']
 base,_=C.image();L={n:C.I.address(base,n)for n in ['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','NumberofLives']}
 steps=[dict(keys=[],slot=0,state=2,kind='observe',wait=40,raw=0,tag='initial-Mario')]
 for key,slot in [('down',8),('down',16),('down',24),('right',25),('right',26),('right',27),('right',28),('right',29)]:
  raw=next(r['raw']for r in frontend['rows']if r['slot']==slot and r['cycle']==0);steps.append(dict(keys=[key],slot=slot,state=2,kind='observe',wait=40,raw=raw,tag=f'initial-slot{slot}'))
 assert steps[-1]['raw']==37
 name=[36,36,25,27,18,23,12,14,36,25,14,27,28,18,10,36]
 steps.append(dict(keys=['select'],slot=29,state=2,kind='observe',wait=40,raw=38,name=name,tag='Prince-authentic-name-no-pending-marker',shot='prince-menu'))
 steps.append(dict(keys=['start'],slot=29,state=2,kind='launch',wait=40,raw=38,tag='confirm-original-Prince'))
 labels=json.loads((O/'native-labels-v122.json').read_text());services=(O/'native-services-v122.s').read_text();labels['PpHostUpdate']=int(re.search(r'PpHostUpdate=\$([0-9a-f]+)',services)[1],16)
 runtime=(O/'native-runtime-v122.bin').read_bytes();meta=(O/'native-metadata-v122.bin').read_bytes();audio=(O/'native-state-v122.bin').read_bytes()[-154:];hooks={}
 for n in ['PpHostUpdate','PpHostDraw','PpNativeTick','PpNativeContact','PpNativeInit']:
  pc=labels[n];bank=3 if pc<0xc000 else 2;start=0xa000 if bank==3 else 0xc000;blob=runtime if bank==3 else meta;offset=pc-0xa000 if bank==3 else pc-0xc800
  hooks[n]=dict(pc=pc,memory='nesWorkRam',physical=bank*8192+pc-start,bytes=list(blob[offset:offset+4]))
 for n,pc in [('KillPlayer',C.I.address(base,'KillPlayer')),('NativeDefeat',0x9af8)]:
  at=16+126*8192+pc-0x8000;hooks[n]=dict(pc=pc,memory='nesPrgRom',physical=at-16,bytes=list(base['raw'][at:at+4]))
 q=dict(mode='Prince-first-native-'+a.mode,controlMode=a.mode,steps=steps,maxFrames=9000,ROM_sha256=frontend['expected_memory_only_SHA256'],launch=dict(raw=38,groups=0,requiresRestore=False),cookie=list(bytes.fromhex(C.image()[1]['details']['Prince_cookie'])),hooks=hooks)
 source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text();extension=R/'tools/audit/prince_first_native_1103_v139.lua'
 anchor="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert body.count(anchor)==1;body=body.replace(anchor,extension.read_text()+'\n'+anchor)
 old=" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end";assert body.count(old)==1
 body=body.replace(old," elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end\n elseif phase=='controls'or phase=='contact-death'then for _,key in ipairs(control_keys())do keys[key]=true end end")
 old="  shot('active-owner');finish()\n end";assert body.count(old)==1;body=body.replace(old,"  controls_begin()\n elseif phase=='controls'or phase=='contact-death'then controls_tick(finish)\n end")
 controller='local L='+lua(L)+'\nlocal Q='+lua(q)+'\n'+body
 for bad in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
 refs={Path(__file__),source,extension,O/'candidate-v140.json',O/'frontend-proposal-v137.json',O/'strike-manifest-v130.json',O/'native-labels-v122.json',O/'native-services-v122.s',R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'}
 prepare(O/('native-first-'+a.mode+'-v139'),ROM,controller,refs,expected=q['ROM_sha256'],timeout=240,scope='Read-only original Prince selection via Ex37->Select38, authentic name/portrait route/blank marker, real fullcold/header/lives. Original source-update paced idle/right/left/unarmedA-jump/support; optional genuine contact/native death/fullcold/respawn/Right. Passive source/native ingress counts and smallCSV, maximum4PNGs. Armed sword requires naturally earned flower and remains explicitly unqualified; no source/native outcome writes or helper/full1-1/audio claim.')


if __name__=='__main__':main()
