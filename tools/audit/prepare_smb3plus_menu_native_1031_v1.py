"""Bounded controller-only SMB3+ Toad/Peach menu/lives/movement checks."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
import prepare_functional_roster_visuals58_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

J=R/'build/smb3plus-menu-host-1031-v4/joint'
O=R/'build/smb3plus-menu-native-1031-v1'


def main():
    assert not O.exists()
    stage=J.parent/'source-stage.json';controls=J.parent/'menu-controls-v1.json'
    s,c=[json.loads(B.read(p)) for p in [stage,controls]]
    for d in [s,c]:B.bound(d)
    assert c['passed'] and c['candidate']==s['candidate']
    b=scoped_load(J/'candidate.nes')
    original=R/'build/peach-palette-native-1030-v1/peach/controller.lua'
    ui_parent=R/'tools/reference/bowser_native_ui_1031_v2.lua'
    ui=R/'tools/reference/smb3plus_native_ui_1031_v1.lua'
    own=B.read(ui_parent)
    own=own.replace('size>=28 and size<=48','size>=4 and size<=24')
    own=own.replace("r('FmAlts')&8","r('M3Variant')")
    own=own.replace('bodyPage==P.first_page','bodyPage>=P.first_page and bodyPage<P.first_page+25')
    own=own.replace('count>150','count>40').replace('Bowser','SMB3+')
    if ui.exists():assert B.read(ui)==own
    else:B.write(ui,own)
    text=B.read(original);text=text[text.index('-- Cold controller-only'):]
    begin,end=text.index('-- Read-only actual DMA'),text.index('local function json(v)')
    text=text[:begin]+own+'\n'+text[end:]
    text=text.replace("{'BmFresh',function()sourceFresh=sourceFresh+1 end}",
        "{'M3Reset',function()sourceFresh=sourceFresh+1 end}")
    text=text.replace("{'BmMarioMovement',function()if main then sourceMain=sourceMain+1 end end}",
        "{'M3Movement',function()if main then sourceMain=sourceMain+1 end end}")
    text=text.replace("{'BmNativeMovement',function()if main then sourceMove=sourceMove+1 end end}",
        "{'M3Step',function()if main then sourceMove=sourceMove+1 end end}")
    text=text.replace("r('BmOwner')==P.variant and r('MarioVariant')==P.variant",
        "r('M3Ready')==179 and r('M3Variant')==P.variant")
    text=text.replace("r('BmOwner')==P.variant","r('M3Ready')==179")
    text=text.replace("ready=r('BmOwner'),native_class=r('MarioVariant')",
        "ready=r('M3Ready'),native_class=r('M3Variant')")
    text=text.replace('Genuine Benj Fresh owner','Genuine M3 reset/ready owner')
    text=text.replace('source_fresh=sourceFresh','source_reset_calls=sourceFresh')
    text=text.replace('source_EndFrame=sourceEnd','completed_Main_returns=sourceEnd')
    text=text.replace('age<110 then b.a=true','age<200 then b.a=true')
    text=text.replace('age>=180 and not main','age>=360 and not main')
    text=text.replace('bounded Benj cold/menu/lives/native movement and timing',
        'bounded SMB3+ menu/lives/native idle/walk/jump/hover-release/land and timing')
    text=text.replace('Controller-only Benj menu/lives DMA, physical CHR, palette roles, actual pixels and native idle/walk/jump/land; shared33-SMC/live-register vector guards. Four PNGs. No1-1 or every-powerup/60Hz claim.',
        'Controller-only SMB3+ Toad/Peach select/lives pixels, palette, real movement and jump/land, genuine Main/ISR observations. Four PNGs. No1-1, every-powerup, complete donor special-move or60Hz claim.')
    assert "r('Bm" not in text and 'BmMarioMovement' not in text
    O.mkdir();packets=[]
    for name,variant,page,colors in [('toad',2,969,[17,54,15]),('peach',3,994,[37,54,7])]:
        folder=O/name;folder.mkdir()
        args=dict(raw=17,slot=16,variant=variant,selects=variant,first_page=page,colors=colors,
            sha256=s['candidate'],main_return=33621)
        names=['R0','SmPosePtr','M3Variant','M3Ready','M3Reset','M3Movement','M3Step','MetaspriteRenderLoop']
        prefix='COLD_ARGS='+V.lua(args)+'\n'+''.join(f'L["{n}"]={address(b,n)}\n' for n in names)
        prefix+=''.join(f'B["{n}"]={(location(b,n)-16)//8192}\n' for n in names if n not in ['R0','SmPosePtr','M3Variant','M3Ready'])
        script=folder/'controller.lua';B.write(script,prefix+text)
        runner=folder/'run.py';B.write(runner,V.RUN)
        bindings={str(p):B.sha(p) for p in [stage,controls,Path(__file__),original,ui_parent,ui,script,runner,
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',R/'tools/run_mesen.py',
            R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]}
        d=dict(prepared=True,native=False,ROM=str(J/'candidate.nes'),ROM_sha256=s['candidate'],
            host_timeout_seconds=60,run_cap_bytes=536870912,max_files=64,max_PNGs=4,bindings=bindings)
        B.write(folder/'ready.json',json.dumps(d,indent=2)+'\n')
        packets.append(str(folder/'ready.json'))
    B.write(O/'prepared.json',json.dumps(dict(prepared=True,native=False,no_RAM_writes=True,
        candidate=s['candidate'],packets=packets),indent=2)+'\n')
    print(json.dumps(dict(prepared=packets,native=False)))


if __name__=='__main__':main()
