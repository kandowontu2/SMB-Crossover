"""Exact linked native instructions and original-vs-leaf isolated CPU cases."""
from pathlib import Path
import csv,hashlib,json,random,re,sys
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/arthur-source-v1'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from arthur_source_map_v1 import machine,ROM,EXPECTED
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
S={m[2]:int(m[1],16)for line in (OUT/'leaf.lbl').read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\w+)',line))}
P=json.loads((OUT/'kernel-source-proof.json').read_text())
RAW=(OUT/'leaf.bin').read_bytes()
FIELDS={int(v['original']):dict(new=S[k],size=v['bytes'])for k,v in P['state']['fields'].items()}

def cpu():
    mem=[0]*65536;mem[0x8000:0xc000]=RAW
    return NesMPU(memory=mem)

def call(c,name,a=0,x=0,y=0,original=False,cut=False):
    c.a,c.x,c.y,c.p,c.sp=a,x,y,0x24,0xff
    c.stPushWord(0x7ffe);c.pc=P['exports'][name]if original else S[name]
    audio=[];steps=0
    while c.pc!=0x7fff:
        steps+=1;assert steps<30000,(name,hex(c.pc),'instruction bound')
        if original and(c.pc in(0xDB99,0xED51,0xE9CA,0xEA2F,0xBB27)or(cut and c.pc==0xE229)):
            if c.pc==0xED51:c.memory[0x0800]=c.a;audio.append(c.a)
            elif c.pc==0xDB99:
                c.memory[0x0801]=(c.memory[0x0801]+1)&255;c.FlagsNZ(c.memory[0x0801])
            elif c.pc in(0xE9CA,0xEA2F):c.a=c.memory[0x0802 if c.pc==0xE9CA else 0x0803];c.FlagsNZ(c.a)
            elif c.pc==0xBB27:c.a=0;c.memory[0x04f0+c.x]=0;c.FlagsNZ(0)
            c.pc=(c.stPopWord()+1)&65535
        else:
            if not original and c.pc==S['ArHostSfx']:audio.append(c.a)
            c.step()
    return dict(a=c.a,x=c.x,y=c.y,p=c.p,sp=c.sp,audio=audio,steps=steps)

def instruction_check():
    rows=[]
    for r in P['instructions_and_data']:
        at=S[f"ArO_{r['address']:04X}"]-0x8000;old=bytes.fromhex(r['bytes']);got=RAW[at:at+len(old)];want=bytearray(old)
        if r['kind']=='instruction'and r.get('relocation'):
            z=r['relocation'];target=S[z['symbol']]
            if z['kind']=='native_data_pointer_immediate':want[1]=(target>>8)if r['address']==0xEFDE else(target&255)
            elif r['mode']=='rel':want[1]=(target-(at+0x8000+2))&255
            elif len(old)==2:want[1]=target&255
            else:want[1:3]=target.to_bytes(2,'little')
        assert got==want,(hex(r['address']),old.hex(),want.hex(),got.hex())
        rows.append(dict(source=r['address'],kind=r['kind'],bytes=len(old)))
    return dict(records=len(rows),instructions=sum(r['kind']=='instruction'for r in rows),native_bytes=sum(r['bytes']for r in rows),all_exact_after_declared_operands=True)

