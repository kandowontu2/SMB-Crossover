"""Prepare two bounded native checks, retaining the shared33-SMC vector guard."""
from pathlib import Path
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/benj-native-1030-v1'
J=R/'build/benj-menu-unlocked-1030-v3/joint'
H=J.parent/'handoff.json'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert not O.exists()
 assert sha(H)=='4c3ae5f151776f374494fb9f553bc0a2d3b7491e66ff0c1ef65d8926cf3741ed'
 h=json.loads(H.read_text());assert h['source']
 for p,s in h['bindings'].items():assert sha(p)==s,p
 original=R/'build/ready62-smb2-final-native-1030-v1/class0/controller.lua'
 text=original.read_text();text=text[text.index('-- Cold controller-only'):]
 a,b=text.index('-- Read-only UI observer v6'),text.index('local function json(v)')
 text=text[:a]+(R/'tools/reference/benj_native_ui_1030_v1.lua').read_text()+'\n'+text[b:]
 text=text.replace('for i=1,P.variant do','for i=1,P.selects do')
 text=text.replace("{'S2ColdInit'","{'BmFresh'").replace("{'S2MainGame'","{'BmMarioMovement'").replace("{'S2Movement'","{'BmNativeMovement'")
 text=text.replace(",{'S2EndFrame',function()if main then sourceEnd=sourceEnd+1 end end}",'')
 text=text.replace("{'S2AudioNativeEntry'","{'AudioUpdate'")
 text=text.replace('updates=updates+1;lastCPU=cost','updates=updates+1;sourceEnd=sourceEnd+1;lastCPU=cost')
 text=text.replace("assert(r('S2Ready')==178 and r('S2NativeCharacter')==P.native_class,'Stable ownsource class/ready')","assert(r('BmOwner')==P.variant and r('MarioVariant')==P.variant,'Stable selected source owner')")
 text=text.replace("assert(r('S2Variant')==P.variant and r('S2Ready')==178,'Real selected SMB2 class ready');",'')
 text=text.replace("assert(sourceFresh>=1 and r('S2Health')==31 and r('S2NativeCharacter')==P.native_class,'Genuine sourceFresh health/class')","assert(sourceFresh>=1 and r('BmOwner')==P.variant,'Genuine Benj Fresh owner')")
 text=text.replace("clock=r('S2Clock'),own=active()and r('S2Ready')==178",'clock=0,own=false')
 text=text.replace("r('S2Clock')","r('FrameCounter')").replace("r('S2Health')","r('PlayerStatus')").replace("r('S2Ready')","r('BmOwner')").replace("r('S2NativeCharacter')","r('MarioVariant')")
 text=text.replace("assert(ppu(0x3f19)==0x16,'Native P2 red eye retained in gameplay');",'')
 text=text.replace('age>=20 and age<90','age>=20 and age<45').replace('age>=45 and age<63','age>=45 and age<110').replace('age>=220 and not main','age>=180 and not main')
 text=text.replace('bounded genuine SMB2 cold/menu/parser/movement and timing','bounded Benj cold/menu/lives/native movement and timing')
 text=text.replace('eye_role_original_red=true,','')
 text=text.replace("scope='Controller-only cold select/lives source body OAM/physicalCHR/PPU pixels, authenticated red-eye role, black lives and restored ground background, idle/walk/jump/land and passive timing. Root must review all four PNGs. No1-1 clear or60Hz claim.'","scope='Controller-only Benj menu/lives DMA, physical CHR, palette roles, actual pixels and native idle/walk/jump/land; shared33-SMC/live-register vector guards. Four PNGs. No1-1 or every-powerup/60Hz claim.'")
 assert "r('S2"not in text
 # Never alter the historical controller, UI observer or exact earlier tests.
 O.mkdir(parents=True);b=scoped_load(J/'candidate.nes');packets=[]
 for name,var,presses,page,colors in [('toad',5,2,901,[22,48,39]),('peach',6,3,908,[15,54,23])]:
  folder=O/name;folder.mkdir()
  args=dict(raw=0,slot=0,variant=var,selects=presses,native_class=var,first_page=page,colors=colors,sha256=h['candidate'],main_return=33621)
  prefix='L["BmOwner"]=23656\nCOLD_ARGS='+V.lua(args)+'\n'
  script=folder/'controller.lua';script.write_text(prefix+text,encoding='utf-8',newline='\n')
  run=folder/'run.py';run.write_text(V.RUN,encoding='utf-8',newline='\n')
  bindings=dict(h['bindings']);bindings.update({str(p):sha(p)for p in [H,Path(__file__),original,R/'tools/reference/benj_native_ui_1030_v1.lua',script,run,R/'tools/audit/prepare_smb2_firstlooks_bg_eye_v6.py',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]})
  ready=dict(prepared=True,native=False,ROM=str(J/'candidate.nes'),ROM_sha256=h['candidate'],source_handoff_sha256=sha(H),host_timeout_seconds=60,run_cap_bytes=536870912,max_files=64,max_PNGs=4,bindings=bindings)
  (folder/'ready.json').write_text(json.dumps(ready,indent=2)+'\n',encoding='utf-8',newline='\n')
  packets.append(dict(identity=name,ready_sha256=sha(folder/'ready.json'),path=str(folder/'ready.json')))
 (O/'prepared.json').write_text(json.dumps(dict(prepared=True,native=False,candidate=h['candidate'],packets=packets,no_RAM_writes=True),indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(prepared=packets,candidate=h['candidate'],source_bindings=len(h['bindings']),no_native_launch=True)))


if __name__=='__main__':main()
