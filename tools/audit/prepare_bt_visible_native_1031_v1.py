"""Controller-only BT admission checks require visible gameplay bodies too."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/bt-ready-native-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--joint',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();j=a.joint.resolve();o=a.output.resolve()
    assert j.is_relative_to(R/'build') and o.is_relative_to(R/'build') and not o.exists()
    stage=j.parent/'source-stage.json';q=json.loads(stage.read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    candidate=sha(j/'candidate.nes');assert q['candidate']==candidate
    b=scoped_load(j/'candidate.nes');o.mkdir();packets=[]
    for name in ['rash','zitz']:
        old=P/name;policy=json.loads((old/'ready.json').read_text())
        for p,h in policy['bindings'].items():assert sha(p)==h,p
        text=(old/'controller.lua').read_text()
        assert text.count(policy['ROM_sha256'])==1
        text=text.replace(policy['ROM_sha256'],candidate)
        text=replace(text,'local sourceDesc=nil','local sourceDesc,sourceGameDesc=nil,nil')
        text=replace(text,'{selected=0,lives=0}','{selected=0,lives=0,game=0}')
        text=replace(text,'local own=L.BtColdStanding+0x2000\n if ptr~=own then return end',
                     'local own=L.BtColdStanding+0x2000;local warm=L.BtRenderBuffer+0x2000\n if ptr~=own and ptr~=warm then return end')
        text=replace(text,"assert(size==32,'Complete original Battletoads descriptor')",
                     "assert(size>=4 and size<=48 and size%4==0,'Complete original Battletoads descriptor')")
        text=replace(text,' sourceDesc=q\nend,emu.callbackType.exec,L.MetaspriteRenderLoop)',
                     ' if ptr==own then sourceDesc=q else sourceGameDesc=q end\nend,emu.callbackType.exec,L.MetaspriteRenderLoop)')
        text=replace(text,'assert(bodyPage==P.first_page,',"assert(bodyPage>=P.first_page and bodyPage<P.first_page+(stage=='game'and 4 or 1),")
        text=replace(text,"local desc=assert(sourceDesc,'Real mapped body descriptor was observed')",
                     "local desc=assert(stage=='game'and sourceGameDesc or sourceDesc,'Real mapped body descriptor was observed')")
        text=replace(text,"if not colorsReady then if stage=='lives'then print('BT_LIVES_PALETTE_WAIT '..frame..' '..table.concat(observed,':'))end;return end",
                     "if not colorsReady then assert(stage~='game','Completed paired gameplay palette');return end")
        text=replace(text,"elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then uiDMA('lives',page)end",
                     "elseif phase=='launch'and r('OperMode')==1 and r('ScreenRoutineTask')==7 then uiDMA('lives',page)\n elseif phase=='game'and r('GameEngineSubroutine')==8 then uiDMA('game',page)end")
        text=replace(text,'frame-q.frame>=2 and frame-q.frame<=7',"frame-q.frame>=(stage=='game'and 1 or 2)and frame-q.frame<=7")
        text=replace(text,'local backgroundChecks=0','local backgroundChecks,gameBodyChecks=0,0')
        text=replace(text,'game_background_checks=backgroundChecks,', 'game_background_checks=backgroundChecks,gameplay_body_pixel_checks=gameBodyChecks,')
        text=replace(text,"elseif phase=='game'then\n  if active()then", "elseif phase=='game'then\n  if lastUI.game and frame-lastUI.game.frame==1 then renderedBody('game');gameBodyChecks=gameBodyChecks+1 end\n  if active()then")
        text=replace(text,"and clockErrors==0 and attackEvents>0 and hostWeapons>0,", "and clockErrors==0 and attackEvents>0 and hostWeapons>0 and gameBodyChecks>=20,")
        # Relinked RAM/ROM entry labels are always regenerated from this cart.
        names=['R0','BtColdStanding','MetaspriteRenderLoop','BtConstruct','BtMovement','BtCoreStep','BtHostReady','BtVariant','BtHostHit','BtWeapons','BtRenderBuffer']
        marker=text.index('-- Cold controller-only')
        prefix=text[:marker]
        import re
        prefix=re.sub(r'^L\["\w+"\]=\d+\n','',prefix,flags=re.M)
        prefix=re.sub(r'^B\["\w+"\]=\d+\n','',prefix,flags=re.M)
        prefix+=''.join(f'L["{n}"]={address(b,n)}\n'for n in names)
        prefix+=f'B["MetaspriteRenderLoop"]={(location(b,"MetaspriteRenderLoop")-16)//8192}\n'
        text=prefix+text[marker:]
        folder=o/name;folder.mkdir()
        (folder/'controller.lua').write_text(text,encoding='utf-8',newline='\n')
        (folder/'run.py').write_text((old/'run.py').read_text(),encoding='utf-8',newline='\n')
        files=[Path(__file__),old/'ready.json',old/'controller.lua',old/'run.py',stage,folder/'controller.lua',folder/'run.py',
               j/'candidate.nes',j/'candidate.dbg',j/'candidate.lbl',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
        prepared=dict(prepared=True,native=False,ROM=str(j/'candidate.nes'),ROM_sha256=candidate,host_timeout_seconds=90,
                      run_cap_bytes=536870912,max_files=64,max_PNGs=4,
                      scope='Real cold menu/lives and360controller gameframes; require original dual-palette DMA and visible gameplay body pixels, movement/jump/land/Battack, Main/ISR. No1-1/everypowerup/60Hz claim.',
                      bindings={str(p.resolve()):sha(p)for p in files})
        (folder/'ready.json').write_text(json.dumps(prepared,indent=2)+'\n',encoding='utf-8',newline='\n')
        packets.append(dict(name=name,ready=str(folder/'ready.json'),sha256=sha(folder/'ready.json')))
    (o/'prepared.json').write_text(json.dumps(dict(prepared=True,native=False,candidate=candidate,packets=packets),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(prepared=True,native=False,packets=packets)))


if __name__=='__main__':main()
