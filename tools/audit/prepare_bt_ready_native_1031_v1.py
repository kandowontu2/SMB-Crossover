"""Prepare bounded controller-only Rash/Zitz native checks; root launches later."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import prepare_smb2_firstlooks_bg_eye_v6 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

J = R/'build/bt-ready-menu-1031-v2/joint'
O = R/'build/bt-ready-native-1031-v1'
P = R/'build/smb3plus-current66-native-1031-v1/toad'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8', newline='\n')


def replace(s, old, new):
    assert old in s, old
    return s.replace(old, new)


def main():
    assert not O.exists()
    stage = json.loads((J.parent/'source-stage.json').read_text())
    for p,h in stage['bindings'].items():
        assert sha(p) == h, p
    assert stage['candidate'] == sha(J/'candidate.nes') == 'f0b7b9b80ac59b546cee599b9efcb5337b970b11638a669ace78a67dd024724d'
    b = scoped_load(J/'candidate.nes')
    s = (P/'controller.lua').read_text()
    s = s[s.index('-- Cold controller-only'):]
    s = replace(s, " or r('ObjectMetasprite')~=233", '')
    s = replace(s, "local own=r('SmPosePtr')+256*emu.read(L.SmPosePtr+1,emu.memType.nesDebug)",
                'local own=L.BtColdStanding+0x2000')
    s = replace(s, 'size>=4 and size<=24 and size%4==0', 'size==32')
    s = replace(s, "r('M3Variant')", "(r('FmGroups')&32)")
    s = replace(s, 'bodyPage>=P.first_page and bodyPage<P.first_page+25', 'bodyPage==P.first_page')
    s = replace(s, "for i=1,3 do assert(ppu(0x3f10+i)==P.colors[i],'Actual original SMB3+ P0 '..stage)end",
                "for i=1,3 do assert(ppu(0x3f10+i)==P.colors[i],'Actual original BT P0 '..stage);assert(ppu(0x3f14+i)==P.P1[i],'Actual original BT P1 '..stage)end")
    s = replace(s, 'part.tile<64 and part.attr&3==0', 'part.tile<64 and part.attr&3<=1')
    s = replace(s, 'ppu(0x3f10+value)', 'ppu(0x3f10+(part.attr&3)*4+value)')
    s = replace(s, "{'M3Reset',function()sourceFresh=sourceFresh+1 end}", "{'BtConstruct',function()sourceFresh=sourceFresh+1 end}")
    s = replace(s, "{'M3Movement',function()if main then sourceMain=sourceMain+1 end end}",
                "{'BtMovement',function()if main then sourceMain=sourceMain+1;assert(r('BtHostReady')==1 and r('BtVariant')==P.variant,'Real mapped ready BT identity')end end}")
    s = replace(s, "{'M3Step',function()if main then sourceMove=sourceMove+1 end end}", "{'BtCoreStep',function()if main then sourceMove=sourceMove+1 end end}")
    s = replace(s, "if bank(L[item[1]])==B[item[1]]then item[2]()end", "if item[1]=='AudioUpdate'and bank(L[item[1]])==B[item[1]]or item[1]~='AudioUpdate'and r('CurrentBank')==3 then item[2]()end")
    s = replace(s, "assert(r('M3Ready')==179 and (r('FmGroups')&32)==P.variant,'Stable selected source owner')",
                "assert(r('SelectedCharacter')==33 and (r('FmGroups')&32)==P.variant,'Stable selected BT owner')")
    s = replace(s, "ready=r('M3Ready'),native_class=(r('FmGroups')&32)", "native_class=(r('FmGroups')&32),attack_events=attackEvents,host_weapon_calls=hostWeapons")
    s = replace(s, 'local backgroundChecks=0', 'local backgroundChecks=0\nlocal attackEvents,hostWeapons=0,0\nfor _,v in ipairs({{\'BtHostHit\',function()attackEvents=attackEvents+1 end},{\'BtWeapons\',function()hostWeapons=hostWeapons+1 end}})do\n emu.addMemoryCallback(function()if r(\'CurrentBank\')==3 then v[2]()end end,emu.callbackType.exec,L[v[1]])\nend')
    s = replace(s, "assert(sourceFresh>=1 and r('M3Ready')==179,'Genuine M3 reset/ready owner');assert(r('ObjectMetasprite')==233,'SourceSMB2bodypublisher');",
                "assert(sourceFresh>=1,'Genuine BT construction');")
    s = replace(s, "if P.raw==3 or P.raw==24 then if age>=25 and age<90 then b.b=true end end",
                "if age>=180 and age<220 or age>=240 and age<280 then b.b=true end")
    s = replace(s, "and clockErrors==0,'bounded SMB3+", "and clockErrors==0 and attackEvents>0 and hostWeapons>0,'bounded BT")
    s = replace(s, "shot('selected');phase='launch'", "for i=0,15 do assert(ppu(0x2328+i)==P.menu_tiles[i+1],'Actual full-width BT menu name')end;shot('selected');phase='launch'")
    s = s.replace('SMB3+ Toad/Peach', 'Battletoads Rash/Zitz').replace('SMB3+', 'Battletoads')
    assert 'M3Ready' not in s and 'M3Variant' not in s and 'ObjectMetasprite' not in s
    O.mkdir()
    packets=[]
    for name,variant,colors in [('rash',0,[15,10,26]),('zitz',32,[15,23,39])]:
        letters=[ord(x)-ord('A')+10 if x!=' ' else 36 for x in f'      {name.upper()}      ']
        assert len(letters)==16
        args=dict(raw=33,slot=23,variant=variant,selects=variant//32,first_page=915,colors=colors,P1=[24,40,32],
                  sha256=stage['candidate'],main_return=33621,menu_tiles=letters)
        folder=O/name
        folder.mkdir()
        names=['R0','BtColdStanding','MetaspriteRenderLoop','BtConstruct','BtMovement','BtCoreStep','BtHostReady','BtVariant','BtHostHit','BtWeapons']
        prefix='COLD_ARGS='+V.lua(args)+'\n'+''.join(f'L["{n}"]={address(b,n)}\n' for n in names)
        prefix+=f'B["MetaspriteRenderLoop"]={(location(b,"MetaspriteRenderLoop")-16)//8192}\n'
        write(folder/'controller.lua',prefix+s)
        runner=(P/'run.py').read_text()
        write(folder/'run.py',runner)
        files=[Path(__file__),P/'controller.lua',P/'run.py',J.parent/'source-stage.json',folder/'controller.lua',folder/'run.py',
               J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]
        q=dict(prepared=True,native=False,ROM=str(J/'candidate.nes'),ROM_sha256=stage['candidate'],host_timeout_seconds=90,
               run_cap_bytes=536870912,max_files=64,max_PNGs=4,
               scope='Controller-only cold title/selection/lives plus360 gameframes, walking/jump/land/two B holds. Original8part cold body/two-role palettes and actual DMA/pixels; physical Main/ISR observations. No RAM writes/videos/full1-1 claim.',
               bindings={str(p.resolve()):sha(p)for p in files})
        write(folder/'ready.json',json.dumps(q,indent=2)+'\n')
        packets.append(dict(name=name,ready=str(folder/'ready.json'),sha256=sha(folder/'ready.json')))
    write(O/'prepared.json',json.dumps(dict(prepared=True,native=False,ROM_sha256=stage['candidate'],packets=packets),indent=2)+'\n')
    print(json.dumps(dict(prepared=True,native=False,packets=packets)))


if __name__ == '__main__':
    main()