def differential():
    rng=random.Random(0xA271);results=[]
    names=['ArNativeSetBodyPalette','ArNativeMove','ArNativeRise','ArNativeFall','ArNativeTerminalFall','ArNativeIdlePose','ArNativeAirPose',
      'ArNativeAttackPose','ArNativeAttack','ArNativeThrow','ArNativeInjuryInit','ArNativeLance','ArNativeDagger',
      'ArNativeTorch','ArNativeAxe','ArNativeCross','ArNativeShotContact','ArNativePlayerContact','ArNativeCollectWeapon','ArNativeRepairArmor']
    for name in names:
        for case in range(96):
            original=machine(4);old=NesMPU(memory=original.memory);new=cpu()
            for addr,d in FIELDS.items():
                for i in range(d['size']):old.memory[addr+i]=new.memory[d['new']+i]=rng.randrange(256)
            def setv(addr,value,i=0):old.memory[addr+i]=new.memory[FIELDS[addr]['new']+i]=value
            setv(0xCF,0);setv(0x94,0);setv(0xBA,case&1);setv(0xE0,0)
            setv(0x04f0,0x80|(4 if case&1 else 0)|(0x20 if case&2 else 0))
            setv(0x061d,0);setv(0x0607,case%7);setv(0x0631,case%3)
            setv(0x0509,80);setv(0x05f1,[0,4,8,12][case%4]);setv(0x0599,case*37%240)
            setv(0x056d,case%2);setv(0x0583,case%2);setv(0x05af,case*17%256)
            setv(0x053a,[0x40,0x42,0x44,0x36,0x4f][case%5]);setv(0xCC,0x40 if case%3 else 0)
            setv(0x85,0);setv(0x0647,case%31)
            for slot in range(17,20):setv(0x04f0,0,slot);setv(0x0631,0x23+case%5,slot)
            x,y,a=0,17,[0,6,12,44,56][case%5]
            if name in('ArNativeRise','ArNativeFall'):setv(0x0607,case%6+(name=='ArNativeRise'))
            if name in('ArNativeLance','ArNativeDagger','ArNativeTorch','ArNativeAxe','ArNativeCross'):
                x=17;setv(0x04f0,0x40|(case%2),17);setv(0x05f1,4 if case&1 else 12,17)
                setv(0x0607,case%24,17);setv(0x0599,case*13%240,17);setv(0x056d,0,17)
                setv(0x0583,0,17);setv(0x05af,case*17%256,17)
            if name=='ArNativeShotContact':
                x=1;y=17;setv(0x26,case%17);setv(0x27,case%13)
                setv(0x0631,0x23+case%5,17)
            if name=='ArNativePlayerContact':x=1;y=2;setv(0x26,case%17);setv(0x27,case%13)
            if name in('ArNativeCollectWeapon','ArNativeRepairArmor'):x=1
            old.memory[0x0802]=new.memory[S['ArAheadTile']]=[0,0xc6,0xd0,0xdf][case%4]
            old.memory[0x0803]=new.memory[S['ArFloorTile']]=[0,0xc6,0xd0,0xdf][case%4]
            old.memory[0x0800]=new.memory[S['ArSoundRequest']]=0
            old.memory[0x0801]=new.memory[S['ArCameraRequest']]=0
            left=call(old,name,a,x,y,True,name=='ArNativeInjuryInit');right=call(new,name,a,x,y)
            assert {k:v for k,v in left.items()if k!='steps'}=={k:v for k,v in right.items()if k!='steps'},(name,case,left,right)
            for addr,d in FIELDS.items():
                if addr in(0x9d,0x9e)and old.memory[0x9d]+256*old.memory[0x9e]==0xf2a3:
                    assert new.memory[S['ArR_009D']]+256*new.memory[S['ArR_009E']]==S['ArO_F2A3'];continue
                assert old.memory[addr:addr+d['size']]==new.memory[d['new']:d['new']+d['size']],(name,case,hex(addr))
            assert old.memory[0x0800]==new.memory[S['ArSoundRequest']]
            assert old.memory[0x0801]==new.memory[S['ArCameraRequest']]
            results.append(dict(kernel=name,case=case,original_instructions=left['steps'],leaf_instructions=right['steps']))
    return dict(kernels=len(names),cases=len(results),all_private_native_state_and_registers_equal=True,
                per_kernel={n:sum(r['kernel']==n for r in results)for n in names})

