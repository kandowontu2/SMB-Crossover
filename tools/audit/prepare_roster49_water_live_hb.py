"""Create a pinned successor profiler with actual native-eligible enemies."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=R/'tools/audit/profile_roster49_water_populated_gq.py'
assert sha(p)=='a9bcb2d32bfb4ef4fd26e5a15768f421132189cab6998fcc9f4462f9b12bad94'
code=p.read_text(encoding='utf-8')
def replace(old,new,count=1):
 global code
 assert code.count(old)==count,(old[:100],code.count(old),count)
 code=code.replace(old,new)
replace("root49-water-populated-profile-gq","root49-water-live-profile-hb")
replace('local dma=0','local dma,expandStart=0,nil')
old="for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)<0x15 and r('Enemy_State',i)&32==0 then enemies=enemies+1 end end"
eligible="""for i=0,5 do
 local flag,kind,state=r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i)
 if flag>0 and flag<128 and state&32==0 and(kind<0x15 or kind==0x2d or kind==0x33)and(kind~=6 or state<2)and r('EnemyOffscrBitsMasked',i)==0 then enemies=enemies+1 end
end"""
replace(old,eligible,2)
old=""" emu.setInput({right=choose or frame>=730,down=char==9 and frame==80,start=frame==200,
  b=frame>=560 and frame<565 or frame>=1030 and frame<1035,
  a=frame>=900 and frame<930 or frame>=1250 and frame<1280},0)"""
new=""" local enemies,visible=0,0
 __ELIGIBLE__
 for i=0,9 do if r('RgShotType',i)==17 and r('SsHidden',i)==0 then visible=visible+1 end end
 if frame>=730 and enemies>0 and visible==8 and not expandStart then expandStart=frame end
 emu.setInput({right=choose or frame>=730 and not expandStart,down=char==9 and frame==80,start=frame==200,
  b=frame>=560 and frame<565 or expandStart and frame>=expandStart+8 and frame<expandStart+13},0)""".replace('__ELIGIBLE__',eligible)
replace(old,new)
replace("used+100000000<80000000000","used+250000000<100000000000")
replace('phase_cap=100000000,reserve=50000000,global_cap=80000000000','phase_cap=250000000,reserve=50000000,global_cap=100000000000')
replace("for revision in ['H','I']:","for revision in ['H','I','J']:")
replace("rom=(cp.parent if revision=='H'else private/'source/build')/f'smb-crossover-{mapper}.nes'","rom=(cp.parent if revision=='H'else private/'source/build'if revision=='I'else V/'root49-water-enemy-filter-gy/source/build')/f'smb-crossover-{mapper}.nes'")
replace("groups=[]\n", "assert sha(V/'root49-water-enemy-filter-gy/build-review-ha.json')=='6eedbf9da2b36e9c77fae68200d63b4308c611af1511becb0bf6a197900144d6'\n groups=[]\n")
replace("stem=f'{revision}-{mapper}-{char}';folder=J/stem;folder.mkdir();fixture=folder/'component.lua'", "assert workspace_bytes(J)+18000000+50000000<250000000\n    assert workspace_bytes(R)+18000000<100000000000\n    stem=f'{revision}-{mapper}-{char}';folder=J/stem;folder.mkdir();fixture=folder/'component.lua'")
replace('First pipe jumps and real expansion press','Real eligible-enemy expansion press')if 'First pipe jumps and real expansion press'in code else None
replace('first pipe jumps and real expansion press','halt at first real native-eligible enemy then actualB expansion; strict enemy admission includes offscreen/goomba/bowser/bullet kinds')
replace("scope='Authored equipment only at550", "predecessor_GQ_sha256='a9bcb2d32bfb4ef4fd26e5a15768f421132189cab6998fcc9f4462f9b12bad94',preparer_sha256=sha(R/'tools/audit/prepare_roster49_water_live_hb.py'),scope='Authored equipment only at550")
out=R/'tools/audit/profile_roster49_water_live_hb.py';assert not out.exists();out.write_text(code,encoding='utf-8')
print(json.dumps(dict(output=str(out.relative_to(R)),sha256=sha(out),scope='Actual native eligibility replaces active-slot population; H/I/J. GQ/GT keep their original active-enemy scopes and zero/missing actual visible-contact coverage.')))
