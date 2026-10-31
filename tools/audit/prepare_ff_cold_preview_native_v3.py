"""Bind corrected physical-sprite/pixel observer to a specific private cart."""
from pathlib import Path
import argparse,difflib,json,os,shutil,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
import arthur_body_fair_budget_v7 as Q
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
OLD=R/'tools/reference/ff_cold_preview_native_v2.lua';T=R/'tools/reference/ff_cold_preview_native_v3.lua'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
def template():
 s=OLD.read_text();s=s.replace("local originalROM=readfile('candidate.nes')", "local romFile=assert(io.open(FF_ROM,'rb'));local originalROM=romFile:read('*a');romFile:close()")
 s=s.replace("local chrUpper,bodyPhysicalPage=0,-1", "local chrUpper,bodyPhysicalPage=0,-1\nlocal uiPixels,renderedUI={},{}")
 old="assert(pr(pattern)==lo and pr(pattern+8)==hi,'Actual hardware UI patterns match original CHR')"
 new="assert(emu.read(bodyPhysicalPage*1024+pattern,emu.memType.nesChrRom)==lo and emu.read(bodyPhysicalPage*1024+pattern+8,emu.memType.nesChrRom)==hi,'Actual physical sprite CHR bytes match bound original ROM')"
 assert s.count(old)==1;s=s.replace(old,new)
 s=s.replace("local py=r('Player_Y_Position');local matched,pixels,visible=0,0,0", "local py=r('Player_Y_Position');local matched,pixels,visible=0,0,0\n local expected={}")
 old="for bit=0,7 do if ((lo>>bit)&1)|(((hi>>bit)&1)<<1)~=0 then pixels=pixels+1 end end"
 new='''for bit=0,7 do
    local value=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
    if value~=0 then
     pixels=pixels+1
     local dx=attr&64~=0 and bit or 7-bit
     local dy=attr&128~=0 and 15-row or row
     expected[(y+1+dy)*256+x+dx]=color[value]
    end
   end'''
 assert s.count(old)==1;s=s.replace(old,new)
 s=s.replace("ui:write(table.concat({wall,stage", "uiPixels[stage]={frame=wall,pixels=expected,count=pixels}\n ui:write(table.concat({wall,stage")
 marker="emu.addMemoryCallback(function()\n if r('CurrentBank')~=(B.FwLoad|0x80)"
 code='''local function renderedBody(stage)
 local q=assert(uiPixels[stage],'Actual completed UI DMA before rendered pixels')
 assert(wall-q.frame>=2 and wall-q.frame<=7,'Stable UI DMA precedes actual rendered PPU frame')
 local screen=emu.getScreenBuffer();assert(#screen==61440,'Actual256x240 PPU pixel buffer')
 local colors,count={},0
 for at,nes in pairs(q.pixels)do
  assert(at>=0 and at<61440,'Source body within visible screen')
  local rgb=screen[at+1]&0xffffff
  if colors[nes]then assert(colors[nes]==rgb,'Every actual opaque UI pixel has exact consistent original palette role '..stage)
  else colors[nes]=rgb end
  count=count+1
 end
 local unique,n={},0
 for _,rgb in pairs(colors)do assert(not unique[rgb],'Original distinct UI colors must remain visibly distinct');unique[rgb]=true;n=n+1 end
 assert(n==3 and count>0,'Original visible body preserves all three source shades, not a blank panel')
 renderedUI[stage]=count
 ui:write(table.concat({wall,'rendered-'..stage,FF_CLASS,bodyPhysicalPage,0,0,0,count,n,0},',')..'\\n');ui:flush()
end
'''
 assert s.count(marker)==1;s=s.replace(marker,code+'\n'+marker)
 s=s.replace("assert(selectDmas>0 and livesDmas>0,'Actual select AND lives nonempty physical OAM/original hardware CHR/PPU verified')", "assert(selectDmas>0 and livesDmas>0 and renderedUI.select and renderedUI.lives,'Actual select AND lives nonempty physical OAM/original hardware CHR/PPU AND rendered source pixels verified')")
 s=s.replace("selectDmas>0 and wall-lastSelectDma<=8 then", "selectDmas>0 and wall-lastSelectDma>=2 and wall-lastSelectDma<=7 then")
 s=s.replace("menuNameChecked=true; snapshot('class-cold-menu')", "menuNameChecked=true; renderedBody('select');snapshot('class-cold-menu')")
 s=s.replace("livesDmas>0 and wall-lastLivesDma<=8 then snapshot('lives')end", "livesDmas>0 and wall-lastLivesDma>=2 and wall-lastLivesDma<=7 and not captured.lives then renderedBody('lives');snapshot('lives')end")
 assert 'pr(pattern)'not in s and 'FF_CLASS>=2' in s
 assert 'emu.write'not in s and 'setState'not in s and 'loadSavestate'not in s
 assert s.count('wall>=1200')==1 and s.count('shots<=6')==1
 if T.exists():assert T.read_text()==s
 else:T.write_text(s,encoding='utf-8',newline='\n')
 return s
