"""Successor population-triggered expansion diagnostic; retain original GQ."""
from pathlib import Path
import hashlib,importlib.util
R=Path(__file__).resolve().parents[2]
p=R/'tools/audit/profile_roster49_water_populated_gq.py'
sp=importlib.util.spec_from_file_location('water_populated_gq_retained',p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert m.sha(p)=='a9bcb2d32bfb4ef4fd26e5a15768f421132189cab6998fcc9f4462f9b12bad94'
m.J=m.V/'root49-water-populated-profile-gt'
old="""local dma=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end"""
new="""local dma,expandStart=0,nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end"""
assert m.FIXTURE.count(old)==1;m.FIXTURE=m.FIXTURE.replace(old,new)
old=""" emu.setInput({right=choose or frame>=730,down=char==9 and frame==80,start=frame==200,
  b=frame>=560 and frame<565 or frame>=1030 and frame<1035,
  a=frame>=900 and frame<930 or frame>=1250 and frame<1280},0)"""
new=""" local enemies,visible=0,0
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)<0x15 and r('Enemy_State',i)&32==0 then enemies=enemies+1 end end
 for i=0,9 do if r('RgShotType',i)==17 and r('SsHidden',i)==0 then visible=visible+1 end end
 if frame>=730 and enemies>0 and visible==8 and not expandStart then expandStart=frame end
 emu.setInput({right=choose or frame>=730 and not expandStart,down=char==9 and frame==80,start=frame==200,
  b=frame>=560 and frame<565 or expandStart and frame>=expandStart+8 and frame<expandStart+13},0)"""
assert m.FIXTURE.count(old)==1;m.FIXTURE=m.FIXTURE.replace(old,new)
# Keep the full predecessor window and its exact pending-return closure check.
original=m.main
def main():
 original()
 receipt=m.J/'successor-binding.json'
 receipt.write_text(__import__('json').dumps(dict(successor_script_sha256=m.sha(__file__),predecessor_script_sha256=m.sha(p),predecessor_review_sha256=m.sha(m.V/'root49-water-populated-profile-gq/review.json'),scope='Actual live enemy population and full8 shield trigger stop then B expansion eight display frames later. Player/enemy/terrain stay natural; equipment/Hard setup remain fully journaled. Original GQ zero full8-populated-expansion coverage is retained. This is diagnostic, not acquisition/route/source/finalmedia proof.'),indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
