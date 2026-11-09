"""Measure a stateless exact DK header compare. Scratch placement only."""
from pathlib import Path
import json
import subprocess

import check_dkjr_oam_current_vectors_1109_v4 as C

P, I, R, OUT = C.P, C.P.I, C.P.R, C.OUT
N = I.N
FIXTURE_PC = 0x5b80
ACTUAL_COMPARE = 0xaf27
ACTUAL_HOT_JSR = 0xaef6


def build(cookie):
    stem = OUT/'dk-cookie-fixture'
    src, cfg, obj, data = (stem.with_suffix(x) for x in ['.s','.cfg','.o','.bin'])
    source = f'''.setcpu "6502"
.segment "CHECK"
CurrentBankC=$7da1
SelectedCharacter=$6002
 lda SelectedCharacter
 cmp #40
 beq Own
 jmp ${ACTUAL_COMPARE:04x}
Own:
 lda CurrentBankC
 pha
 ldx #3
Bank:
 stx CurrentBankC
 stx $5116
'''
    for i in range(15,-1,-1):
        source += f' lda ${0xdfe0+i:04x}\n cmp #${cookie[i]:02x}\n bne Reject\n'
    source += ''' dex
 cpx #1
 bne Bank
 ldy #255
 bcs Restore
Reject:
 clc
Restore:
 pla
 sta CurrentBankC
 sta $5116
 rts
'''
    src.write_text(source)
    cfg.write_text(f'MEMORY{{P:start=${FIXTURE_PC:04x},size=$100,file=%O;}}SEGMENTS{{CHECK:load=P,type=ro;}}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',src,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data],check=True)
    obj.unlink()
    return data.read_bytes(), src


def measure_main(raw, cookie, code):
    costs = []
    n, invoke = 0, N.invoke
    controller = I.C.C.C.C.V
    original_bus = controller.ControllerBus

    class FixtureBus(original_bus):
        def __init__(self, bundle):
            super().__init__(bundle)
            self[FIXTURE_PC:FIXTURE_PC+len(code)] = code

    def record(memory, name, *args, **kwargs):
        nonlocal n
        if name == 'GameCoreRoutine':
            n += 1
        begin = len(memory.writes)
        z = invoke(memory, name, *args, **kwargs)
        if name == 'GameCoreRoutine' and 2 <= n <= 13:
            maps = tuple(value for at,value in memory.writes[begin:] if at in [0x5115,0x5116])
            state = (bytes(memory[:256]), bytes(memory[0x200:0x800]), bytes(memory[0x6000:0x8000]),
                     bytes(memory[0x15a:0x17b]), tuple(memory.rawtags), tuple(map(bytes,memory.ram)), maps,
                     tuple(z[k] for k in ('A','X','Y','P')))
            costs.append((z['CPU'],state))
        return z

    N.invoke = record
    if code:
        controller.ControllerBus = FixtureBus
    try:
        I.cpu(raw,cookie)
    finally:
        N.invoke = invoke
        controller.ControllerBus = original_bus
    assert len(costs)==12
    return costs


def check_headers(raw, fixture, code, cookie):
    images = []
    for data in [raw, fixture]:
        image=I.SYMBOLS.bundle()
        image['raw']=data
        images.append(image)
    seeds=[N.Bus(b) for b in images]
    for m in seeds:
        m.raw_page(1,193)
        N.put(m,CurrentBank=193,SelectedCharacter=40)
        m[FIXTURE_PC:FIXTURE_PC+len(code)]=code
        for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
    controls=0
    valid_costs=[]
    for mapper in [2,3,160,216]:
        for bank,index,bad in [(0,0,0)] + [(k,i,x) for k in [2,3] for i in range(16) for x in range(256) if x!=cookie[i]]:
            pair=[]
            for seed in seeds:
                N.put(seed,CurrentBankC=mapper)
                seed.raw_page(2,mapper)
                seed.writes.clear()
                if bank:seed.ram[bank][0x1fe0+index]=bad
                c=N.NesMPU(memory=seed,pc=0xaee2)
                c.a,c.x,c.y,c.p,c.sp=83,3,8,0x31,224
                c.stPushWord(0x5aff)
                r56=bytes(seed[8:10]);overlay=tuple(seed.rawtags)
                for _ in range(600):
                    if c.pc==0x5b00:break
                    assert seed[c.pc];c.step()
                else:raise AssertionError('bounded stateless cookie compare')
                assert c.sp==224 and bytes(seed[8:10])==r56 and tuple(seed.rawtags)==overlay
                assert c.p&1==int(bank==0)
                maps=tuple(v for a,v in seed.writes if a==0x5116)
                pair.append((c.processorCycles,maps))
                if bank:seed.ram[bank][0x1fe0+index]=cookie[index]
            assert pair[0][1]==pair[1][1],(mapper,bank,index,bad,pair)
            if bank:controls+=1
            else:valid_costs.append([v[0] for v in pair])
    return valid_costs,controls


def main():
    proposal=OUT/'oam-source.json'
    ui_path=I.O/'frontend-v2.json'
    rows=json.loads(proposal.read_text())['patches']
    cookie=bytes.fromhex(rows[-1]['new_hex'])
    raw=P.compose(P.compose(P.MINI_PRIVATE.read_bytes(),json.loads(ui_path.read_text())['patches']),rows)
    assert P.sha(raw)==C.PIN
    code,src=build(cookie)
    at=16+65*8192+ACTUAL_HOT_JSR-0xa000
    assert raw[at:at+3]==bytes([0x20,ACTUAL_COMPARE&255,ACTUAL_COMPARE>>8])
    fixture=raw[:at]+bytes([0x20,FIXTURE_PC&255,FIXTURE_PC>>8])+raw[at+3:]
    original, fast = [measure_main(image,cookie,body) for image,body in [(raw,None),(fixture,code)]]
    assert all(a[1]==b[1] for a,b in zip(original,fast))
    rows=[[a[0],b[0],a[0]-b[0]] for a,b in zip(original,fast)]
    print('Whole Main saved',[row[-1] for row in rows],flush=True)
    costs, negatives = check_headers(raw,fixture,code,cookie)
    q=dict(passed=True, CPU_only=True, ROM_written=False, fixture_only=True, resident_funding=False,
           base_SHA256=C.PIN, scratch_PC=FIXTURE_PC, scratch_leaf_bytes=len(code),
           actual_hot_replaced_JSR=ACTUAL_HOT_JSR, exact_full_cookie=bytes(cookie).hex(),
           valid_callback_CPU_pairs=costs, individual_poison_cases=negatives, idle_Main_CPU_pairs=rows,
           scope='Fixture preserves all 32 exact comparisons, original bank visits, scratch, native gameplay, OAM, SMC and public result. Exhausts every wrong value at each individual header byte in both physical banks. Unchanged cold/retire ingress. No lifetime/cache claim and no executable ROM placement.',
           bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__),src,proposal,ui_path,P.MINI_PRIVATE]})
    (OUT/'cookie-measurement.json').write_text(json.dumps(q,indent=2)+'\n')
    print('Complete cookie',len(code),'B, callbacks',costs,'poisons',negatives,'Main savings',[row[-1] for row in rows],flush=True)


if __name__=='__main__':
    main()