def main():
 a=argparse.ArgumentParser();a.add_argument('--joint',type=Path,default=R/'build/ff-cold-preview-v5/joint');a.add_argument('--source-handoff',type=Path,default=R/'build/ff-cold-preview-v5/handoff-source-v1.json');a.add_argument('--expect-source',default='377536313b5971be65ff89709785f048dfcfb66d70fc94f0beed688e4173936c');a.add_argument('--expect-rom',default='334b291a929e81d12e25e2f067fe047fdd48f0cba9e58cdab2f0156f9ebd946d');a.add_argument('--data-dir',type=Path,default=R/'build/ff-cold-preview-v5/joint');a.add_argument('--output',type=Path,default=R/'build/ff-cold-preview-v5/native-prepared-v3');v=a.parse_args()
 J=v.joint.resolve();F=v.output.resolve();assert not F.exists();assert B.sha(J/'candidate.nes')==v.expect_rom
 B.validate(v.source_handoff,v.expect_source);b=qualified(J/'candidate.nes');data=v.data_dir.resolve()
 s=template();F.mkdir(parents=True)
 end=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1;assert b['raw'][location(b,'GameLoop')+int(b['syms']['GameLoop']['size'])-1]==0x60
 p=json.loads((R/'build/ff-cold-preview-v5/native-prepared-v2/prepared.json').read_text())
 actual=R/'tools/audit/capture_budget.py';budget=F/'capture-budget.py';budget.write_text(actual.read_text().replace('RUN_BYTES = 2_000_000_000','RUN_BYTES = 536_870_912').replace('receipt = preflight(output)','receipt = preflight(output, reserved_bytes=RUN_BYTES, reserved_files=RUN_FILES)'),encoding='utf-8',newline='\n')
 proof=Q.load(budget);storage=[]
 for i,name in enumerate(p['classes']):
  (F/(name+'.lua')).write_text(f'FF_CLASS={i}\nFF_MAIN_RETURN={end}\nFF_DIR=[=[{data.as_posix()}/]=]\nFF_ROM=[=[{(J/"candidate.nes").as_posix()}]=]\n'+s,encoding='utf-8',newline='\n')
  storage.append(dict(name=name,**proof.preflight(F/'native'/(name+'-cold-v3'),reserved_bytes=536870912,reserved_files=64)))
 save(F/'storage-preflight.json',dict(passed=True,launch_performed=False,classes=storage))
 correction=dict(native=False,source_cart_changed=False,first_failure='Settled Thief class3 DMA after wall138; complete source OAM/page785/Blue P0 passed; debug pattern byte comparison failed. V2 did not log exact byte tuple, so none reconstructed as native evidence.',
  source_commit='b9fa69ddc6d0a331fb103fdb5eef6904305703c2',binary_commit_equivalence_not_claimed=True,
  actual_reference='MMC5 UpdateChrBanks183..217 selects spriteA only at sprite fetch/lastsprite register outside rendering; vblank after lastBG512B selectsB. BaseMapper DebugReadVram944..950 returns InternalReadVram, not forced spriteA. MemoryDumper NesChrRom returns raw registered original CHR.',
  correction='Read physical tracked5120/5130 through nesChrRom, exact bound-ROM bytes; retain OAM/PPU/page checks and add all-source-opaque rendered color-role checks on stable2..7frame image. No pattern or visibility assertion removed without replacement.',
  old_packet=str(R/'build/ff-cold-preview-v5/native-prepared-v2/prepared.json'),old_failure=str(R/'build/ff-cold-preview-v5/native/thief-cold-v2'))
 save(F/'observer-correction.json',correction)
 (F/'observer.diff').write_text(''.join(difflib.unified_diff(OLD.read_text().splitlines(True),s.splitlines(True),fromfile='v2',tofile='v3')),encoding='utf-8',newline='\n')
 files={Path(__file__),T,OLD,R/'tools/audit/run_ff_cold_preview_native_v3.py',v.source_handoff.resolve(),J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',data/'ram3.bin',data/'ff-cookie.bin',R/'tools/run_mesen.py',Path(Q.__file__),actual,Path(p['emulator'])}|set(F.iterdir())|set((R/'build/ff-cold-preview-observer-v3').iterdir())
 p.update(status='PREPARED_ONLY_REQUIRES_ROOT_GRANT',candidate=v.expect_rom,source_handoff=v.expect_source,source_handoff_path=str(v.source_handoff.resolve()),joint=str(J),output=str(F/'native'),command=f'python tools/audit/run_ff_cold_preview_native_v3.py --packet "{F}" --launch CLASS',bindings={str(f.resolve()):B.sha(f)for f in sorted(files)if f.is_file()})
 save(F/'prepared.json',p);print(json.dumps(dict(path=str(F/'prepared.json'),sha256=B.sha(F/'prepared.json'),candidate=p['candidate'])),flush=True)
if __name__=='__main__':main()
