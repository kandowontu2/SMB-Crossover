"""Replace the overflowing DK platform refresh save with the live operands."""
from collections import Counter
from itertools import product
from pathlib import Path
import json
import subprocess

import check_dkjr_platform_carry_1110_v1 as C

R, V, I, N = C.R, C.V, C.I, C.N
OUT = R.R / 'build/dkjr-platform-refresh-1110'
SOURCE = R.R / 'tools/reference/dkjr_platform_refresh_1110_v1.s'
NEGATIVE = C.OUT / 'carry-proof.json'
PAGES = [817,833,847,856,867,881,882,883,959,960,961]
SMC = [0x62, 0x6a, 0x6c, 0x6d, 0x79]


def link():
    OUT.mkdir(exist_ok=True)
    cfg = OUT / 'refresh.cfg'
    cfg.write_text('MEMORY{A:start=$B624,size=$81,file=%O;B:start=$B7AC,size=$1E,file=%O;}'
                   'SEGMENTS{REFRESH:load=A,type=ro;ALIASES:load=B,type=ro;}\n')
    cc = R.R / 'tools/Windows/cc65/bin'
    outputs = []
    for name in ['old','new']:
        obj, data = (OUT / (name + ext) for ext in ['.o', '.bin'])
        command = [cc/'ca65.exe', SOURCE, '-o', obj]
        if name == 'old':
            command.extend(['-D','ORIGINAL'])
        subprocess.run(command,check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data],check=True)
        obj.unlink()
        blob = data.read_bytes()
        assert len(blob) == 159
        outputs.append((blob[:129],blob[129:]))
    return outputs


def staged():
    base = C.BASE.read_bytes()
    negative = json.loads(NEGATIVE.read_text())
    assert not negative['passed'] and I.sha(base) == negative['base_SHA256']
    assert "write to actual ROM" in negative['active_platform']['terminal'] and '0175' in negative['active_platform']['terminal']
    before = R.OAM.compose(base, negative['patches'])
    assert I.sha(before) == negative['memory_only_SHA256']
    at = lambda page: V.CHR + page*1024
    payload = b''.join(before[at(page):at(page)+1024] for page in PAGES)
    left, right = link()
    after = bytearray(payload)
    for start, old, new in [(0xb624-0xa000,left[0],right[0]), (0xb7ac-0xa000,left[1],right[1]),
                            (0xbbb8-0xa000,bytes.fromhex('20acb720bbb7'),bytes.fromhex('20e98a20a08a')),
                            (9*1024+0x2f7,b'\xff'*5,bytes(SMC))]:
        assert payload[start:start+len(old)] == old
        after[start:start+len(old)] = new
    assert payload[:8160].count(bytes.fromhex('20acb7')) == 2 and payload[:8160].count(bytes.fromhex('20bbb7')) == 2
    patches = list(negative['patches'][:-1])
    for i,page in enumerate(PAGES):
        old, new = payload[i*1024:(i+1)*1024], after[i*1024:(i+1)*1024]
        if old != new:
            assert page in [881,882,960]
            patches.append(dict(physical_CHR=page,file_offset=at(page),old_hex=old.hex(),new_hex=new.hex()))
    old_cookie = bytes.fromhex(negative['patches'][-1]['old_hex'])
    new_cookie = old_cookie[:3] + bytes.fromhex(I.sha(after))[:13]
    patches.append(dict(physical_PRG=65,file_offset=534485,old_hex=old_cookie.hex(),new_hex=new_cookie.hex()))
    return base, before, R.OAM.compose(base, patches), payload, bytes(after), old_cookie, new_cookie, patches


