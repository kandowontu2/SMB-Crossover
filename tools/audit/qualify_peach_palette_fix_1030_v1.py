"""Check the palette fix, archive its source, prepare bounded native runs."""
from pathlib import Path
import json
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
import benj_current_menu_controls_1030_v1 as M
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from finalize_ff_current_component_v3 import dependencies

P=R/'build/benj-menu-unlocked-1030-v3'
O=R/'build/peach-palette-fix-1030-v1';J=O/'joint'
N=R/'build/peach-palette-native-1030-v1'
D=R/'docs/qa/checkpoints/2026-10-30/peach-palette-correction-source'


def save(p,d):B.write(p,json.dumps(d,indent=2)+'\n')


def main():
    assert not D.exists()and not N.exists()and not(O/'handoff.json').exists()
    h=json.loads(B.read(P/'handoff.json'));B.bound(h)
    s=json.loads(B.read(O/'source-stage.json'));B.bound(s)
    old,new=[scoped_load(p/'candidate.nes')for p in [P/'joint',J]]
    outcomes=[];negative=None
    for variant in range(7):
        for area in range(4):
            for tier in range(3):
                for flags in [0x30,0x31,0x71,0xf1]:
                    cases=[]
                    for bundle in [old,new]:
                        q=M.T.make(bundle,0)
                        q.put(MarioVariant=variant,AreaType=area,PlayerStatus=tier,
                            CurrentPlayer=0,VRAM_Buffer1_Offset=0,VRAM_Buffer1=0)
                        c,tr,path,info=M.T.invoke(q,'GetPlayerColors',a=91,x=3,y=5,p=flags)
                        end=q.get('VRAM_Buffer1_Offset')
                        start=address(bundle,'VRAM_Buffer1')+end-7
                        packet=bytes(q.m[start:start+8])
                        cases.append((M.regs(c),M.T.app(q,tr),q.m.banks[:],packet))
                    if variant<6:
                        assert cases[0]==cases[1],('Foreign palette changed',variant,area,tier,flags)
                    else:
                        assert cases[0][3][4:7]==bytes.fromhex('0f3617')
                        assert cases[1][3][4:7]==bytes.fromhex('163027')
                        assert cases[0][0]==cases[1][0]and cases[0][2]==cases[1][2]
                        assert cases[0][3][:4]==cases[1][3][:4]and cases[0][3][7:]==cases[1][3][7:]
                        if negative is None:negative=dict(old_packet=cases[0][3].hex(),corrected_packet=cases[1][3].hex(),
                            original_donor_normal_P2='163027',wrong_prior_expected='0f3617')
                    outcomes.append(dict(variant=variant,area=area,status=tier,flags=flags,packet=cases[1][3].hex()))
    controls=dict(passed=True,CPU_only=True,native=False,candidate=s['candidate'],
        foreign_palette_pairs=288,corrected_Peach_packets=48,old_wrong_palette_regression=negative,
        public_and_private_labels_exact=True,ROM_delta_bytes=3,
        cases=outcomes,limitations=s['limits'],bindings={str(p):B.sha(p)for p in [Path(__file__),
            O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl']})
    save(O/'controls.json',controls)
    own={p for p in J.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg','.chr']}
    own|={J/n for n in ['native-pose-map.bin','toad-visible-pairs.bin','peach-visible-pairs.bin']}
    own|=set(dependencies(J/'main.dep'))|set(dependencies(J/'union.dep'))
    own|={Path(__file__),R/'tools/audit/prepare_peach_palette_fix_1030_v1.py',R/'tools/audit/benj_peach_palette_trace_1030_v1.py'}
    own|={O/n for n in ['controls.json','source-stage.json','main-build.json','union-build.json','final-link.json']}
    own|={R/'build/benj-peach-palette-trace-1030-v2'/n for n in ['trace.json','ram.bin','ppu.bin','oam.bin']}
    assert all(p.is_file()and p.resolve().is_relative_to(R)and p.suffix.lower()not in ['.nes','.o','.dbg','.lbl','.map','.exe']for p in own)
    D.mkdir(parents=True)
    archive=D/'source-only.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(own):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in own:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    assert archive.stat().st_size<5*1024*1024
    bindings=dict(h['bindings']);bindings.update({str(p):B.sha(p)for p in own})
    bindings.update({str(p):B.sha(p)for p in [P/'handoff.json',archive,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'main.o',J/'consumer-18.o',J/'benj-chr.o']})
    successor=dict(source=True,native=False,installed=False,status='PEACH_PALETTE_CORRECTION_SOURCE_FROZEN_NATIVE_PENDING',
        candidate=s['candidate'],parent=s['parent'],joint=str(J),normal_colors='163027',
        delta_offsets=s['delta_offsets'],enabled=64,limitations=s['limits'],bindings=bindings)
    save(O/'handoff.json',successor);save(D/'handoff.json',successor)
    save(D/'manifest.json',dict(candidate=s['candidate'],handoff_sha256=B.sha(O/'handoff.json'),archive_sha256=B.sha(archive),
        archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():B.sha(p)for p in sorted(own)}))
    B.write(D/'README.md',"Corrects the prior98048319 palette-row mistake. The earlier48 packets and two native smokes passed an incorrect expected Peach row0F3617; they did not prove its authenticity. Original donor selector751D returnsP2 for Peach in normal small/big forms, and actual donor OAM usesP2. Its normal visible row is163027. The successor changes only those3 ROM constants, preserving every label, allCHR and the previous64 enabled identities. Original fire-form selector returnsP0; full fire/star/area progression is still unfinished. Native visual checks are prepared separately. Historical evidence is retained unchanged.\n")
    ready_packets=[]
    for name in ['toad','peach']:
        previous=R/'build/benj-native-1030-v1'/name
        folder=N/name;folder.mkdir(parents=True)
        text=B.read(previous/'controller.lua').replace(s['parent'],s['candidate'])
        if name=='peach':
            assert '["colors"]={15,54,23}'in text
            text=text.replace('["colors"]={15,54,23}','["colors"]={22,48,39}')
        B.write(folder/'controller.lua',text)
        B.write(folder/'run.py',B.read(previous/'run.py'))
        ready=json.loads(B.read(previous/'ready.json'))
        b=dict(bindings)
        for p in [O/'handoff.json',Path(__file__),previous/'controller.lua',folder/'controller.lua',folder/'run.py',
                  R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',Path('C:/mesen2/Mesen.exe')]:b[str(p)]=B.sha(p)
        ready.update(ROM=str(J/'candidate.nes'),ROM_sha256=s['candidate'],source_handoff_sha256=B.sha(O/'handoff.json'),bindings=b)
        save(folder/'ready.json',ready)
        ready_packets.append(dict(identity=name,path=str(folder/'ready.json'),sha256=B.sha(folder/'ready.json')))
    save(N/'prepared.json',dict(prepared=True,native=False,candidate=s['candidate'],packets=ready_packets))
    print(json.dumps(dict(candidate=s['candidate'],source_bindings=len(bindings),archive_members=len(own),
        archive_bytes=archive.stat().st_size,foreign_pairs=288,Peach_packets=48,native_launch=False),indent=2))


if __name__=='__main__':main()
