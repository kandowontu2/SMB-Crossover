"""Rebind distinct four-owner proposal to exact Princev65 and Bub9cf inputs.

The v15 measurement/source is read-only. No candidate or shared byte is written.
"""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    original=R/'tools/audit/measure_dkjr_retirement_1102_v15.py';src=original.read_text()
    src=src.replace('v15','v18').replace("hp=O/'hit-freeze-v12-CPU.json'","hp=O/'native-pause-v16-CPU.json'")
    src=src.replace("(O/'hit-freeze-v12.lbl')","(O/'native-pause-v16.lbl')").replace("H['DkHitThaw']","H['DkPauseThaw']")
    insertion='''
    bbpath=R/'build/bub-menu-candidate-1102-v2/combined-current-landing.json';bb=json.loads(bbpath.read_text())
    assert bb['expected_rebased_ROM_sha256']=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    cookie=next(bytes.fromhex(x['new'])for x in bb['patches']if len(bytes.fromhex(x['new']))==16)
    oldbb=bytes.fromhex('a727012954ecad01314374d1f7ed6441')
    source=re.sub(r'CoBBCookie:\\.byte [^\\n]+','CoBBCookie:.byte '+','.join('$%02x'%x for x in cookie),source)
    prince_source=(R/'build/prince-actor-1101-v1/collision-owner-v59.s').read_text()
    pcookie=re.search(r'PrCookie:\\n\\.byte [^\\n]+',prince_source)[0]
    source=re.sub(r'PrCookie:\\n\\.byte [^\\n]+',lambda m:pcookie,source)
'''
    needle="    source=(O/'admission-owner-v11.s').read_text()\n";assert src.count(needle)==1;src=src.replace(needle,needle+insertion)
    src=src.replace("selector=(O/'admission-selector-v11.s').read_text();", "selector=(O/'admission-selector-v11.s').read_text().replace('PpNativeRoute=$df29','PpNativeRoute=$df26');")
    src=src.replace("pp=R/'build/prince-actor-1101-v1/sunny-rebase-manifest-v54.json'", "pp=R/'build/prince-actor-1101-v1/native-manifest-v65.json'")
    needle="    assert A.sha(raw)==prior['expected_memory_only_SHA256']\n";assert src.count(needle)==1
    src=src.replace(needle,needle+'''
    for x in bb['patches']:
        if len(bytes.fromhex(x['new']))==16:continue
        at=x['offset'];assert raw[at:at+len(bytes.fromhex(x['old']))]==bytes.fromhex(x['old'])
        raw[at:at+len(bytes.fromhex(x['new']))]=bytes.fromhex(x['new'])
    bank65=raw[16+65*8192:16+66*8192];assert bank65.count(oldbb)==1
    at=16+65*8192+bank65.index(oldbb);raw[at:at+16]=cookie
''')
    needle="    before=bundle([(0xae00,(O/'admission-owner-v11.bin').read_bytes()),(0xab72,(O/'admission-owner-extra-v11.bin').read_bytes()),(0xa740,(O/'admission-selector-v11.bin').read_bytes())])"
    assert src.count(needle)==1;src=src.replace(needle,'    before=bundle([])')
    src=src.replace("(O/'admission-owner-v11.lbl')", "(R/'build/prince-actor-1101-v1/collision-owner-v59.lbl')")
    start=src.index("    helper=(O/'hit-freeze-v12.bin').read_bytes();");end=src.index('    out=dict(',start)
    src=src[:start]+'''
    helper=(O/'native-pause-v16.bin').read_bytes();cookie=sb[SL['DkCookie']-0xa740:SL['DkCookie']-0xa740+16]
    dk=[]
    for foreign,cbank in [(0,0),(28,2),(36,0),(37,2),(38,0),(39,2),(40,0),(255,2)]:
        mm=N.Bus(after);N.put(mm,CurrentBank=3,CurrentBankC=2,SelectedCharacter=foreign,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0)
        mm.raw_page(1,3);mm.raw_page(2,2);mm.ram[2][0x1540:0x1540+len(helper)]=helper
        for bank in [2,3]:mm.ram[bank][0x1fe0:0x1ff0]=cookie
        flags=bytes([1,0,7,0,64,0])
        for i,flag in enumerate(flags):mm[W.address(after,'Enemy_Flag')+i]=flag;mm[W.address(after,'Enemy_ID')+i]=9 if i%2 else 6
        c=N.NesMPU(memory=mm,pc=H['DkPauseBegin']);c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(10000):
            if c.pc==0x5fff:break
            c.step()
        else:raise AssertionError('DK actual lease begin bound')
        assert c.p&1 and N.get(mm,'TimerControl')==255
        N.put(mm,CurrentBank=0xd7,CurrentBankC=cbank);mm.raw_page(1,0xd7);mm.raw_page(2,cbank)
        z=N.invoke(mm,'CoRetire',a=0x51,x=4,y=0x73,p=0xf1)
        assert bytes(mm[W.address(after,'Enemy_Flag'):W.address(after,'Enemy_Flag')+6])==flags
        assert N.get(mm,'TimerControl')==0 and not mm.ram[2][0x440] and not any(mm.ram[2][0x445:0x44b])
        assert mm.ram[2][0x1fe0]==mm.ram[3][0x1fe0]==0
        start=len(mm.writes);N.invoke(mm,'CoRetire');assert not any(at==W.address(after,'TimerControl')or W.address(after,'Enemy_Flag')<=at<W.address(after,'Enemy_Flag')+6 for at,_ in mm.writes[start:])
        flags_preserved+=6;dk.append(dict(foreign=foreign,entry_C=cbank,CPU=z['CPU'],actual_native_pause_timer_and_empty_fields_restored_once=True,repeat_retire_no_native_flag_or_timer_writes=True))
''' +src[end:]
    src=src.replace("O/'hit-freeze-v12.bin'", "O/'native-pause-v16.bin'")
    src=src.replace("[Path(__file__),A.BASE,pp,", "[Path(__file__),R/'tools/audit/measure_dkjr_retirement_1102_v15.py',bbpath,R/'build/prince-actor-1101-v1/collision-owner-v59.s',A.BASE,pp,")
    src=src.replace("reference_private_Prince_SHA256=prior['expected_memory_only_SHA256'],", "reference_private_Prince_SHA256=prior['expected_memory_only_SHA256'],reference_private_Bub_SHA256=bb['expected_rebased_ROM_sha256'],cookie_rebind='Latest9cfBBcookie retained at newly linked CoBBCookie; original carrier301/666 and all Sunny5/Princev65 payload/gates preserved. No fixed-offset cookie overlap treated as disjoint.',")
    src=src.replace('already granted Prince v54','already granted Prince v65')
    src=src.replace('pendingBub9cf370B and privatePrincev64 ingress must compose disjointly','deliveredBub9cf370B and privatePrincev65 ingress must compose with the label-bound BB cookie rebind')
    src=src.replace('sourceAI freeze inclmisc/firebars','actual earned source hit/native-pause full phase, nested native powerup pipeline and rendered mechanical hazards')
    env={'__name__':'dkjr_distinct_v18','__file__':__file__};exec(compile(src,str(original),'exec'),env);env['main']()


if __name__=='__main__':main()