def fixed_graph(seed):
    # Follow the exact fixed native code. Data operands may read only native
    # RAM or the same permanently mapped low page, never the A/C windows.
    widths = {'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,
              'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
    todo = [0x8ae9,0x8aa0]
    visited = set()
    while todo:
        pc = todo.pop()
        if pc in visited:
            continue
        assert 0x8000 <= pc < 0xa000, hex(pc)
        visited.add(pc)
        name, mode = N.NesMPU.disassemble[seed[pc]]
        assert name not in ['???','RTI','BRK'] and mode not in ['ind','inx','iny'], (hex(pc),name,mode)
        end = pc + widths[mode]
        if mode in ['abs','abx','aby']:
            addr = seed[pc+1] + 256*seed[pc+2]
            assert addr+(255 if mode in ['abx','aby'] else 0)<0xa000, (hex(pc),hex(addr))
        if name in ['JMP','JSR']:
            todo.append(addr)
        if mode == 'rel':
            offs = seed[pc+1]
            todo.append(end+offs-(256 if offs&128 else 0))
        if name not in ['JMP','RTS']:
            todo.append(end)
    return len(visited)


def standalone(seeds):
    cases = 0
    for ident, top, camera, p in product(range(0x24,0x2d), [144,192,208], [0,255,256], [0x21,0x65]):
        states = []
        for index, seed in enumerate(seeds):
            m = V.slim_fork(seed)
            C.setup(m,40,0,8,top,ident)
            N.put(m, ScreenLeft_X_Pos=camera&255, ScreenLeft_PageLoc=camera>>8)
            m.ram[2][0x8fe] = 2
            c = N.NesMPU(memory=m,pc=0xb624)
            c.a,c.x,c.y,c.p,c.sp = 83,7,91,p,246
            c.stPushWord(0x5aff)
            initial = bytes(m[0x15a:0x17b])
            m.writes.clear()

            def check(z):
                if index == 0 and z.pc == 0xb686 and z.memory.rawtags[1] == 3:
                    changed = {i for i,_ in m.writes if 0x15a<=i<0x17b}
                    assert changed.issubset({0x100+s for s in SMC}), changed

            V.run(c,lambda z:z.pc==0x5b00,check)
            assert initial == bytes(m[0x15a:0x17b])
            states.append((V.registers(c,0xef), C.memory(m)[:5], bytes(m.ram[2][:0x900])))
        assert states[0] == states[1], (ident,top,camera,p)
        cases += 1
    return cases


def replay_platform(seed):
    m = V.slim_fork(seed)
    C.setup(m,40,0,8,208)
    N.invoke(m,'InitEnemyObject',x=C.SLOT)
    assert (N.get(m,'Enemy_ID',C.SLOT),N.get(m,'Enemy_Flag',C.SLOT)) == (0x25,1)
    cpu = N.NesMPU
    counts = Counter()
    minimum = 255
    transitions = []

    class Trace(cpu):
        def step(self):
            nonlocal minimum
            minimum = min(minimum,self.sp)
            pc = self.pc
            tag = m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            if (tag,pc) in [(199,0xac29),(193,0xb029),(3,0xb6a5)]:
                counts[f'{tag}:{pc:04x}'] += 1
                if (tag,pc) == (199,0xac29):
                    top = N.get(m,'Enemy_Y_Position',self.x)
                    source = m.ram[2]
                    record = (self.x,top,N.get(m,'Player_Y_Position'),source[0x210],source[0x6b])
                    if not transitions or transitions[-1] != record:
                        transitions.append(record)
            return super().step()

    N.NesMPU = Trace
    try:
        for age in range(1,49):
            N.put(m,FrameCounter=age,SavedJoypadBits=0,SavedJoypad1Bits=0,
                  VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
            N.invoke(m,'GameCoreRoutine',x=0,y=0)
            I.C.clear(m)
    finally:
        N.NesMPU = cpu
    admitted = [row for row in transitions if row[1]-32 == row[2] and row[1]-17 == row[3] and row[4]==1]
    return dict(real_carry_calls=counts['3:b6a5'],calls=dict(counts),native_updates=48,
                admitted_height_count=len(admitted), transitions=transitions[:32],
                lives=N.get(m,'NumberofLives')), minimum


def main():
    parent, unsafe, after, old, new, parent_cookie, cookie, patches = staged()
    seeds = [V.make_seed(rom,payload) for rom,payload in [(unsafe,old),(after,new)]]
    low = fixed_graph(seeds[1])
    equal = standalone(seeds)
    old_core, new_core = C.cold(parent,parent_cookie), C.cold(after,cookie)
    exact = C.genuine_event(old_core,new_core)
    try:
        active, min_sp = replay_platform(new_core)
    except AssertionError as error:
        active = dict(real_carry_calls=0,terminal=str(error))
        min_sp = None
    good = active['real_carry_calls']>0 and active['admitted_height_count']>0 and min_sp>0x7a
    result = dict(passed=good,ROM_written=False,platform_placement_added=False,
                  base_SHA256=I.sha(parent),memory_only_SHA256=I.sha(after),patches=patches,cookie=cookie.hex(),
                  fixed_native_instruction_closure=low,standalone_native_platform_cases=equal,
                  actual_position_cases=exact,active_platform=active,minimum_foreground_SP=min_sp,
                  vectors_pending=True,stack_bytes_removed=28,
                  bindings={p.relative_to(R.R).as_posix():I.sha(p.read_bytes()) for p in
                            [Path(__file__),SOURCE,C.SOURCE,C.BASE,NEGATIVE]},
                  scope='Actual linked low natives and two-header carry transport. Native platform actor initialized in a CPU fixture; no authored stage placement.')
    (OUT/'refresh-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print('DK Jr platform refresh',good,result['memory_only_SHA256'],low,equal,active,'minSP',result['minimum_foreground_SP'],flush=True)


if __name__=='__main__':
    main()
