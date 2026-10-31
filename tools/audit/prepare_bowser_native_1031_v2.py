"""Prepare bounded controller-only tests of a frozen current64+Bowser build."""
from pathlib import Path
import argparse
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--handoff',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();H=a.handoff.resolve();O=a.output.resolve()
    assert not O.exists() and O.is_relative_to(R/'build')
    h=json.loads(B.read(H));B.bound(h)
    J=Path(h['joint']);bundle=scoped_load(J/'candidate.nes')
    assert h['candidate']==B.sha(J/'candidate.nes')
    # The actual source successor must retain the corrected current64 parent.
    assert bundle['raw'][514822:514825]==bytes.fromhex('163027')
    original=R/'build/peach-palette-native-1030-v1/peach/controller.lua'
    ui=R/'tools/reference/bowser_native_ui_1031_v2.lua'
    text=B.read(original);text=text[text.index('-- Cold controller-only'):]
    begin,end=text.index('-- Read-only actual DMA'),text.index('local function json(v)')
    text=text[:begin]+B.read(ui)+'\n'+text[end:]
    text=text.replace('local shots=0','local lastReady,lastHP,emitted=0,0,0\nlocal shots=0')
    text=text.replace("shots<=4,'Four PNG bound'","shots<=5,'Five PNG bound'")
    text=text.replace("{'BmFresh',function()sourceFresh=sourceFresh+1 end}","{'BwConstruct',function()sourceFresh=sourceFresh+1 end}")
    text=text.replace("{'BmMarioMovement',function()if main then sourceMain=sourceMain+1 end end}",
        "{'BwMovement',function()if main then sourceMain=sourceMain+1;lastReady=emu.read(0xbe26,emu.memType.nesDebug);lastHP=emu.read(0xbe29,emu.memType.nesDebug)end end}")
    text=text.replace("{'BmNativeMovement',function()if main then sourceMove=sourceMove+1 end end}",
        "{'Bw3Step',function()if main then sourceMove=sourceMove+1 end end},{'Bw1Step',function()if main then sourceMove=sourceMove+1 end end},{'BwWeaponTail',function()if main then sourceEnd=sourceEnd+1 end end},{'BwSpawnFire',function()if main then emitted=emitted+1 end end}")
    text=text.replace('updates=updates+1;sourceEnd=sourceEnd+1;lastCPU=cost','updates=updates+1;lastCPU=cost')
    text=text.replace("assert(r('BmOwner')==P.variant and r('MarioVariant')==P.variant,'Stable selected source owner')",
        "assert(lastReady==183 and r('FmAlts')&8==P.variant,'Stable selected source owner')")
    text=text.replace("assert(sourceFresh>=1 and r('BmOwner')==P.variant,'Genuine Benj Fresh owner')",
        "assert(sourceFresh>=1,'Genuine Bowser cold construction')")
    text=text.replace("ready=r('BmOwner'),native_class=r('MarioVariant')","ready=lastReady,native_class=P.variant,HP=lastHP,source_fire_calls=emitted")
    text=text.replace("if P.raw==3 or P.raw==24 then if age>=25 and age<90 then b.b=true end end",
        "if age>=105 and age<109 or age>=175 and age<179 then b.b=true end")
    text=text.replace('age>=180 and not main','age>=220 and not main')
    text=text.replace("sourceAudio>0 and vectorGuards>60", "sourceAudio>0 and emitted>=1 and vectorGuards>60")
    text=text.replace("elseif phase=='game'then\n  if active()then", "elseif phase=='game'then\n  if age==160 then shot('fire')end\n  if active()then")
    text=text.replace('bounded Benj cold/menu/lives/native movement and timing','bounded Bowser cold/menu/lives/native movement/fire and timing')
    text=text.replace('Controller-only Benj menu/lives DMA, physical CHR, palette roles, actual pixels and native idle/walk/jump/land; shared33-SMC/live-register vector guards. Four PNGs. No1-1 or every-powerup/60Hz claim.',
        'Controller-only Bowser menu/lives DMA, physical CHR, palette roles, actual pixels, native idle/walk/jump/land and source breath. Shared33-SMC/live-register vector guards. Five PNGs. No1-1/every-powerup or60Hz claim.')
    assert "r('Bm"not in text and 'BmMarioMovement'not in text
    O.mkdir(parents=True);packets=[]
    for name,var,presses,page in [('smb3',0,0,825),('smb1',8,1,824)]:
        folder=O/name;folder.mkdir()
        args=dict(raw=27,slot=26,variant=var,selects=presses,first_page=page,
            colors=[26,48,39],sha256=h['candidate'],main_return=33621)
        labels={n:address(bundle,n) for n in ['R0','SmPosePtr','FmAlts','BwConstruct','BwMovement',
            'Bw3Step','Bw1Step','BwWeaponTail','BwSpawnFire','MetaspriteRenderLoop']}
        prefix='COLD_ARGS='+V.lua(args)+'\n'+''.join(f'L["{n}"]={value}\n'for n,value in labels.items())
        prefix+=''.join(f'B["{n}"]=3\n'for n in ['BwConstruct','BwMovement','Bw3Step','Bw1Step','BwWeaponTail','BwSpawnFire'])
        script=folder/'controller.lua';B.write(script,prefix+text)
        run=folder/'run.py';B.write(run,V.RUN)
        bindings=dict(h['bindings'])
        bindings.update({str(p):B.sha(p)for p in [H,Path(__file__),original,ui,script,run,
            R/'tools/audit/prepare_smb2_firstlooks_bg_eye_v6.py',R/'tools/run_mesen.py',
            R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]})
        ready=dict(prepared=True,native=False,ROM=str(J/'candidate.nes'),ROM_sha256=h['candidate'],
            source_handoff_sha256=B.sha(H),host_timeout_seconds=60,run_cap_bytes=536870912,
            max_files=64,max_PNGs=5,bindings=bindings)
        B.write(folder/'ready.json',json.dumps(ready,indent=2)+'\n')
        packets.append(dict(identity=name,path=str(folder/'ready.json'),ready_sha256=B.sha(folder/'ready.json')))
    B.write(O/'prepared.json',json.dumps(dict(prepared=True,native=False,candidate=h['candidate'],
        packets=packets,no_RAM_writes=True),indent=2)+'\n')
    print(json.dumps(dict(prepared=packets,candidate=h['candidate'],native=False)))


if __name__=='__main__':main()
