"""Execute the scene wrapper and real cold/warm loader with a scoped old-chain stub."""
from pathlib import Path
import json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import prepare_metal_storm_scene_1101_v13 as P
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
from arthur_cache_host_controls_v1 import OverlayMemory
from verify_native_relocation import NesMPU
def main():
    s=json.loads((P.O/'scene-assembly.json').read_text())
    for p,h in s['bindings'].items():assert P.sha(p)==h,p
    b=qualified(P.O/'candidate.nes');minimum=255;calls=0
    def put(m,**kw):
        for n,v in kw.items():m[address(b,n)]=v
    def make(identity):
        m=OverlayMemory(b);m.raw_page(1,151);m.raw_page(2,215)
        put(m,CurrentBank=151,CurrentBankC=215,SelectedCharacter=identity,OperMode=1,GameEngineSubroutine=8,
            FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,NmiDisable=255,
            HorizontalScroll=73,VerticalScroll=32,ReloadCHRBank=7,X5WideChrActive=0)
        m.ppuctrl=160
        for i,v in enumerate([18,20,21,22,23,24,25,26,4,5,6,7]):m[address(b,'CurrentCHRBank')+i]=v;m[address(b,'X5ChrMode')+i]=0
        for bank in [2,3]:m.ram[bank][:]=bytes((i*17+bank*29+7)&255 for i in range(8192))
        for i in range(11):m[i]=(31*i+15)&255
        return m
    def invoke(m):
        nonlocal minimum,calls
        entry=s['labels']['Ms13Scene'];m[0x16a]=85;m[0x16c]=entry&255;m[0x16d]=entry>>8
        maps=m.rawtags[:];zp=bytes(m[:11]);oldcalls=0;loaded=False
        c=NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=149,7,91,0x71,224;c.stPushWord(0x5ffe)
        for _ in range(1_000_000):
            if c.pc==0x5fff:break
            minimum=min(minimum,c.sp)
            if c.pc==address(b,'KrSceneInit') and m.rawtags[1]==157:
                # Explicit isolation: prior scene chain is not emulated here.
                # Its call ordering and preservation are observed; Main proof remains separate.
                oldcalls+=1;assert not loaded;c.pc=(c.stPopWord()+1)&65535;continue
            if c.pc==s['labels']['Ms8Load'] and m.rawtags[1]==244:loaded=True;assert oldcalls==1
            if c.pc>=0x8000:assert m.rawtags[(c.pc-0x8000)//8192]&128,('Unauthenticated RAM execution',hex(c.pc))
            assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
        else:raise AssertionError(('instruction bound',hex(c.pc)))
        assert c.sp==224 and oldcalls==1
        assert (c.a,c.x,c.y,c.p&0xcf)==(85,7,91,0x41),(c.a,c.x,c.y,c.p)
        assert m.rawtags==maps and bytes(m[:11])==zp
        calls+=1
    foreign=0
    for identity in range(64):
        if identity==35:continue
        m=make(identity);before=[bytes(m.ram[k]) for k in [2,3]];invoke(m)
        assert [bytes(m.ram[k]) for k in [2,3]]==before and m.ppu_reads==0
        foreign+=1
    m=make(35);invoke(m)
    actor=(P.M/'native-actor.bin').read_bytes();render=(P.M/'native-render.bin').read_bytes();cookie=(P.M/'native-cookie.bin').read_bytes()
    assert m.ram[3][:len(actor)]==actor and m.ram[2][0xd00:0xd00+len(render)]==render
    assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3]) and m.ram[2][0x800]==0
    reads=m.ppu_reads;m.ram[2][0x800]=167;before=[bytes(m.ram[k]) for k in [2,3]];invoke(m)
    assert m.ram[2][0x800]==0 and m.ppu_reads==reads
    expect=bytearray(before[0]);expect[0x800]=0
    assert m.ram[2]==expect and bytes(m.ram[3])==before[1]
    rejects=0
    for key,value in [('OperMode',0),('FamilyMainCommit',0),('DisableScreenFlag',0),('Mirror_PPUMASK',24),('NmiDisable',0)]:
        m=make(35);put(m,**{key:value});before=[bytes(m.ram[k]) for k in [2,3]];invoke(m)
        assert [bytes(m.ram[k]) for k in [2,3]]==before and m.ppu_reads==0
        rejects+=1
    q=dict(passed=True,ROM_sha256=s['ROM_sha256'],foreign_identities_preserved=foreign,cold_loader=True,
           warm_scene_constructor_marker_reset=True,invalid_scene_rejections=rejects,calls=calls,minimum_standalone_SP=minimum,
           prior_scene_chain='Explicit KrSceneInit no-op stub; only ordering/preservation tested here.',
           limitations='Not actual Main/IRQ or native gameplay evidence; menu remains locked. No injury, combat, audio or full-stage claim.')
    (P.O/'scene-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
    d=R/'docs/qa/checkpoints/2026-11-01/metal-storm-scene-v13';d.mkdir(exist_ok=True)
    files=[P.O/n for n in ['component.s','component.cfg','component.lbl','scene-assembly.json','scene-CPU.json']]
    files += [P.M/'native-cookie.bin',P.REF,Path(P.__file__),Path(__file__)]
    packet=d/'source-and-proof.zip'
    with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED) as z:
        for f in files:z.write(f,f.relative_to(R).as_posix())
    assert packet.stat().st_size<500_000
    q['packet_sha256']=P.sha(packet);q['packet_bytes']=packet.stat().st_size
    (d/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    path=R/'docs/qa/continuation-current.json';current=json.loads(path.read_text())
    current['previous_goal_turn_classification']='progress'
    current['metal_storm_scene_integration']=dict(checkpoint=str(d.relative_to(R)),candidate=str(P.O/'candidate.nes'),installed=False,
        next='Implement menu resolution/retirement and start handling; complete original health/combat/audio. Then actual Main/IRQ and native gameplay tests. Current public nightly remains7ec9.')
    current['current_priority']='Metal Storm scene loader merged with current7ec9, focused cold/warm tests pass. Finish menu/lifecycle, health/combat/audio and native verification. Mario the Tank natural pickups verified; full-stage roster goal remains incomplete.'
    path.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps(q))
if __name__=='__main__':main()
