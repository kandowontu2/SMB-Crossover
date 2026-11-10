"""FF588 proposal paired typed-callback/lifetime/fault/real-vector checks.

Genuine cold-menu witnesses are separate from explicit CPU unit fixtures.
No ROM, emulator, generated receipt or build output is written.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import audit_ff_immediate_guard_factor_1110 as G

L,W,N,Fix=G.L,G.W,G.N,G.Fix
PROPOSAL_PIN='6b35d68d7f653f9250f07cdfd451aba2b2751ea9ef89ddb50306c6a76a5a6a85'
PIN='58811ce678361678deff8f32966e945869be75e0f017e2bf36b2e2430ab96ebd'
SERVICES=tuple(service for service,_ in G.PAIRS)
COUNTS=Counter();SEAM_KEYS=set()


def application(m,c):
    return (L.app(m),L.regs(c),bytes(m[0x15a:0x17b]),m.vram,
            m.chr_latches,m.upper,m.ppu_addr,m.toggle,m.ppuctrl,tuple(m.ppu_log))


def fixture(seed,raw,fields=None,byte=None,bit=0):
    m=L.clone(seed);m.bundle=dict(m.bundle,raw=raw)
    for i,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(i,tag)
    if fields:N.put(m,**fields)
    if byte is not None:m.ram[3][0x1fe0+byte]^=1<<bit
    N.put(m,NmiDisable=255)
    return m


def save_sample(m,c,stop,origin,key):
    if key in SEAM_KEYS:return
    SEAM_KEYS.add(key);q,d=L.clone(m,c)
    L.SAMPLES.append((origin,stop,q,d))


def pair(seed,image,trial,service,fields=None,byte=None,bit=0,flags=0x31,y=0,
         capture=False,patches=()):
    outputs=[]
    for raw in (image,trial):
        m=fixture(seed,raw,fields,byte,bit);entered=[]
        seam_points={p['transfer'] for p in patches}|{p['ready'] for p in patches}
        def watch(mem,c):
            if c.pc>=0x8000:
                tag=mem.rawtags[(c.pc-0x8000)//8192]
                if tag==3:entered.append(c.pc)
                if capture and raw is trial and tag==190 and c.pc in seam_points:
                    save_sample(mem,c,(0x5b00,224),'typed_callback_guard_transfer',
                                (service,c.pc,flags&4))
        c=L.call(m,service,a=83,x=0,y=y,p=flags,observe=watch)
        if byte is not None:
            assert not entered,('corrupt full cookie executed RAM3',service,byte,bit,entered)
        outputs.append((application(m,c),m,c))
    assert outputs[0][0]==outputs[1][0],('typed callback difference',service,fields,byte,bit,flags,y,
                                       L.regs(outputs[0][2]),L.regs(outputs[1][2]))
    COUNTS['paired_actual_typed_callback_calls']+=1
    return outputs[-1][1:]


def callbacks(seed,image,trial,patches):
    for variant in range(4):
        for service in SERVICES:
            for y in (0,255):
                for flags in (0x31,0xf1):
                    pair(seed,image,trial,service,dict(FfVariant=variant),flags=flags,y=y)
                    COUNTS['four_classes_all_typed_AXYP_two_Y_two_flags']+=1
    for service in SERVICES:
        for flags in (0x31,0x35):
            pair(seed,image,trial,service,flags=flags,capture=True,patches=patches)
            COUNTS['all_transfer_unmasked_and_masked_reached_contexts']+=1
    for field in ('GameEngineSubroutine','GamePauseStatus'):
        for value in range(256):
            for service in SERVICES:
                pair(seed,image,trial,service,{field:value})
                COUNTS[f'all_typed_{field}_0_to_255']+=1
    for field in ('TimerControl','MmDeathFlag'):
        for value in (0,1,127,128,255):
            for service in SERVICES:
                pair(seed,image,trial,service,{field:value})
                COUNTS[f'all_typed_{field}_boundaries']+=1
    print(json.dumps(dict(event='all_typed_callbacks_pass',counts=dict(COUNTS))),flush=True)


def faults(seed,image,trial,patches):
    for owner in range(256):
        if owner==22:continue
        for service in SERVICES:
            pair(seed,image,trial,service,dict(SelectedCharacter=owner))
            COUNTS['all255_foreign_owners_all_typed_callbacks']+=1
    for byte in range(16):
        for bit in range(8):
            for service in SERVICES:
                for flags in (0x31,0xf1):
                    pair(seed,image,trial,service,byte=byte,bit=bit,flags=flags)
                    COUNTS['all16_cookie_bytes_all8_bit_faults_all_typed_two_flags']+=1
    # Cold constructor/readback and public gates are unchanged, but exercise
    # warm acceptance, preceding-c10 warm rejection and real readback failure.
    m=fixture(seed,trial);L.forced(m);before=bytes(m.ram[3]);reads=m.ppu_reads
    c=L.call(m,'FwLoad');assert c.p&1 and bytes(m.ram[3])==before and m.ppu_reads==reads
    COUNTS['new_warm_zero_PPU_reads']+=1
    original=W.ROM.read_bytes();oldkernel=original[1048592+893*1024:1048592+901*1024]
    oldcookie=original[511774:511790]
    m=fixture(seed,trial);m.ram[3][:]=oldkernel;m.ram[3][0x1fe0:0x1ff0]=oldcookie
    c=L.call(m,'FwCheck');assert not c.p&1
    COUNTS['preceding_c10_warm_header_rejected']+=1
    for fault in (False,True):
        m=fixture(seed,trial);m.ram[3][0x1fe0]=0;L.forced(m);injected=[];reads=m.ppu_reads
        def inject(mem,c):
            if fault and not injected and c.pc==W.address(mem.bundle,'FwVerify256'):
                mem.ram[3][0]^=1;injected.append(1)
        c=L.call(m,'FwLoad',observe=inject)
        if fault:
            assert injected and not c.p&1 and m.ram[3][0x1fe0]==0
            COUNTS['real_copy_readback_fault_rejects_validity']+=1
        else:
            assert c.p&1 and m.ppu_reads-reads==16400
            COUNTS['real_cold_reload_after_invalid_cookie']+=1
    print(json.dumps(dict(event='full_cookie_and_foreign_pass',counts=dict(COUNTS))),flush=True)


def lifecycle(seed,image,trial):
    for variant in range(4):
        for scenario in ('ready','new_life','life_award','new_area','new_world','unready'):
            fields=dict(FfVariant=variant,FfPower=2,FfEarned=2,FfHealCharges=3 if variant==1 else 0,
                        SavedJoypadBits=0,SavedJoypad1Bits=0,A_B_Buttons=0,Player_State=0)
            if scenario=='new_life':fields['NumberofLives']=1
            elif scenario=='life_award':fields['NumberofLives']=3
            elif scenario=='new_area':fields['AreaAddrsLOffset']=1
            elif scenario=='new_world':fields['WorldNumber']=1
            elif scenario=='unready':fields['FfReady']=0
            for service in SERVICES:
                m,c=pair(seed,image,trial,service,fields)
                assert N.get(m,'FfVariant')==variant
                if service=='FwSvcMovement':
                    power=0 if scenario in ('new_life','unready') else 2
                    charges=3 if variant==1 and power else 0
                    assert (N.get(m,'FfPower'),N.get(m,'FfEarned'),N.get(m,'FfHealCharges'))==(power,power,charges)
                COUNTS['four_class_six_lifecycle_scenarios_all_typed']+=1
    print(json.dumps(dict(event='all_typed_lifecycle_pass',counts=dict(COUNTS))),flush=True)


def main():
    assert sha256(Path(G.__file__).read_bytes()).hexdigest()==PROPOSAL_PIN
    original=W.ROM.read_bytes();assert sha256(original).hexdigest()==W.PIN
    image,kernel,cookie,*_=Fix.proposal(original);assert sha256(image).hexdigest()==L.PIN
    b=W.Symbols.bundle();trial,patches,changed=G.proposal(image,b)
    assert sha256(trial).hexdigest()==PIN
    with patch.object(L,'sample',lambda *a,**k:None):
        old,oldcold,_=L.cold_menu(image,0,cookie,kernel)
        seed,cold,last=L.cold_menu(trial,0,cookie,kernel)
    assert L.app(old)==L.app(seed)
    L.SAMPLES.clear();L.SAMPLE_KEYS.clear();L.PATHS.clear();L.DEEPEST=None
    save_sample(seed,last,(last.pc,last.sp),'genuine_idle_normal_NMI',('normal',))
    callbacks(seed,image,trial,patches)
    faults(seed,image,trial,patches)
    lifecycle(seed,image,trial)
    expected={p['transfer'] for p in patches}|{p['ready'] for p in patches}
    reached={c.pc for origin,stop,m,c in L.SAMPLES if origin=='typed_callback_guard_transfer'}
    assert reached==expected,('unreached transfer/ready seams',sorted(expected-reached))
    vectors=L.irq_checks(image)
    print(json.dumps(dict(passed=True,source_CPU_only=True,in_memory_proposal_only=True,
        Mesen_run=False,ROM_written=False,output_files=0,parent_SHA256=L.PIN,proposal_SHA256=PIN,
        proposal_checker_SHA256=PROPOSAL_PIN,changed_operand_bytes=len(changed),new_allocated_bytes=0,
        kernel_SHA256=sha256(kernel).hexdigest(),cookie=cookie.hex(),actual_menu_cold=[oldcold,cold],
        cases=dict(COUNTS),all8_transfer_instructions_and8_ready_targets_reached=len(reached),
        real_vectors=vectors,saved_cycles_per_empty_Main=2728,remaining_cycles_about=50000,
        scope='Eight same-entry authenticated typed transfers. Explicit CPU fault/lifecycle/ABI fixtures follow genuine cold starts; real-vector cuts and resumed foreground compare against identical no-interrupt cuts. Original public guards/full16-byte checks remain. This optimization does not resolve overwhelming idle lag and has no fullstage or physical qualification.')),flush=True)


if __name__=='__main__':main()
