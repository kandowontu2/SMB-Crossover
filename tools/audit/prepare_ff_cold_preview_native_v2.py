"""Prepare corrected four-class native observers, without launching Mesen."""
from pathlib import Path
import json,os,shutil,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
import arthur_body_fair_budget_v7 as Q
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=R/'build/ff-cold-preview-v5';J=O/'joint';F=O/'native-prepared-v2'
T=R/'tools/reference/ff_cold_preview_native_v2.lua'
CLASSES=['fighter','white-mage','black-mage','thief']
OPTIONS=['--doNotSaveSettings','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
 '--nes.randomizeMapperPowerOnState=false','--nes.removeSpriteLimit=false','--nes.adaptiveSpriteLimit=false']
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 assert not F.exists() and not T.exists()
 B.validate(O/'handoff-source-v1.json','377536313b5971be65ff89709785f048dfcfb66d70fc94f0beed688e4173936c')
 b=qualified(J/'candidate.nes');assert B.sha(J/'candidate.nes')=='334b291a929e81d12e25e2f067fe047fdd48f0cba9e58cdab2f0156f9ebd946d'
 old=R/'tools/reference/ff_current_names_native_v1.lua';s=old.read_text()
 assert s.count('FF_CLASS==2 and{0x28,0x18,0x21}')==1
 s=s.replace('FF_CLASS==2 and{0x28,0x18,0x21}','FF_CLASS>=2 and{0x28,0x18,0x21}')
 s=s.replace("local normalDmas,paletteChecks,shots=0,0,0", "local normalDmas,paletteChecks,shots=0,0,0\nlocal selectDmas,livesDmas,lastSelectDma,lastLivesDma=0,0,-99,-99\nlocal chrUpper,bodyPhysicalPage=0,-1")
 s=s.replace("local image,cookie=readfile('ram3.bin'),readfile('ff-cookie.bin')", "local image,cookie=readfile('ram3.bin'),readfile('ff-cookie.bin')\nlocal originalROM=readfile('candidate.nes')")
 marker="emu.addMemoryCallback(function(_,v)hardwareMask=v end,emu.callbackType.write,0x2001)"
 add='''
emu.addMemoryCallback(function(_,v)chrUpper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(_,v)bodyPhysicalPage=chrUpper+v end,emu.callbackType.write,0x5120)
local ui=assert(io.open(OUTPUT..'select-lives-DMA.csv','w'))
ui:write('frame,stage,class,physicalPage,header,parts,visible,opaquePixels,P0,background\\n')
local function uiBody(stage,page)
 local all={};for i=0,255 do all[i]=emu.read(page*256+i,emu.memType.nesDebug)end
 local base=L.FfRenderBuffer;local header=emu.read(base,emu.memType.nesDebug)
 assert(header>=4 and header<=32 and header%4==0,'Actual UI original body0 record')
 assert(r('FfTemp2')==0 and bodyPhysicalPage==756+r('FfRenderPage') and bodyPhysicalPage>=756 and bodyPhysicalPage<788,'Actual UI hardware window0 is original FF ART, never code carrier')
 local color=FF_CLASS>=2 and{0x28,0x18,0x21}or{0x16,0x30,0x36}
 for i=1,3 do assert(pr(0x3f10+i)==color[i],'Actual UI original class palette '..stage)end
 if stage=='lives'then assert(pr(0x3f00)==0x0f and pr(0x3f10)==0x0f,'Native lives black backdrop preserved')end
 local px=(r('Player_X_Position')-r('ScreenLeft_X_Pos'))&255
 local py=r('Player_Y_Position');local matched,pixels,visible=0,0,0
 for i=0,252,4 do if all[i]<240 then visible=visible+1 end end
 local function signed(v)return v>=128 and v-256 or v end
 for i=1,header,4 do
  local tile=emu.read(base+i,emu.memType.nesDebug)
  local attr=emu.read(base+i+1,emu.memType.nesDebug)&0xdf
  local y=(py+signed(emu.read(base+i+2,emu.memType.nesDebug)))&255
  local x=(px+signed(emu.read(base+i+3,emu.memType.nesDebug)))&255
  assert(tile<64 and attr&3==0 and attr&0x20==0,'UI source body uses original window0/P0/in-front')
  local found=false
  for at=0,252,4 do
   if all[at]==y and all[at+1]==tile and all[at+2]==attr and all[at+3]==x then found=true;break end
  end
  assert(found,'Complete original UI body part submitted to physical DMA '..stage..' part '..i)
  matched=matched+1
  for row=0,15 do
   local pattern=(tile&254)*16+math.floor(row/8)*16+row%8
   local source=1048592+bodyPhysicalPage*1024+pattern
   local lo,hi=originalROM:byte(source+1),originalROM:byte(source+9)
   assert(pr(pattern)==lo and pr(pattern+8)==hi,'Actual hardware UI patterns match original CHR')
   for bit=0,7 do if ((lo>>bit)&1)|(((hi>>bit)&1)<<1)~=0 then pixels=pixels+1 end end
  end
 end
 assert(matched==header/4 and pixels>0 and visible>=matched and visible<=8,'Nonempty complete UI body within normal sprite hardware budget')
 ui:write(table.concat({wall,stage,FF_CLASS,bodyPhysicalPage,header,matched,visible,pixels,string.format('%02x%02x%02x',color[1],color[2],color[3]),pr(0x3f00)},',')..'\\n');ui:flush()
end
'''
 assert s.count(marker)==1;s=s.replace(marker,marker+'\n'+add)
 marker=" if phase~='game'then return end"
 change=''' if r('SelectedCharacter')==22 and r('FfVariant')==FF_CLASS then
  if phase=='select' and r('OperMode')==0 and r('CrossoverMenuState')==2 and r('CrossoverMenuIndex')==21 and wall-lastAction>=8 and wall-lastSelectDma>=8 then
   uiBody('select',page);selectDmas=selectDmas+1;lastSelectDma=wall
  elseif loaded and r('OperMode')==1 and r('ScreenRoutineTask')==7 and wall-lastLivesDma>=8 then
   uiBody('lives',page);livesDmas=livesDmas+1;lastLivesDma=wall
  end
 end
 if phase~='game'then return end'''
 assert s.count(marker)==1;s=s.replace(marker,change)
 s=s.replace("assert(menuNameChecked and hudNameChecked,'Actual cold menu and gameplay hardware class names')", "assert(menuNameChecked and hudNameChecked,'Actual cold menu and gameplay hardware class names')\n assert(selectDmas>0 and livesDmas>0,'Actual select AND lives nonempty physical OAM/original hardware CHR/PPU verified')")
 s=s.replace("trace:close();palette:close();guard:close();oam:close()", "trace:close();palette:close();guard:close();oam:close();ui:close()")
 s=s.replace("local f=assert(io.open(OUTPUT..'result.json','w'))", "local u=assert(io.open(OUTPUT..'ui-result.json','w'));u:write(string.format('{\"passed\":true,\"class\":%d,\"select_DMA_checks\":%d,\"lives_DMA_checks\":%d,\"actual_original_chr_oam_ppu\":true}\\n',FF_CLASS,selectDmas,livesDmas));u:close()\n local f=assert(io.open(OUTPUT..'result.json','w'))")
 s=s.replace("elseif wall-lastAction>=16 then", "elseif wall-lastAction>=16 and selectDmas>0 and wall-lastSelectDma<=8 then")
 s=s.replace("if mode==1 and r('ScreenRoutineTask')==7 and loaded then snapshot('lives')end", "if mode==1 and r('ScreenRoutineTask')==7 and loaded and livesDmas>0 and wall-lastLivesDma<=8 then snapshot('lives')end")
 assert 'emu.write'not in s and 'setState'not in s and 'loadSavestate'not in s
 assert s.count('wall>=1200')==1 and s.count('shots<=6')==1 and s.count('emu.stop(0);return')==1
 T.write_text(s,encoding='utf-8',newline='\n');F.mkdir()
 end=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1;assert b['raw'][location(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1]==0x60
 actual=R/'tools/audit/capture_budget.py';budget=F/'capture-budget.py'
 budget.write_text(actual.read_text().replace('RUN_BYTES = 2_000_000_000','RUN_BYTES = 536_870_912').replace('receipt = preflight(output)','receipt = preflight(output, reserved_bytes=RUN_BYTES, reserved_files=RUN_FILES)'),encoding='utf-8',newline='\n')
 exe=os.environ.get('MESEN')or shutil.which('Mesen')or'C:/mesen2/Mesen.exe';assert Path(exe).is_file()
 proof=Q.load(budget);storage=[]
 for i,name in enumerate(CLASSES):
  (F/(name+'.lua')).write_text(f'FF_CLASS={i}\nFF_MAIN_RETURN={end}\nFF_DIR=[=[{J.as_posix()}/]=]\n'+s,encoding='utf-8',newline='\n')
  storage.append(dict(name=name,**proof.preflight(O/'native'/(name+'-cold-v2'),reserved_bytes=536870912,reserved_files=64)))
 save(F/'storage-preflight.json',dict(passed=True,launch_performed=False,classes=storage))
 save(F/'observer-correction.json',dict(passed=True,native=False,old_template=str(old),old_template_sha256=B.sha(old),
  old_failure=str(R/'build/ff-current-names-v3/native/thief-cold-v1'),
  actual_source_palette='FfPalettePointer and FwPreviewColors: class0/1 Red16,30,36; class2 AND3 Blue28,18,21',
  additions='Actual4014 DMA buffer submitted parts, exact original hardware window0/pattern bytes/P0, nonempty original pixel count, lives black backdrop; both contexts required before success.',
  preserved='All original bound loader/full8KB16cookie/semantic/controller/gameplay/world/palette/zeroRAMwrite/death/frame/capture assertions retained. No emulator launched.'))
 files={Path(__file__),T,old,R/'tools/audit/run_ff_cold_preview_native_v2.py',O/'handoff-source-v1.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'ram3.bin',J/'ff-cookie.bin',R/'tools/run_mesen.py',Path(Q.__file__),actual,Path(exe)}|set(F.iterdir())
 p=dict(status='PREPARED_ONLY_ROOT_SERIAL_RUNS_NOT_GRANTED',native=False,candidate=B.sha(J/'candidate.nes'),source_handoff=B.sha(O/'handoff-source-v1.json'),
  emulator=str(Path(exe).resolve()),emulator_sha256=B.sha(exe),classes=CLASSES,command='python tools/audit/run_ff_cold_preview_native_v2.py --launch CLASS',
  configuration=dict(physical_frames=1200,gameplay_physical_frames=260,screenshots_per_run=6,files_per_run=64,reserved_bytes_per_run=536870912,timeout_seconds=120,no_debug_RAM_writes=True,AllZeros=True,normal8sprite_limit=True),options=OPTIONS,
  bindings={str(f.resolve()):B.sha(f)for f in sorted(files)})
 save(F/'prepared.json',p);print(json.dumps(dict(path=str(F/'prepared.json'),sha256=B.sha(F/'prepared.json'),candidate=p['candidate'])))
if __name__=='__main__':main()
