"""Proposed C94/A95 bridge CPU ABI, not an allocation or linked/native build."""
from pathlib import Path
import argparse,hashlib,itertools,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
import rogue_dawn_map_v1 as ref

NAMES=sorted(set(re.findall(r'RdHost\w+', (ROOT/'src/rogue_dawn_control.s').read_text())))
EXPECTED='55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217'

def labels(p):
    return {m[2]:int(m[1],16)for line in p.read_text().splitlines()if(m:=re.match(r'al ([\da-fA-F]+) \.(\S+)',line))}

def build(out):
    out.mkdir(parents=True,exist_ok=True)
    (out/'bridge-wrapper.s').write_text('CurrentBank=$0145\nRdHostService=$5C79\nRdHostEntryA=$5FB7\nRdHostDispatch=$A600\n.include "rogue_dawn_host_bridge.s"\n')
    (out/'bridge.cfg').write_text('MEMORY { C:start=$DF50,size=$B0,bank=94,file=%O; }\nSEGMENTS { ROGUE_DAWN_HOST_BRIDGE:load=C,type=ro; }\n')
    cc=ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(out/'bridge-wrapper.s'),'-o',str(out/'bridge.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(out/'bridge.cfg'),str(out/'bridge.o'),'-o',str(out/'bridge.bin'),'-Ln',str(out/'bridge.lbl'),'--dbgfile',str(out/'bridge.dbg')],check=True)
    return (out/'bridge.bin').read_bytes(),labels(out/'bridge.lbl')

def run(b,code,symbols,service,pflags,sp,interrupt=None):
    m=Memory(b);m.page(1,124);m.page(2,94)
    m[address(b,'CurrentBank')]=252;m[address(b,'CurrentBankC')]=222
    for n,v in [('SelectedCharacter',2),('DisableScreenFlag',1),('Sprite0HitDetectFlag',0),('OperMode',1),('GameEngineSubroutine',8),('NmiDisable',255 if interrupt and interrupt[1]=='lagNMI'else 0)]:m[address(b,n)]=v
    m[0x5fee]=1;m[0x5c79]=0xa5;m[0x5fb7]=0x5a
    m[3]=0x97;m[4]=0x83
    c=NesMPU(memory=m,pc=symbols[NAMES[service]]);c.sp=sp
    c.a,c.x,c.y,c.p=(service*13+41)&255,(service*7+5)&255,(service*17+19)&255,pflags
    original=(c.a,c.x,c.y,c.p&0xcf);c.stPushWord(0x5aff)
    for k in range(sp+1,256):m[0x100+k]=(k*17+29)&255
    live=bytes(m[0x101+sp:0x200]);r0=bytes(m[3:5]);before_smc=bytes(m[z]for z in SMC)
    expected=((original[0]^0xd3)&255,(original[1]+47)&255,(original[2]^0x81)&255,((pflags^service^0xc7)|0x30)&0xcf)
    events=[];own_writes=[];low=c.sp;trace=[];fired=False;calls=0
    def snapshot():return(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(m.banks),m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],bytes(m[z]for z in SMC),bytes(m[0x101+c.sp:0x200]),m[0x5c79],m[0x5fb7])
    for _ in range(1000):
        if c.pc==0x5b00:break
        if interrupt and not fired and c.pc==interrupt[0]:
            fired=True;before=snapshot();kind=interrupt[1]
            physical=before[6];want=list(physical)
            if kind!='IRQ' and physical[1]!=(before[7]&127):
                assert bytes(m[c.pc:c.pc+3])==bytes.fromhex('8d1551'),'Only actual shadow-before-hardware gap admitted'
                want[1]=before[7]&127
            if kind=='IRQ':c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
            else:c.nmi()
            for _ in range(50000):
                low=min(low,c.sp);c.step()
                if c.pc==before[5]and c.sp==before[4]:break
            else:raise AssertionError(('ISR timeout',interrupt,hex(c.pc)))
            after=snapshot();assert after[:6]==before[:6] and after[6]==tuple(want) and after[7:]==before[7:],('ISR preservation',interrupt,before,after)
        if c.pc==0xa600:
            assert m.banks[1]==95 and m.banks[2]==94
            assert m[0x5c79]==service and(c.a,c.x,c.y,c.p&0xcf)==original
            calls+=1;c.a,c.x,c.y,c.p=expected;c.p|=0x30;c.pc=(c.stPopWord()+1)&65535;c.processorCycles+=6
            continue
        trace.append(c.pc);at=c.pc;prior=len(m.writes);c.step();low=min(low,c.sp)
        own_writes.extend(m.writes[prior:]);events.extend([dict(PC=f'{at:04X}',address=f'{z:04X}',value=v)for z,v in m.writes[prior:]if z in [0x5115,address(b,'CurrentBank')]])
    else:raise AssertionError(('bridge timeout',hex(c.pc)))
    assert calls==1 and c.sp==sp and(c.a,c.x,c.y,c.p&0xcf)==expected
    assert m.banks[1:3]==[124,94]and m[address(b,'CurrentBank')]==252 and m[address(b,'CurrentBankC')]==222,(service,sp,m.banks,m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],events)
    assert bytes(m[z]for z in SMC)==before_smc and bytes(m[0x101+sp:0x200])==live
    assert not any(z in [3,4]for z,_ in own_writes),'Bridge cannot borrow NMI-live zero-page scratch'
    if not interrupt:assert bytes(m[3:5])==r0
    assert not interrupt or fired
    return dict(service=service,name=NAMES[service],input_flags=pflags,entry_SP=sp,minimum_SP=low,internal_bridge_CPU=c.processorCycles-6,full_callback_ABI=True,mapper_events=events,interrupt_R0_R1_before_after=[r0.hex(),bytes(m[3:5]).hex()]if interrupt else None),sorted(set(trace))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-host-plan-v1/bridge-controls.json');a=p.parse_args()
    code,s=build(a.output.parent);assert len(code)==175 and s['RdHostBridgeStart']==0xdf50 and s['RdHostBridgeEnd']==0xdfff
    host=ROOT/'build/sunny-integrated-final.nes';b=scoped_load(host);assert ref.digest(b['raw'])==EXPECTED
    at=16+94*8192+0x1f50;assert b['raw'][at:at+176]==b'\xff'*176
    image=bytearray(b['raw']);image[at:at+len(code)]=code;b=dict(b,raw=bytes(image))
    global SMC
    SMC=[address(b,n)+k for n,k in [('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]]
    rows=[]
    for service,flags,sp in itertools.product(range(22),[0x30,0x31,0x70,0x71,0xb0,0xb1,0xfe,0xff],[160,176,240]):
        row,_=run(b,code,s,service,flags,sp);rows.append(row)
    _,trace=run(b,code,s,3,0x71,176)
    seams=[]
    for pc,kind in itertools.product([z for z in trace if z>=s['RdHostCall95']],['IRQ','NMI','lagNMI']):
        row,_=run(b,code,s,3,0x71,176,(pc,kind));seams.append(dict(PC=f'{pc:04X}',kind=kind,minimum_SP=row['minimum_SP'],actual_interrupt_R0_R1=row['interrupt_R0_R1_before_after']))
    proof=dict(passed=True,native_run=False,allocation_approved=False,scope=__doc__,proposed_C94=dict(start='DF50',end_exclusive='DFFF',bytes=len(code),tail_remaining=1),callback_names=NAMES,callback_cells=len(rows),rows=rows,actual_host_ISR_seams=seams,minimum_SP=min(z['minimum_SP']for z in seams),state_request={'5C79':'callback service ID','5FB7':'transient saved entry A; no resource value'},typed_target='A95:A600 callback target is an explicit CPU boundary, not an implemented host dispatcher.',smc_all_five_unchanged=True,notes=['Fixed owner contract A124/C94 on callback entry; restored actual saved A owner.','Output callback AXYP is preserved, including N/Z and decimal flag; ordinary FarCallCommon alone would not preserve target N/Z.','No new zero-page scratch or shared SMC use. Caller-live stack exact.','Only genuine pre-STA5115 shadow/hardware gap permits NMI normalization; IRQ restores the prior physical bank.','In-memory insertion only, no actual candidate ROM is emitted or modified.','New host routines must preserve C94 and cannot re-enter a control callback while one is outstanding.'],bindings=[ref.binding(x)for x in [Path(__file__),ROOT/'src/rogue_dawn_host_bridge.s',host,host.with_suffix('.dbg'),a.output.parent/'bridge.bin',a.output.parent/'bridge.lbl']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,bridge_bytes=len(code),callback_cells=len(rows),ISR_seams=len(seams),minimum_SP=proof['minimum_SP'])))
if __name__=='__main__':main()
