"""Read-only, stdout-only source factoring proposal for Z2 fairy duplicates.

No file, ROM, source input, grant or menu is changed by this checker. The
in-memory candidate aliases exact duplicate fairy pages and poisons released
pages, so real publisher/PPU reads cannot accidentally rely on their old art.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_remaining_roster_starts_1110 as C
import check_sonic_sms_native_prototype_1110 as Authority
from check_tmnt_render_oa import address, location
from check_mini_funded_actor_1108_v3 import slim_fork

R = Path(__file__).resolve().parents[2]
ROM = R/'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
TARGETS = tuple(range(321,335))
CHR = 1048592
N = C.I.N


def digest(raw):
    return sha256(raw).hexdigest()


def canonical(page):
    return 319 + (page & 1 == 0) if page in TARGETS else page


def page_bytes(raw, page):
    assert 0 <= page < 1024, page
    return raw[CHR+1024*page:CHR+1024*(page+1)]


def proposal(raw, *, poison=False):
    b = C.W.bundle(raw)
    at = location(b,'Z2PoseChrLo')
    assert at == 574138 and address(b,'Z2PoseChrLo') == 0xc2aa
    assert raw[at:at+27] == bytes(range(52,79))
    assert raw[location(b,'Z2PoseChrHi'):location(b,'Z2PoseChrHi')+27] == bytes([1])*27
    image = bytearray(raw)
    table = bytes(canonical(p)&255 for p in range(308,335))
    image[at:at+27] = table
    if poison:
        for p in TARGETS:
            image[CHR+1024*p:CHR+1024*(p+1)] = bytes([p&255])*1024
    return bytes(image),dict(file_offset=at,old_hex=raw[at:at+27].hex(),new_hex=table.hex(),
                            role='Lossless source fairy page alias; no pose/tile/palette changes')


def finite_sources(raw,b):
    prior_path = R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
    prior = json.loads(prior_path.read_text())
    assert prior['passed']
    overlap = {k:sorted(set(v)&set(TARGETS)) for k,v in prior['exact_finite_domains'].items()
               if set(v)&set(TARGETS)}
    assert overlap == {'ZeldaII body':list(TARGETS)},overlap
    # Rebind all50 current tables, four formally retired M3 arrays, exact native
    # map mirrors, special weapon readers and15 complete private writer chunks.
    current = Authority.chr_authority(raw)
    assert current['prior_domains'] == 88 and current['private_writer_chunks_exact'] == 15
    assert current['current_tables_exact'] == 50
    # New owners after that census remain explicitly excluded from these pages.
    recent = {'Mini':list(range(962,969)),'Getsu':list(range(990,993)),
              'Giant':list(range(168,215,2)),'JaySteve':list(range(216,223,2)),
              'SonicPrototype':list(range(224,231,2))}
    assert not any(set(TARGETS)&set(v) for v in recent.values())
    sites = [
        (69,0xa4cf,'e01b9002a203a9c68da17da9c68d1651bdaac28d086b'),
        (69,0xa50a,'ad086ba201a0008d6a01a9758d6c01a9a28d6d01a9be4c5a01'),
        (69,0xb3f3,'a94fa2018d6a01a9898d6c01a9a28d6d01a9be205a01'),
        (62,0xa275,'9947018a2903098099e073a9018dee738d460160')]
    compiled=[]
    for bank,pc,expected in sites:
        at=16+8192*bank+(pc&8191);blob=bytes.fromhex(expected)
        assert raw[at:at+len(blob)] == blob,(bank,hex(pc),raw[at:at+len(blob)].hex())
        compiled.append(dict(physical_PRG=bank,PC=pc,file_offset=at,bytes=blob.hex()))
    # The actual bounded table load occurs once in all current PRG; no stale
    # debug-symbol alias or second high-table API is accepted as a live reader.
    assert raw[:CHR].count(bytes.fromhex('bdaac2')) == 1
    assert raw.index(bytes.fromhex('bdaac2')) == 566511
    source=(R/'src/zelda2_link_render.s').read_text()
    assert source.count('lda Z2PoseChrLo,x') == 1
    assert 'cpx #27\n bcc :+\n ldx #3' in source
    assert 'lda SmChrBank\n ldx #.hibyte(308)\n ldy #0\n farcall X5SetPhysicalChr,jmp' in source
    world=(R/'src/zelda2_link_draw_world.s').read_text()
    assert 'lda #.lobyte(335)\n ldx #.hibyte(335)\n farcall X5SetSpecialChr' in world
    references=[]
    for p in (R/'src').glob('*'):
        if p.is_file() and p.suffix in ('.s','.inc'):
            for line,text in enumerate(p.read_text(errors='replace').splitlines(),1):
                if 'Z2PoseChrLo' in text or 'Z2PoseChrHi' in text:
                    references.append(dict(file=p.relative_to(R).as_posix(),line=line,text=text.strip()))
    assert len(references) == 3,references
    hud=raw[location(b,'InvHudPhysicalBanks'):location(b,'InvHudPhysicalBanks')+8]
    assert hud == bytes(range(236,244))
    return dict(current_authority=current,sole_domain_overlap=overlap,recent_owner_domains=recent,
                current_reader_and_publishers=compiled,source_table_references=references,
                world_page=335,HUD_pages=list(hud),publication='Exactly one1KB body window0; no adjacent implicit page.')


class FundingBus(N.Bus):
    def __init__(self,b):
        self.pattern_events=[]
        self.table_reads=[]
        super().__init__(b)

    def __getitem__(self,i):
        if isinstance(i,int) and 0xc2aa<=i<0xc2c5 and self.rawtags[2]==198:
            self.table_reads.append(i-0xc2aa)
        return super().__getitem__(i)

    def __setitem__(self,i,value):
        super().__setitem__(i,value)
        if isinstance(i,int) and 0x5120<=i<=0x512b:
            physical=self.chr_latches[i-0x5120]
            self.pattern_events.append((i,physical,digest(page_bytes(self.bundle['raw'],physical))))


def invoke(m,name,**kwargs):
    return N.invoke(m,name,**kwargs)


def normalize_state(m):
    # Only the private page selector and its actual hardware/publication byte
    # may change. All palettes, source gameplay state, OAM, VRAM and WRAM match.
    state=bytearray(m[:0x8000])
    for a in (address(m.bundle,'SmChrBank'),address(m.bundle,'CurrentCHRBank'),0x5120,
              address(m.bundle,'SafecallA_SMC')+1):
        state[a]=0
    return (bytes(state),bytes(m.ram[0]),bytes(m.ram[1]),bytes(m.ram[2]),bytes(m.ram[3]),
            tuple(m.rawtags),bytes(m.vram),m.ppu_addr,m.toggle,m.upper,
            tuple((a,h)for a,p,h in m.pattern_events))


def regular_nmi(m):
    N.put(m,NmiDisable=0,FamilyMainCommit=0)
    cpu=N.NesMPU(memory=m,pc=0x5b00);cpu.sp,cpu.p=224,0x31
    cpu.nmi()
    for _ in range(200000):
        if (cpu.pc,cpu.sp)==(0x5b00,224):break
        assert m[cpu.pc],('NMI BRK',hex(cpu.pc),m.rawtags)
        cpu.step()
    else:raise AssertionError('Full regular NMI bound')
    assert m.upper==0
    return cpu.processorCycles


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='Reservation only; this stdout audit writes nothing.')
    args=parser.parse_args()
    assert args.output.resolve()==(R/'build/sonic-fairy-funding-audit-1110').resolve()
    assert not args.output.exists()
    raw=ROM.read_bytes();assert digest(raw)==PIN
    b=C.W.bundle(raw)
    authority=finite_sources(raw,b)
    aliases=[]
    for p in TARGETS:
        assert page_bytes(raw,p)==page_bytes(raw,canonical(p))
        aliases.append(dict(page=p,canonical=canonical(p),file_offset=CHR+1024*p,SHA256=digest(page_bytes(raw,p))))
    candidate,patch=proposal(raw)
    poisoned,_=proposal(raw,poison=True)
    images=[C.W.bundle(q) for q in (raw,poisoned)]
    previous=N.Bus;N.Bus=FundingBus
    try:
        seeds=[N.fresh(q)for q in images]
    finally:N.Bus=previous
    counts=Counter();readers=set();changed_slots=set()
    print('Finite source census and14 exact duplicate page comparisons passed.',flush=True)
    for pose in range(256):
        for face in (1,2):
            pair=[]
            for seed in seeds:
                m=slim_fork(seed)
                N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=face,
                      Player_SprAttrib=0,VRAM_Buffer1_Offset=0,NmiDisable=255,FamilyMainCommit=1)
                a=invoke(m,'Z2SetPose',x=pose)
                expected=pose if pose<27 else 3
                assert m.table_reads==[expected],(pose,face,m.table_reads)
                readers.update(m.table_reads)
                z=invoke(m,'Z2PublishBody')
                regular_nmi(m)
                assert all(p not in TARGETS for _,p,_ in m.pattern_events) or seed is seeds[0]
                pair.append((m,a,z))
            old,new=pair
            assert old[1:]==new[1:],('API registers/cycles',pose,face,old[1:],new[1:])
            sa=address(b,'SafecallA_SMC')+1
            if old[0][sa]!=new[0][sa]:
                assert old[0][sa]+256 in TARGETS and new[0][sa]==(canonical(old[0][sa]+256)&255)
            assert normalize_state(old[0])==normalize_state(new[0]),('State/pixels',pose,face,
                [(hex(i),old[0][i],new[0][i])for i in range(0x8000)if old[0][i]!=new[0][i]][:25],
                [i for i,(a,z) in enumerate(zip(normalize_state(old[0]),normalize_state(new[0])))if a!=z])
            changed_slots.update(a for (a,p,h),(a2,p2,h2) in zip(old[0].pattern_events,new[0].pattern_events)
                                 if p!=p2)
            counts['bounded_pose_and_regular_NMI']+=1
    assert readers==set(range(27)) and changed_slots=={0x5120}
    print('All256 pose inputs/both facings and512 real regular NMI publications passed.',flush=True)
    # Genuine full pose selector, world/HUD draw and intermediate lives owner.
    for pose in range(27):
        for face in (1,2):
            for scene in ('menu','lives','gameplay'):
                pair=[]
                for seed in seeds:
                    m=slim_fork(seed)
                    N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=face,
                          OperMode=0 if scene=='menu' else 1,GameEngineSubroutine=8,
                          Z2CachedPose=pose if pose<11 else 3,
                          Z2ActiveSpells=1 if pose<11 else 9,
                          FrameCounter=0 if pose<11 else (pose-11)*4,
                          Player_SprAttrib=0,VRAM_Buffer1_Offset=0,NmiDisable=255,
                          FamilyMainCommit=1,MmDeathFlag=0,CurrentOAMOffset=0,
                          Player_Rel_XPos=96,Player_Rel_YPos=176,Player_Y_HighPos=1)
                    if scene=='menu':
                        invoke(m,'Z2PortraitGate')
                    elif scene=='lives':
                        invoke(m,'DrawPlayer_Intermediate')
                    else:
                        invoke(m,'Z2GraphicsGate')
                        invoke(m,'Z2DrawShots')
                    regular_nmi(m)
                    pair.append(m)
                assert normalize_state(pair[0])==normalize_state(pair[1]),('Full scene',pose,face,scene)
                counts['full_'+scene]+=1
    print('Full Z2 menu/lives/gameplay+world/HUD scene pairs passed.',flush=True)
    # Complete current frontend names/admission for every present profile.
    inventories=[C.inventory(q)for q in (raw,poisoned)]
    assert inventories[0]==inventories[1]
    assert inventories[0]['distinct_named_entries']==100
    counts['complete_menu_entries']=100
    # Poisoning without the table rewrite must be detected for a freed form.
    broken=bytearray(poisoned);at=patch['file_offset']
    broken[at:at+27]=bytes.fromhex(patch['old_hex'])
    n=C.W.bundle(bytes(broken));previous=N.Bus;N.Bus=FundingBus
    try:m=N.fresh(n)
    finally:N.Bus=previous
    N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=1,NmiDisable=255,FamilyMainCommit=1)
    invoke(m,'Z2SetPose',x=13);invoke(m,'Z2PublishBody');regular_nmi(m)
    assert any(p==321 and h!=digest(page_bytes(raw,321))for _,p,h in m.pattern_events)
    report=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,files_written=0,
                parent_SHA256=PIN,memory_only_table_candidate_SHA256=digest(candidate),
                table_patch=patch,released_bytes=14*1024,proposed_released_pages=aliases,
                counts=dict(counts),all27_table_indices_seen=True,only_hardware_slot_changed=0,
                wrong_unaliased_poison_negative_detected=True,source_authority=authority,
                scope='Exact table data alias and poisoned-page differential actual CPU publishers/'
                      'full regular NMI/menu/lives/world/HUD paths. Every original CHR byte rendered '
                      'by the admitted source forms remains identical;14 existing duplicate pages '
                      'can become new storage only after root grants this semantic source change.',
                limitations=['No native Mesen or timing/display qualification.',
                             'No Sonic gameplay, loader, RAM lifecycle or menu admission.',
                             'No claim for malformed arbitrary mapper values outside named finite source domains.'],
                bindings={str(p.relative_to(R)):digest(p.read_bytes())for p in
                          [Path(__file__),ROM,R/'src/zelda2_link_render.s',R/'src/zelda2_link_art.inc',
                           R/'src/zelda2_link_draw_world.s',R/'src/mmc5_expanded.s',
                           R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json']})
    print(json.dumps(report,separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
