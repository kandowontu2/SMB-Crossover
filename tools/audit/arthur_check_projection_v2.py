"""Verify declared native transformations and source-vs-five-slot actual6502."""
from pathlib import Path
import hashlib,json,random,re,sys
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'build/arthur-source-v1';OUT=ROOT/'build/arthur-projected-leaf-v2'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
symbols=lambda p:{m[2]:int(m[1],16)for l in p.read_text().splitlines()if(m:=re.match(r'al ([0-9A-Fa-f]+) \.(\w+)',l))}
S=symbols(OUT/'leaf.lbl');B=symbols(BASE/'leaf.lbl')
RAW=(OUT/'leaf.bin').read_bytes();OLD=(BASE/'leaf.bin').read_bytes()
P=json.loads((BASE/'kernel-source-proof.json').read_text());Q=json.loads((OUT/'projection-proof.json').read_text())
SLOTS={0:0,17:1,18:2,19:3,1:4}
WIDEN={0xa5:0xad,0xb5:0xbd,0xa6:0xae,0xb6:0xbe,0xa4:0xac,0xb4:0xbc,0x85:0x8d,0x95:0x9d,
       0x86:0x8e,0x96:0x8e,0x84:0x8c,0x94:0x8c,0x65:0x6d,0x75:0x7d,0xe5:0xed,0xf5:0xfd,
       0x25:0x2d,0x35:0x3d,0x05:0x0d,0x15:0x1d,0x45:0x4d,0x55:0x5d,0xc5:0xcd,0xd5:0xdd,
       0xe4:0xec,0xc4:0xcc,0xe6:0xee,0xf6:0xfe,0xc6:0xce,0xd6:0xde,0x06:0x0e,0x16:0x1e,
       0x46:0x4e,0x56:0x5e,0x26:0x2e,0x36:0x3e,0x66:0x6e,0x76:0x7e,0x24:0x2c}
class TrackedMemory(list):
    def __init__(self):super().__init__([0]*65536);self.writer=None;self.last={}
    def __setitem__(self,key,value):
        super().__setitem__(key,value)
        if isinstance(key,int):self.last[key]=self.writer
def cpu(raw):
    mem=TrackedMemory();mem[0x8000:0xc000]=raw;return NesMPU(memory=mem)
def call(c,syms,name,a=0,x=0,y=0):
    c.a,c.x,c.y,c.p,c.sp=a,x,y,0x24,0xff;c.stPushWord(0x7ffe);c.pc=syms[name];steps=0
    while c.pc!=0x7fff:
        steps+=1;assert steps<30000,(name,hex(c.pc),'instruction bound');c.memory.writer=c.pc;c.step()
    return dict(a=c.a,x=c.x,y=c.y,p=c.p,sp=c.sp,steps=steps)

def instructions():
    rows=[];widened=set(Q['declared_transformations']['widened_absolute_scalar_instructions'])
    edits={0xE045:1,0xE04D:3,0xE051:4}
    for r in P['instructions_and_data']:
        at=S[f'ArO_{r["address"]:04X}'];old=bytes.fromhex(r['bytes']);got=RAW[at-0x8000:at-0x8000+5]
        if r['kind']=='data':assert got[0]==old[0];kind='exact_data'
        elif r['mode']=='rel':
            target=S[r['relocation']['symbol']]
            if got[0]==old[0]:assert got[1]==(target-at-2)&255;kind='relative_branch'
            else:
                assert got[:3]==bytes([old[0]^0x20,3,0x4c])and int.from_bytes(got[3:5],'little')==target,(r,got.hex())
                kind='equivalent_long_branch'
        else:
            want=bytearray(old);z=r.get('relocation')
            if r['address']in widened:
                want=bytearray([WIDEN[old[0]]])+S[z['symbol']].to_bytes(2,'little');kind='absolute_scalar_projection'
            elif r['address']in edits:want[1]=edits[r['address']];kind='logical_slot_bound'
            elif z:
                target=S[z['symbol']]
                if z['kind']=='native_data_pointer_immediate':want[1]=(target>>8)if r['address']==0xEFDE else(target&255)
                elif len(old)==2:want[1]=target&255
                else:want[1:3]=target.to_bytes(2,'little')
                kind='declared_relocation'
            else:kind='exact_instruction'
            assert got[:len(want)]==want,(hex(r['address']),kind,want.hex(),got.hex())
        rows.append(dict(source=r['address'],kind=kind))
    return dict(records=len(rows),native_instructions=sum(r['kind']=='instruction'for r in P['instructions_and_data']),
       per_kind={k:sum(r['kind']==k for r in rows)for k in sorted({r['kind']for r in rows})},all_declared_transformations_checked=True)

