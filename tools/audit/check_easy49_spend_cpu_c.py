"""Check compiled ammo commit and Easy rejection against an independent oracle."""
from pathlib import Path
import hashlib,itertools,json,sys,time
R=Path(__file__).resolve().parents[2];H=R/'build/verification/root49-easy-injury-private-a';B=R/'build/verification/root49-easy-hard-user-baseline-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RETURN=0x5d00
def main():
    from py65.devices.mpu6502 import MPU
    sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'build/verification/agent49g-samus-crouch-fix-proposal-b'));from image import Image
    out=H/'spend-cpu-c.json';assert not out.exists()
    template=bytes((i*29+71)&255 for i in range(10240))
    class Memory:
        def __init__(self,im,bank):self.im=im;self.bank=bank;self.ram=bytearray(template);self.writes=[]
        @staticmethod
        def physical(a):
            if a<0x2000:return a&2047
            if 0x6000<=a<0x8000:return 2048+a-0x6000
            raise AssertionError(('unexpected hardware',hex(a)))
        def __getitem__(self,a):
            if a>=0x8000:
                bank=62 if a<0xa000 else self.bank if a<0xc000 else 0 if a<0xe000 else 63
                return self.im.raw[16+bank*8192+(a&8191)]
            return self.ram[self.physical(a)]
        def __setitem__(self,a,v):v&=255;self.ram[self.physical(a)]=v;self.writes.append((a,v))
        def put(self,n,v,i=0):self.ram[self.physical(self.im.ram[n]+i)]=v&255
    def execute(im,hook,case,ammo_index):
        mode,char,item,cost,ammo,star,p=case;mem=Memory(im,hook['physical_bank'])
        for name,v in [('CrossoverBehaviorVersion',mode),('SelectedCharacter',char),('PlayerStatus',2),('StarInvincibleTimer',star),('InvDirty',19)]:mem.put(name,v)
        if ammo_index!=255:mem.put('InvAmmo',ammo,ammo_index)
        cpu=MPU(memory=mem,pc=hook['address']);cpu.a=item;cpu.x=0xa5;cpu.y=cost;cpu.p=p;cpu.sp=0xe4
        mem.ram[0x1e5]=(RETURN-1)&255;mem.ram[0x1e6]=(RETURN-1)>>8
        initial=bytes(mem.ram);stack=[];steps=0
        while cpu.pc!=RETURN:
            pc=cpu.pc;op=mem[pc];sp=cpu.sp
            if op==32:stack.extend([(0x100+sp,(pc+2)>>8),(0x100+((sp-1)&255),(pc+2)&255)])
            elif op==72:stack.append((0x100+sp,cpu.a))
            elif op==8:stack.append((0x100+sp,cpu.p|0x30))
            cpu.step();steps+=1;assert steps<200
        classic=mode==0 and 1<=char<=5
        free=ammo_index==255 or bool(star)
        afford=free or ammo>=cost
        wanted=not classic and afford
        assert bool(cpu.p&1)==wanted,(case,ammo_index,cpu.p,wanted)
        expected=bytearray(initial)
        if not classic:
            for n,v in [('InvCost',cost),('InvItem',item),('InvIndex',char*16+item)]:expected[Memory.physical(im.ram[n])]=v
            if not free and afford:
                expected[Memory.physical(im.ram['InvAmmo']+ammo_index)]=ammo-cost
                expected[Memory.physical(im.ram['InvDirty'])]=20
        for a,v in stack:expected[Memory.physical(a)]=v&255
        assert mem.ram==expected,('Complete RAM commit oracle',case,ammo_index)
        assert [q for q in mem.writes if 0x100<=q[0]<0x200]==stack
        return (cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc),bytes(mem.ram),stack
    report=dict(status='RUNNING_COMPILED_AMMO_BOUNDARY',script_sha256=sha(__file__),results=[],complete_Easy_behavior=False,hardware_or_route_proof=False)
    def save():out.write_text(json.dumps(report,indent=2)+'\n')
    save();t=time.monotonic()
    for mapper in ['mmc3','mmc5']:
        new=Image(H/('source/build/smb-crossover-'+mapper+'.nes'));old=Image(B/('smb-crossover-'+mapper+'.nes'))
        nh=new.hook('InventorySpend');oh=old.hook('InventorySpend')
        tab=old.hook('InvAmmoIndex')['rom_offset'];tab2=new.hook('InvAmmoIndex')['rom_offset']
        aliases=old.raw[tab:tab+192];assert aliases==new.raw[tab2:tab2+192]
        count=diff=0;digest=hashlib.sha256()
        for case in itertools.product([0,1],[1,2,3,4,5,9,10,11],range(16),[0,1,2,7,112],[0,1,2,6,111,112,255],[0,1],[0,1,2,64,128,195]):
            mode,char,item,cost,ammo,star,p=case;idx=aliases[char*16+item]
            actual,ram,stack=execute(new,nh,case,idx);count+=1
            if mode!=0 or char>5:
                control,cram,_=execute(old,oh,case,idx)
                assert actual==control,('Unaffected fullABI',case,actual,control)
                expected=bytearray(cram)
                for a,v in stack:expected[Memory.physical(a)]=v
                assert ram==expected;diff+=1
            digest.update(bytes((*case,actual[3]&1)))
        report['results'].append(dict(mapper=mapper,cases=count,unaffected_full_ABI_and_RAM_differentials=diff,digest=digest.hexdigest(),ROM_sha256=sha(new.path)))
        save();print(mapper,count,'PASS',flush=True)
    report.update(status='PASS_COMPILED_AMMO_BOUNDARY',elapsed_seconds=time.monotonic()-t,limits='Pure CPU routine with NMOS decimal flag clear to match RP2A03 arithmetic; exact RAM including stack. No native pickup/drop or ordinary-route proof.')
    save();print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
