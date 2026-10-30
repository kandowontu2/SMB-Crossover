"""Compile a sizing proposal, inventory actual consumers; install no hooks."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/ff-fx-world-marker-proposal-v2';O=R/'build/ff-fx-epoch-proposal-v1'
S=R/'tools/reference/ff_fx_epoch_rom_proposal_v1.s'

def main():
    assert not O.exists();O.mkdir();d=json.loads((P/'source-closure.json').read_text());files={Path(__file__),S,P/'source-closure.json'}
    for p,h in d['bindings'].items():assert B.sha(p)==h,p
    b=qualified(P/'joint/candidate.nes');names=['FwActionTick','FwWeapons','FwEnemyContact','FwForgetEnemy']
    refs={n:[]for n in names}
    for f in(P/'joint').rglob('*'):
        if f.is_file()and f.suffix in['.s','.inc']:
            files.add(f)
            for i,line in enumerate(f.read_text(errors='replace').splitlines(),1):
                for n in names:
                    if re.search(r'\b'+n+r'\b',line):refs[n].append(dict(path=str(f.resolve()),line=i,text=line.strip()))
    assert all(len(rows)==1 and rows[0]['text'].startswith('FW_GATE ')for rows in refs.values())
    link=json.loads((P/'joint/final-link.json').read_text())['command'];objects=[Path(x)for x in link if x.endswith('.o')]
    imports=[]
    for f in objects:
        q=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-imports',str(f)],cwd=R,capture_output=True,text=True)
        assert q.returncode==0;qnames=re.findall(r'Name:\s*"([^"]+)"',q.stdout)
        assert not set(names)&set(qnames),(str(f),set(names)&set(qnames))
        imports.append(dict(object=str(f.resolve()),sha256=B.sha(f),retired_names_imported=[]));files.add(f)
    targets=[];at=location(b,'FwServiceVeneers')
    for i in range(36):
        op=b['raw'][at+3*i:at+3*i+3];assert op[0]==0x4c
        target=int.from_bytes(op[1:],'little');assert target not in[address(b,n)for n in names];targets.append(target)
    assert [address(b,n)for n in names]==[0xadde,0xadf8,0xae12,0xae2c]
    assert address(b,'FwProjectileEntry')==0xae46
    occupied=[]
    for v in b['segs'].values():
        if str(v.get('oname','')).strip('"').endswith('ram3.bin'):
            a=int(v['start'],0);z=a+int(v['size'],0);occupied.append((a,z,v['name'].strip('"')))
    occupied.sort();occupied.append((0xbfe0,0xbff0,'own16Bcookie'))
    gaps=[];cursor=0xa000
    image=(P/'joint/ram3.bin').read_bytes()
    for a,z,n in sorted(occupied):
        if a>cursor:
            assert set(image[cursor-0xa000:a-0xa000])<={255}
            gaps.append(dict(start=cursor,end=a,bytes=a-cursor))
        cursor=max(cursor,z)
    if cursor<0xc000:
        assert set(image[cursor-0xa000:])<={255};gaps.append(dict(start=cursor,end=0xc000,bytes=0xc000-cursor))
    cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','--create-full-dep',str(O/'rom-glue.dep'),'-o',str(O/'rom-glue.o'),str(S)]
    B.save(O/'compile-validated-outputs.json',validate(cmd,O,cwd=R));B.run(O,cmd,'compile')
    files|={f for f in O.rglob('*')if f.is_file()}|{P/'joint/candidate.nes',P/'joint/candidate.dbg',R/'tools/audit/private_build_outputs_v1.py'}
    proposal=dict(source_only=True,adopted=False,native=False,admitted=False,
        parent_sha256=B.sha(P/'joint/candidate.nes'),no_new_lease=True,
        proposed_own_ABI_retirement=dict(span=[0xadde,0xae46],bytes=104,names=names,source_refs=refs,actual_linked_object_import_closure=imports,
            actual36JMPtargets=targets,approval_required='Explicit retirement review before replacing these own exported old kernel gates.'),
        compiled_unlinked_ROM_glue=dict(bytes=80,native_selector=52,UI_heartbeat=28,remaining_proposed_gate_bytes=24,
            native_hook='Existing FwNativeDrawAll::Native18B farcall becomes same-span3B JMP FfMuxNativeROM +15Bpad. No extra foreign farcall.',
            UI_hook='Only own FF service29 JMP changes FwPaletteTick -> FfMuxTickROM; original body service still runs first, including fullqueue failure.'),
        RAM3=dict(actual_compiled_occupied=occupied,source_checked_unused_holes=gaps,total_unused_bytes=sum(g['bytes']for g in gaps),
            proposed_workers='Routine-boundary packing only after actual assembly sizing; largest hole BECF..<BFE0,273B. No physical layout or ready cookie is published.',
            payload='New source-built8KB stream in existing893..<901; new full payload fingerprint/cookie version7; all original code/art/publisher/CHR PCs/bytes protected.'),
        frame_protocol=dict(
            identities='Native0; Fire1=[16,26,30]; Ice/White2=[12,21,30]; Bolt3=[18,28,30]; Sword4=[0C,1C,2C]; Ink5=[0F,0F,0F].',
            native='Actual completed native-world object gets bit4 on ALL its admitted parts iff at least one visible part usesP1; whole tagged object hides only in non-native epochs.',
            owned='Logical0..<RgOamPlayerStart+actual body header, mapped through RgOamRotation. Body0 always retained. Swordrole2/inkrole3 form separate complete record groups; upperwindows5/6/7 identify source projectile slots0/12/24.',
            source_kind='Actual FfProjectileEntry mapskind1Fire,2Bolt,3Ice,4White. Validate original active/frame range; no inferred new spell types.',
            palettes='Chosen exact family uses only P1; sword/ink/FX attributes map toP1 without bitplane/coordinate/flip changes. WorldP2/P3 and bodyP0 stay intact. Clear bit4 on every marker before DMA.',
            fairness='Advance family cursor only on completed DrawAll, over families with actually visible admitted records; same-family source objects share an epoch. Source chunk/part/OAM rotation fairness remains untouched.',
            packet='Owner/cookie check precedes aliases. Pending cleared before a changed packet; whole OAM filtering+packet complete before owner/family and final80 valid publication. Active80 remains after nativequeue; retireC0 uses frozenpreflush.',
            skipped_or_paused='Genuine row29 runs before GameLoop pause branch. Heartbeat reissues the LAST committed non-native family palette even when thisMain skipsdrawing; completed lateDraw may replace it. No epochadvance withoutdraw. Must prove fullqueue/cold/paused/catchup actual callers.',
            empty='If no family remains, preserve body0, clear metadata and restore nativeP1 coherently even with fullnativequeue; no all-world hiding.',
            aliases='Only existing FF transient target/rectangle/render-phase scratch plus selectedFF SmFreezeTurn/LastBlue/Packet/Pending; no new ExRAM/ZP or source-persistent gameplay fields.'),
        required_proofs=['True shared Main with nativeworld/FFallkinds/sword/ink, RGB/priority/window/coherentwhole-object controls.',
            'Exact foreign/cold/fullcookie/malformed/lifecycle/normal-lag-IRQ/source state and ordered native writes; verify heartbeat per actualcompletedMain.',
            'Unchanged source motion/combat/pickup/source bytes; conditional dense PN/CHR/loader fingerprint complete.',
            'Measure fullcycle cost, software64 and hardware8/line/family visibility. Native/performance/campaign/readiness remain separate.'],
        tradeoffs=['Color-exact admitted epochs may flicker1/3 or1/4 under legally coexisting families; does not claim simultaneous original-frame identity.',
            'Existing FF largeBolt CPU and hardware/software sprite saturation remain unresolved blockers.'],
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)})
    B.save(O/'proposal.json',proposal);print(json.dumps(dict(path=str(O/'proposal.json'),sha256=B.sha(O/'proposal.json'),ROM_glue=80,RAM3_unused=sum(g['bytes']for g in gaps))),flush=True)

if __name__=='__main__':main()