def differential():
    rng=random.Random(0xA2715);results=[]
    names=['ArNativeSetBodyPalette','ArNativeMove','ArNativeRise','ArNativeFall','ArNativeTerminalFall','ArNativeIdlePose','ArNativeAirPose',
      'ArNativeAttackPose','ArNativeAttack','ArNativeThrow','ArNativeInjuryInit','ArNativeLance','ArNativeDagger',
      'ArNativeTorch','ArNativeAxe','ArNativeCross','ArNativeShotContact','ArNativePlayerContact','ArNativeCollectWeapon','ArNativeRepairArmor']
    for name in names:
        for case in range(128):
            old,new=cpu(OLD),cpu(RAW)
            def setv(addr,value,i=0):
                key=f'ArR_{addr:04X}';old.memory[B[key]+i]=new.memory[S[key]+(SLOTS[i]if P['state']['fields'][key]['bytes']==20 else i)]=value
            for key,v in P['state']['fields'].items():
                for i in(SLOTS if v['bytes']==20 else range(v['bytes'])):setv(v['original'],rng.randrange(256),i)
            for k,v in((0xcf,0),(0x94,0),(0xba,case&1),(0xe0,0),(0xa9,0),(0x85,0),
                (0x4f0,0x80|(4 if case&1 else 0)|(0x20 if case&2 else 0)),(0x61d,0),(0x607,case%7),(0x631,case%3),
                (0x509,80),(0x5f1,[0,4,8,12][case%4]),(0x599,case*37%240),(0x56d,case%2),(0x583,case%2),
                (0x5af,case*17%256),(0x53a,[0x40,0x42,0x44,0x36,0x4f][case%5]),(0xcc,0x40 if case%3 else 0),(0x647,case%31)):setv(k,v)
            for slot in(17,18,19):setv(0x4f0,0,slot);setv(0x631,0x23+case%5,slot)
            x,y,a=0,0,[0,6,12,44,56][case%5]
            if name=='ArNativeThrow':y=17
            if name in('ArNativeRise','ArNativeFall'):setv(0x607,case%6+(name=='ArNativeRise'))
            if name in('ArNativeLance','ArNativeDagger','ArNativeTorch','ArNativeAxe','ArNativeCross'):
                x=17
                for k,v in((0x4f0,0x40|(case%2)),(0x5f1,4 if case&1 else 12),(0x607,case%24),
                    (0x599,case*13%240),(0x56d,0),(0x583,0),(0x5af,case*17%256)):setv(k,v,17)
            if name in('ArNativeShotContact','ArNativePlayerContact'):
                x=1;y=17 if name=='ArNativeShotContact'else 0;setv(0x26,case%17);setv(0x27,case%13)
            if name in('ArNativeCollectWeapon','ArNativeRepairArmor'):x=1
            for syms,c in((B,old),(S,new)):
                c.memory[syms['ArAheadTile']]=[0,0xc6,0xd0,0xdf][case%4]
                c.memory[syms['ArFloorTile']]=[0,0xc6,0xd0,0xdf][case%4]
            left=call(old,B,name,a,x,y);right=call(new,S,name,a,SLOTS.get(x,x),SLOTS.get(y,y))
            for reg in('a','p','sp'):assert left[reg]==right[reg],(name,case,reg,left,right)
            for reg in('x','y'):assert right[reg]in(left[reg],SLOTS.get(left[reg],left[reg])),(name,case,reg,left,right)
            for key,v in P['state']['fields'].items():
                addr=v['original']
                if addr in(0x9d,0x9e)and old.memory[B['ArR_009D']]+old.memory[B['ArR_009E']]*256==B['ArO_F2A3']:
                    assert new.memory[S['ArR_009D']]+new.memory[S['ArR_009E']]*256==S['ArO_F2A3'];continue
                for i in(SLOTS if v['bytes']==20 else range(v['bytes'])):
                    l=old.memory[B[key]+i];r=new.memory[S[key]+(SLOTS[i]if v['bytes']==20 else i)]
                    logical_writers={0x23:'ArO_F03B',0x9f:'ArO_EFDC',0xa9:None}
                    if l!=r and addr in logical_writers:
                        allowed=([B['ArO_F611'],B['ArO_F6C2']]if addr==0xa9 else[B[logical_writers[addr]]])
                        if old.memory.last.get(B[key]+i)in allowed:l=SLOTS.get(l,l)
                    assert l==r,(name,case,key,i,l,r)
            for key in('ArSoundRequest','ArCameraRequest'):assert old.memory[B[key]]==new.memory[S[key]]
            results.append(dict(kernel=name,case=case,source_instructions=left['steps'],projected_instructions=right['steps']))
    return dict(kernels=len(names),cases=len(results),all_mapped_state_registers_flags_and_adapter_effects_equal=True,
       logical_index_normalization='Native player0/shot17..19/target1 -> compact0/1..3/4. ReturnedX/Y and savedA9 normalized only as logical slot representations.')