def leaf_cases():
    c=cpu();call(c,'ArInit')
    read=lambda name:c.memory[S[name]]
    put=lambda name,value:c.memory.__setitem__(S[name],value)
    # One authentic native update is three video ticks; native X step is3px.
    x0=read('ArR_05AF')
    for _ in range(30):call(c,'ArTick',1)
    assert read('ArUpdates')==10 and read('ArR_05AF')==x0+30
    # Natural flat leaf floor is resolved only through its declared contact API.
    def step(pad):
        before=read('ArR_0599');call(c,'ArStep',pad)
        if read('ArMode')==2 and read('ArR_0599')>=184 and before<=184:
            put('ArR_0599',184);call(c,'ArOnLand')
    call(c,'ArInit');ys=[]
    for i in range(20):step(0x80 if i==0 else 0);ys.append(read('ArR_0599'))
    assert min(ys)==152 and read('ArMode')==0 and read('ArJumpCount')==0
    single_apex=184-min(ys)
    call(c,'ArInit');ys=[]
    for i in range(26):step(0x80 if i in(0,6)else 0);ys.append(read('ArR_0599'))
    assert min(ys)==120 and read('ArMode')==0
    double_apex=184-min(ys)
    call(c,'ArInit')
    for i in range(10):step(0x80 if i in(0,4,8)else 0)
    assert read('ArJumpCount')==2 # third fresh press cannot rearm the jump
    call(c,'ArInit')
    for i in range(10):step(0x80)
    assert read('ArJumpCount')==1 # held A cannot repeat the authored jump
    call(c,'ArInit');put('ArDoubleJumpEnabled',0);ys=[]
    for i in range(20):step(0x80 if i in(0,6)else 0);ys.append(read('ArR_0599'))
    assert min(ys)==152
    # Native crouch lock survives Down->Right and releases with neutral.
    call(c,'ArInit');step(4);x0=read('ArR_05AF');step(1)
    assert read('ArR_04F0')&2 and read('ArR_05AF')==x0
    step(0);assert read('ArR_04F0')&2==0
    pickups=[]
    for item,weapon in((6,0x44),(7,0x36),(8,0x42),(9,0x4f),(10,0x40)):
        call(c,'ArInit');call(c,'ArCollectPickup',item)
        assert read('ArR_053A')==weapon
        pickups.append(dict(native_item=item,weapon=weapon))
    # Source geometry/lifetime is exercised for each real weapon; no fake grant.
    shots=[]
    for item,weapon in((6,0x44),(7,0x36),(8,0x42),(9,0x4f),(10,0x40)):
        call(c,'ArInit');call(c,'ArCollectPickup',item);step(0x40)
        assert c.memory[S['ArR_04F0']+17]!=0
        assert c.memory[S['ArR_0631']+17]=={0x40:0x23,0x42:0x24,0x44:0x25,0x36:0x26,0x4f:0x27}[weapon]
        start=c.memory[S['ArR_05AF']+17]
        for _ in range(3):step(0)
        assert c.memory[S['ArR_05AF']+17]!=start or c.memory[S['ArR_0607']+17]!=0
        shots.append(dict(native_item=item,native_weapon=weapon,source_projectile_executed=True))
    call(c,'ArInit');call(c,'ArTakeHit');assert read('ArR_04F0')&0x60==0x60 and read('ArHurtMode')==1
    call(c,'ArCollectPickup',5);assert read('ArR_04F0')&0x20==0
    call(c,'ArOnLand');step(0);assert read('ArR_053B')==8
    call(c,'ArInit');call(c,'ArTakeHit');put('ArR_04F0',read('ArR_04F0')&~0x40);call(c,'ArTakeHit');assert read('ArDead')==1
    return dict(native_walk_pixels_per_update=3,video_ticks_per_update=3,single_jump_apex=single_apex,
        authored_double_jump_apex=double_apex,third_press_rejected=True,held_repeat_rejected=True,
        adaptation_disabled_matches_single_jump=True,native_crouch_lock=True,pickups=pickups,weapons=shots,
        armor_loss_repair_and_naked_death=True)

def main():
    exact=instruction_check();diff=differential();leaf=leaf_cases()
    files=[Path(__file__),ROM,OUT/'leaf.bin',OUT/'leaf.lbl',OUT/'leaf.dbg',OUT/'native-kernels.s',OUT/'native-context.inc',
       OUT/'component.s',OUT/'leaf.cfg',OUT/'kernel-source-proof.json',OUT/'build-proof.json',
       ROOT/'tools/audit/arthur_source_map_v1.py',ROOT/'tools/audit/arthur_extract_kernels_v1.py',ROOT/'tools/audit/verify_native_relocation.py']
    result=dict(status='PASS_PRIVATE_LEAF_ORIGINAL_INSTRUCTION_AND_CPU_CONTROLS',original_ROM_sha256=EXPECTED,
      leaf_sha256=sha(OUT/'leaf.bin'),native_instruction_check=exact,original_vs_ported=diff,leaf_controller_cases=leaf,
      capacity=dict(native_code_bytes=S['ArNativeEnd']-S['ArNativeStart'],authored_leaf_bytes=S['ArLeafEnd']-S['ArLeafStart'],
                    private_ZP_bytes=P['state']['ZP_bytes'],private_BSS_bytes=S['ArLeafStateEnd']-S['ArNativeStateStart']),
      bindings={str(p.resolve()):sha(p)for p in files},
      limits='Isolated actual6502 cases with declared world/camera/audio/consume adapters. No host leases/hooks or native controller/gameplay admission. Original pickup reachability and all-pose native art review remain separate.')
    p=OUT/'cpu-receipt.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],leaf_sha256=result['leaf_sha256'],native_instruction_check=exact,
       differential_cases=diff['cases'],capacity=result['capacity'],receipt_sha256=sha(p))))
if __name__=='__main__':main()
