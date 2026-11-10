"""Isolated 9897 Jay scene/cold/hot call chain with current CPU vectors."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_jay_silius_private_motion_1110 as Motion
import check_ff_head_lifetime_irq_1110 as Vector
import check_getsu_fuma_owner_1110 as Common
import check_getsu_owner_vectors_1110 as ColdVector
import check_roster_powerup_continuation_1110 as Game
import check_sonic_fairy_funding_1110 as Fairy

H, W, N, Jay, Donor = Motion.Host, Motion.W, Motion.N, Motion.Jay, Motion.Donor
SOURCE = H.ROOT / 'tools/reference/jay_silius_scene_lifecycle_1110.s'
ROM_PIN = Motion.NEXT
LINK_PIN = 'c79bc2e16d67ee256fb1f44089eb429950906884b846522a40b73842d9ed31a1'
LAYOUT = {'COLD':(0x4800,256), 'HOT':(0x4a00,512), 'DESCRIPTOR':(0x4d00,7)}
RETURN_RTS = 0x4d10
CHR, PAGES, STOP = 1048592, (331,332), 0x5b00


def digest(data):
    return sha256(data).hexdigest()


def offset(bank, pc):
    return 16 + bank*8192 + (pc & 8191)


def actual_donor():
    raw = Donor.DONOR.read_bytes()
    assert digest(raw) == Donor.PIN
    cpu, _ = Motion.Motion.opening(raw)
    found = []

    def observe():
        if cpu.memory.code_key(cpu.pc) == (6,0x8093):
            found.append(Donor.fork(cpu))
        cpu.step()

    Donor.frame(cpu,cpu.memory,0,observe)
    actor, = found
    return actor


def proposal(raw, donor):
    assert digest(raw) == ROM_PIN
    base = W.Symbols.bundle()
    base['raw'] = raw
    H.Terrain.source_bindings(raw,base)
    H.carrier(raw)
    linked = Jay.build()
    kernel = linked['images']['PRIVATE']
    assert digest(kernel) == LINK_PIN and len(kernel) == 1925
    kernel = kernel.ljust(2048,b'\xea')
    descriptor = bytes.fromhex('0202014b014c01')
    cookie = bytes((0xa7,16,32,1)) + sha256(kernel+descriptor).digest()[:12]
    fields = linked['ram']
    aliases = {alias:fields[logical] for alias,logical in dict(PadNow=0x162,PadPrevious=0x163,
        XLo=0x11,XHi=0x10,YLo=0x13,YHi=0x12,DonorVY=0x15,DonorFlags=0x19).items()}
    aliases.update({a:linked['symbols'][s] for a,s in dict(OriginalInput='JayOriginalInput',
        PositionSetup='JayPositionSetup',Integrate='JayIntegrate').items()})
    aliases['Descriptor'] = LAYOUT['DESCRIPTOR'][0]
    names = ('OperMode','OperMode_Task','GameEngineSubroutine','GamePauseStatus','NmiDisable',
             'FamilyMainCommit','SwimmingFlag','WorldNumber','LevelNumber','ScreenLeft_PageLoc',
             'ScreenLeft_X_Pos','Player_PageLoc','SavedJoypadBits','FrameCounter','Player_X_Position',
             'Player_Y_Position','Player_Pos_ForScroll','Player_X_Scroll','Player_Y_Speed','Player_State')
    aliases.update({name:W.address(base,name) for name in names})
    aliases['MikeMovement'] = W.address(base,'JnMovement')
    ordered = {address:logical for logical,address in fields.items() if address < 0xc0f0}
    assert sorted(ordered) == list(range(0xc000,0xc033))
    template = bytes(donor.memory.ram[ordered[address]] for address in sorted(ordered))
    constants = ''.join(f'{key} = ${value:04x}\n' for key,value in aliases.items())
    text = SOURCE.read_text().replace('CookieBytes',','.join(map(str,cookie)))
    text = text.replace('TemplateBytes',','.join(map(str,template)))
    program = HostAssemble(constants+text, LAYOUT)
    assert program['images']['DESCRIPTOR'] == descriptor
    new = bytearray(raw)
    redirects = []
    for bank,pc,old,label in ((65,0xac2c,'2026b0','JaySceneOrRetire'),
                             (65,0xaf00,'ad0260','JaySelect'),
                             (65,0xae85,'2072ab','JayCopyOrLegacy'),
                             (96,0xa53d,'4ccba2','JayHot')):
        at = offset(bank,pc)
        assert new[at:at+3] == bytes.fromhex(old)
        target = program['symbols'][label]
        opcode = 0x20 if old.startswith('20') else 0x4c
        new[at:at+3] = bytes((opcode,)) + target.to_bytes(2,'little')
        redirects.append((bank,hex(pc),old,new[at:at+3].hex()))
    for i,page in enumerate(PAGES):
        start = CHR+1024*page
        new[start:start+1024] = kernel[1024*i:1024*(i+1)]
    return base,dict(base,raw=bytes(new)),program,linked,kernel,cookie,redirects


HostAssemble = H.assemble


def stage_fixture(m, program):
    # Isolated test transport for the ungranted resident and descriptor
    # origins. Real product PRG bytes are never inferred free at these PCs.
    for name,code in program['images'].items():
        at = LAYOUT[name][0]
        list.__setitem__(m,slice(at,at+len(code)),code)
    list.__setitem__(m,RETURN_RTS,0x60)


def menu(bundle, cycle, program=None):
    with patch.object(N,'Bus',W.ControllerBus):
        m = W.UI.seed(bundle,15)
    if program is not None:
        stage_fixture(m,program)
    for _ in range(cycle):
        W.UI.key(m,32)
    assert W.UI.menu_name(m)[0] == H.FAMILIES[cycle] and m[0x730b] & 0x60 == cycle << 5
    start = W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    return m


def native_cold(m, program, *, vectors=False):
    c = ColdVector.entry(m)
    cuts, seen = Counter(), set()
    while (c.pc,c.sp) != (STOP,224):
        tag = m.rawtags[1]
        if vectors:
            test = 0x4800 <= c.pc < 0x4900 or tag == 193 and 0xae00 <= c.pc < 0xafa0
            test |= tag == 251 and (0xaf40 <= c.pc < 0xafa0 or 0xb9d6 <= c.pc < 0xba00)
            key = (tag,c.pc,c.sp,c.p&4,m[5],m.ram[2][0x1fe0],m.ram[3][0x1fe0])
            if test and key not in seen:
                seen.add(key)
                for kind in ('FF',) if c.p&4 else ('FF','IRQ'):
                    q,d = Vector.clone(m,c)
                    ColdVector.interrupt(d,kind)
                    cuts[kind] += 1
        ColdVector.step(c)
        assert c.processorCycles < 12_000_000, ('actual common cold bound',hex(c.pc))
    return c,dict(cuts)


def cold_cases(trial, program, kernel, cookie):
    def fixture():
        m = Common.blank(trial)
        stage_fixture(m,program)
        Common.scene(m,16)
        m[0x730b] = 32
        return m

    m = fixture()
    before = m.ppu_reads
    c,cuts = native_cold(m,program,vectors=True)
    assert c.p&1 and Common.headers(m) == (cookie,)*2
    assert bytes(m.ram[3][:2048]) == kernel and not any(m.ram[2][:256])
    count = m.ppu_reads-before
    assert count == 4100 and cuts['FF'] and cuts['IRQ'], (count,cuts)
    prior = tuple(map(bytes,m.ram))
    before = m.ppu_reads
    assert native_cold(m,program)[0].p&1 and m.ppu_reads == before and tuple(map(bytes,m.ram)) == prior
    q = Vector.clone(m)
    q.ram[2][0x33] = 1
    Common.invoke(q,program['symbols']['JaySceneOrRetire'])
    assert not q.ram[2][0x33] and q.ppu_reads == before and tuple(map(bytes,q.ram)) == prior
    for bank in (2,3):
        for byte in range(16):
            q = Vector.clone(m)
            q.ram[bank][0x1fe0+byte] ^= 1
            before = q.ppu_reads
            assert native_cold(q,program)[0].p&1
            assert q.ppu_reads-before == count and Common.headers(q) == (cookie,)*2
    for updates in (dict(SelectedCharacter=0),dict(OperMode=0),dict(FamilyMainCommit=0),
                    dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)):
        q = fixture(); N.put(q,**updates)
        before = tuple(map(bytes,q.ram)),q.ppu_reads
        assert not native_cold(q,program)[0].p&1
        assert before == (tuple(map(bytes,q.ram)),q.ppu_reads)
    for variant in (0,64,96):
        q = fixture(); q[0x730b] = variant
        assert not native_cold(q,program)[0].p&1 and q.ppu_reads == 0
    for fault in ((2,1),(3,1),(3,0x400)):
        q = fixture(); q.corrupt_at = fault
        assert not native_cold(q,program)[0].p&1 and all(not head[0] for head in Common.headers(q)), fault
    return dict(actual_PPU_reads=count,warm_reads=0,header_reload_faults=32,
                scene_warm_resets_ready=True,foreign_context_rejections=9,
                copy_readback_failures=3,vectors=cuts)


def bridge(m,c,donor,linked):
    state = linked['ram']
    external = Donor.fork(donor)
    external.pc = 0x81d2
    external.a,external.x,external.y,external.p,external.sp = Motion.regs(c)
    for logical,physical in state.items():
        external.memory.ram[logical] = m[physical]
    before = bytes(external.memory.ram)
    external.stPushWord(0x60ff)
    Motion.run(external,(0x6100,c.sp))
    assert all(before[i] == value for i,value in enumerate(external.memory.ram)
               if i not in state and not 0x100 <= i <= 0x1ff)
    for logical,physical in state.items():
        value = external.memory.ram[logical]
        if m[physical] != value:
            m[physical] = value
    c.a,c.x,c.y,c.p,_ = Motion.regs(external)
    c.pc = RETURN_RTS


def ready(m,program,donor,linked,cycle,pads,*,vectors=False):
    s = program['symbols'] if program else {}
    reports, counts, cuts = [],Counter(),Counter()
    samples = set()
    snapshots = []
    epoch_seed = None
    hot_instructions = {op['pc'] for op in program['instructions'] if op['segment'] == 'HOT'} if program else set()
    cold_epoch = None
    for logical in range(700):
        active = tuple(N.get(m,name) for name in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8)
        if active and len(reports) >= len(pads):
            break
        m.controller_pad = pads[len(reports)] if active else 0

        def observe(memory,cpu):
            nonlocal cold_epoch,epoch_seed
            if program is None:
                return
            if cpu.pc == s['JaySceneOrRetire'] and cycle == 1:
                assert N.get(memory,'DisableScreenFlag') and N.get(memory,'NmiDisable') == 255
                assert N.get(memory,'Player_Y_HighPos') == 0 and N.get(memory,'Player_Y_Position') == 0
                cold_epoch = logical
            if cpu.pc == 0xb000 and memory.rawtags[1] == 3:
                bridge(memory,cpu,donor,linked)
                counts['real_donor_weapon_import'] += 1
            if cpu.pc == s['PublishPosition']:
                assert memory.rawtags[2] == 2 and memory.rawtags[1] == 224
                counts['private_motion'] += 1
                snapshots.append((memory[linked['ram'][0x10]]*256+memory[linked['ram'][0x11]],
                                  memory[linked['ram'][0x12]]*256+memory[linked['ram'][0x13]]))
                if len(reports) == len(pads)-1:
                    epoch_seed = Vector.clone(memory)
            if cpu.pc in hot_instructions or memory.rawtags[1] == 3 and 0xa000 <= cpu.pc < 0xa785:
                key = cpu.pc,memory.rawtags[1],memory.rawtags[2],cpu.p&4
                if vectors and active and cycle == 1 and key not in samples:
                    samples.add(key)
                    for kind in ('NMI','IRQ'):
                        q,d = Vector.clone(memory,cpu)
                        maps = tuple(q.rawtags)
                        before = (tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),
                                  bytes(q[0x101+cpu.sp:0x200]))
                        Vector.isr(q,d,kind)
                        assert before == (tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),
                                          bytes(q[0x101+cpu.sp:0x200]))
                        if maps != tuple(q.rawtags):
                            instruction = bytes(q[cpu.pc:cpu.pc+3])
                            assert instruction in (bytes.fromhex('8d1551'),bytes.fromhex('8d1651'),bytes.fromhex('8e1651'))
                            slot = 1 if instruction[1] == 0x15 else 2
                            assert q.rawtags[slot] == q[0x145 if slot == 1 else 0x7da1]
                            assert all(maps[i] == q.rawtags[i] for i in range(4) if i != slot)
                            cuts['mapper_split'] += 1
                        cuts[kind] += 1

        Game.frame(m,observe)
        if active:
            reports.append(tuple(N.get(m,name) for name in ('Player_X_Position','Player_Y_Position','NumberofLives')))
    assert len(reports) == len(pads), (cycle,len(reports))
    return dict(reports=reports,counts=dict(counts),cuts=dict(cuts),snapshots=snapshots,
                cold_epoch=cold_epoch,epoch_seed=epoch_seed)


def family_parity(base,trial,program,linked,donor):
    result = {}
    for cycle in (0,2):
        a,b = menu(base,cycle),menu(trial,cycle,program)
        pads = [0]*5+[1]*30+[129]*12+[1]*8+[65]*5
        before = ready(a,None,donor,linked,cycle,pads)
        after = ready(b,program,donor,linked,cycle,pads)
        assert before == after and not after['counts']
        exclude = (range(0x100,0x200),range(0x4800,0x4d11))
        assert all(a[i] == b[i] for i in range(0x8000) if all(i not in r for r in exclude))
        assert (a.ram,a.vram,a.chr_latches,a.rawtags,a.ppu_reads) == (b.ram,b.vram,b.chr_latches,b.rawtags,b.ppu_reads)
        result[H.FAMILIES[cycle]] = dict(logical_updates=len(pads),terminal=after['reports'][-1])
    return result


def direct_hot(m, program):
    m.raw_page(1,224)
    N.put(m,CurrentBank=224,NmiDisable=255)
    c = N.NesMPU(memory=m,pc=program['symbols']['JayHot'])
    c.a,c.x,c.y,c.p,c.sp = 16,0,0,0x31,224
    c.stPushWord(STOP-1)
    points = Counter()

    def observe(cpu):
        if cpu.pc >= 0x8000 and m.rawtags[1] == 3 and 0xa000 <= cpu.pc < 0xc000:
            raise AssertionError(('unauthorized private execution',hex(cpu.pc)))
        if cpu.pc == W.address(m.bundle,'JnMovement'):
            points['legacy'] += 1
        return False

    Motion.run(c,(STOP,224),hook=observe)
    return points['legacy']


def hot_rejections(seed,program):
    assert seed is not None and N.get(seed,'FamilyMainCommit') & 1
    m = Vector.clone(seed)
    prior = tuple(map(bytes,m.ram))
    before = {name:N.get(m,name) for name in ('OperMode','OperMode_Task','GameEngineSubroutine',
        'GamePauseStatus','FamilyMainCommit','SwimmingFlag','WorldNumber','LevelNumber',
        'ScreenLeft_PageLoc','ScreenLeft_X_Pos','Player_PageLoc','SavedJoypadBits','FrameCounter')}
    legacy = direct_hot(m,program)
    assert legacy == 0 and tuple(map(bytes,m.ram)) == prior, (before,legacy,prior[2][0x33:0x35].hex())
    for bank in (2,3):
        for byte in range(16):
            m = Vector.clone(seed)
            m.ram[bank][0x1fe0+byte] ^= 1
            prior = tuple(map(bytes,m.ram))
            assert direct_hot(m,program) == 1 and tuple(map(bytes,m.ram)) == prior
    for updates in (dict(GamePauseStatus=1),dict(GameEngineSubroutine=7),dict(ScreenLeft_X_Pos=1),
                    dict(SavedJoypadBits=64),dict(FamilyMainCommit=0)):
        m = Vector.clone(seed)
        N.put(m,**updates)
        prior = tuple(map(bytes,m.ram))
        assert direct_hot(m,program) == 1 and tuple(map(bytes,m.ram)) == prior
    return dict(duplicate_epoch_stays_private=True,all32_header_faults_take_old_motor=True,context_fallbacks=5)


class CarrierBus(W.ControllerBus):
    pages = None

    def __getitem__(self,address):
        if address == 0x2007 and self.pages is not None and self.ppu_addr < 0x2000:
            slot = self.ppu_addr >> 10
            slot = 8 + slot % 4 if self.lastset else slot
            self.pages.add(self.chr_latches[slot])
        return super().__getitem__(address)


def carrier_cases(base,trial,program,cookie,kernel):
    with patch.object(Fairy.N,'Bus',Fairy.FundingBus):
        seeds = [Fairy.N.fresh(q) for q in (base,trial)]
    for pose in range(256):
        for face in (1,2):
            pair = []
            for seed in seeds:
                m = Fairy.slim_fork(seed)
                Fairy.N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=face,
                            Player_SprAttrib=0,VRAM_Buffer1_Offset=0,NmiDisable=255,FamilyMainCommit=1)
                a = Fairy.invoke(m,'Z2SetPose',x=pose)
                assert m.table_reads == [pose if pose < 27 else 3]
                b = Fairy.invoke(m,'Z2PublishBody')
                Fairy.regular_nmi(m)
                assert not set(PAGES).intersection(p for _,p,_ in m.pattern_events)
                pair.append((Fairy.normalize_state(m),a,b))
            assert pair[0] == pair[1], (pose,face)
    bad = bytearray(trial['raw'])
    bad[574138+23] = 331 & 255
    with patch.object(Fairy.N,'Bus',Fairy.FundingBus):
        m = Fairy.N.fresh(dict(trial,raw=bytes(bad)))
    Fairy.N.put(m,SelectedCharacter=5,Z2Variant=1,PlayerFacingDir=1,NmiDisable=255,FamilyMainCommit=1)
    Fairy.invoke(m,'Z2SetPose',x=23)
    Fairy.invoke(m,'Z2PublishBody')
    Fairy.regular_nmi(m)
    assert any(page == 331 for _,page,_ in m.pattern_events)
    pages = {}
    transitions = []
    for owner in range(37,44):
        before,after = Common.blank(base),Common.blank(trial)
        stage_fixture(after,program)
        receipts = []
        for m in (before,after):
            Common.scene(m,owner)
            m.__class__ = CarrierBus
            m.pages = set()
            c,_ = native_cold(m,program)
            assert not set(PAGES).intersection(m.pages)
            receipts.append((Motion.regs(c),m.ram,m.ppu_reads,m.pages,m.rawtags,m.chr_latches,m.ppu_log))
        assert receipts[0] == receipts[1], owner
        pages[owner] = sorted(after.pages)
        original_headers = Common.headers(after)
        if owner in (37,39,43):
            Common.scene(after,16)
            after[0x730b] = 32
            c,_ = native_cold(after,program)
            assert c.p&1 and Common.headers(after) == (cookie,)*2
            assert bytes(after.ram[3][:2048]) == kernel and not any(after.ram[2][:256])
            Common.scene(after,owner)
            c,_ = native_cold(after,program)
            assert c.p&1 and Common.headers(after) == original_headers
            transitions.append(owner)
    return dict(current_aliased_Zelda_pose_and_NMI_pairs=512,alias_removal_detected=True,
                existing_cold_owner_read_pages=pages,bidirectional_Jay_owner_transitions=transitions)


def main():
    donor = actual_donor()
    base,trial,program,linked,kernel,cookie,redirects = proposal(H.ROM.read_bytes(),donor)
    print('Jay isolated source sizes',program['used'],flush=True)
    cold = cold_cases(trial,program,kernel,cookie)
    print('Jay current compact worker',cold,flush=True)
    legacy = family_parity(base,trial,program,linked,donor)
    m = menu(trial,1,program)
    hot = ready(m,program,donor,linked,1,[0]*8+[1]*28+[128]*14+[0]*36,vectors=True)
    assert hot['cold_epoch'] == 1 and hot['counts']['private_motion'] == 86
    assert hot['counts']['real_donor_weapon_import'] == 86 and min(y for _,y in hot['snapshots']) == 3072-840
    assert hot['reports'][-1][-1] == 2 and hot['snapshots'][-1][1] == 3072
    assert Common.headers(m) == (cookie,)*2 and bytes(m.ram[3][:2048]) == kernel
    negatives = hot_rejections(hot['epoch_seed'],program)
    print('Jay actual main',hot['counts'],hot['cuts'],negatives,flush=True)
    carrier = carrier_cases(base,trial,program,cookie,kernel)
    print(json.dumps(dict(passed=True,ROM_SHA256=ROM_PIN,ROM_written=False,build_files=0,Mesen=False,
        image_SHA256=digest(trial['raw']),source_SHA256=digest(SOURCE.read_bytes()),
        ungranted_resident_fixture=program['used'],redirects=redirects,typed_header=cookie.hex(),
        cold=cold,legacy=legacy,carrier=carrier,hot_negatives=negatives,
        actual_native_hot=dict(updates=86,terminal=hot['reports'][-1],
          terminal_donor_16ths=hot['snapshots'][-1],original_held_apex_16ths=840,
          authentic_weapon_imports=86,cuts=hot['cuts'],cold_epoch=hot['cold_epoch']),
        RAM_and_CHR_allocation_granted=False),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