def leaf_cases():
    c=cpu(RAW);read=lambda n:c.memory[S[n]];put=lambda n,v:c.memory.__setitem__(S[n],v)
    def step(pad):
        before=read('ArR_0599');call(c,S,'ArStep',pad)
        if read('ArMode')==2 and read('ArR_0599')>=184 and before<=184:put('ArR_0599',184);call(c,S,'ArOnLand')
    apices=[]
    for jump_frames in((0,),(0,6),(0,4,8)):
        call(c,S,'ArInit');ys=[];maximum=0
        for i in range(30):step(0x80 if i in jump_frames else 0);ys.append(read('ArR_0599'));maximum=max(maximum,read('ArJumpCount'))
        apices.append(dict(presses=list(jump_frames),apex=184-min(ys),max_jump_count=maximum,landed=read('ArMode')==0))
    assert apices[0]['apex']==32 and apices[1]['apex']==64 and apices[2]['max_jump_count']==2
    call(c,S,'ArInit');x0=read('ArR_05AF')
    for _ in range(30):call(c,S,'ArTick',1)
    assert read('ArUpdates')==10 and read('ArR_05AF')==x0+30
    pickups=[]
    for item,weapon in((6,0x44),(7,0x36),(8,0x42),(9,0x4f),(10,0x40)):
        call(c,S,'ArInit');call(c,S,'ArCollectPickup',item);assert read('ArR_053A')==weapon;step(0x40)
        assert c.memory[S['ArR_04F0']+1]and c.memory[S['ArR_0631']+1]=={0x40:0x23,0x42:0x24,0x44:0x25,0x36:0x26,0x4f:0x27}[weapon]
        for _ in range(3):step(0)
        pickups.append(dict(source_item=item,weapon=weapon,compact_projectile1_executed=True))
    call(c,S,'ArInit');call(c,S,'ArTakeHit');assert read('ArR_04F0')&0x60==0x60
    call(c,S,'ArCollectPickup',5);assert read('ArR_04F0')&0x20==0
    call(c,S,'ArOnLand');step(0);assert read('ArR_053B')==8
    call(c,S,'ArInit');call(c,S,'ArTakeHit');put('ArR_04F0',read('ArR_04F0')&~0x40);call(c,S,'ArTakeHit');assert read('ArDead')==1
    return dict(apices=apices,walk30ticks_pixels=30,source_updates=10,weapons=pickups,native_armor_loss_repair_and_death=True)

def main():
    exact=instructions();diff=differential();leaf=leaf_cases()
    files=[Path(__file__),OUT/'projection-proof.json',OUT/'leaf.bin',OUT/'leaf.lbl',OUT/'native-kernels.s',OUT/'component.s',
       BASE/'handoff.json',BASE/'cpu-receipt.json',BASE/'leaf.bin',BASE/'leaf.lbl',ROOT/'tools/audit/verify_native_relocation.py']
    result=dict(status='PASS_ABSTRACT_EXRAM_FIVE_SLOT_SOURCE_CPU_PROJECTION',leaf_sha256=sha(OUT/'leaf.bin'),
       native_instruction_check=exact,differential=diff,leaf_controller_cases=leaf,
       code=dict(native_bytes=S['ArNativeEnd']-S['ArNativeStart'],leaf_bytes=S['ArLeafEnd']-S['ArLeafStart']),
       state=Q['state'],bindings={str(p.resolve()):sha(p)for p in files},
       limits='Isolated CPU proof, not a host lease or native gameplay admission. Host pointer save/restore, NMI interleavings, collision and sprite/palette ownership remain unverified.')
    p=OUT/'cpu-receipt.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],instructions=exact,differential=diff,code=result['code'],receipt_sha256=sha(p))))
if __name__=='__main__':main()
