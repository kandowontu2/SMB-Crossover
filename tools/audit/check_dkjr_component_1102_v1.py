"""Original instruction differentials and exact body raster recovery, in memory."""
from pathlib import Path
import sys,re,json,hashlib,collections
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import dkjr_original_cpu_1102_v1 as D
import prepare_dkjr_component_1102_v1 as P
O=P.O

class Flat(list):pass

def labels():
    return {n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)}

def main():
    L=labels();blob=(O/'component.bin').read_bytes();layout=json.loads((O/'component-layout.json').read_text())
    data=L['DkjrSourceData'];imports={v:int(k,16)for k,v in layout['imports'].items()}
    impcounts=collections.Counter();cases=collections.Counter();states=collections.Counter();digest=hashlib.sha256();minimum_sp=255
    for address in imports:
        assert blob[address-0xa000:address-0xa000+3]==bytes([0x4c,address&255,address>>8])
    # These two donor pointers can name immutable recovered descriptors/fruit.
    # OAM ($04/05) remains an original RAM address and is translated by each
    # component indirect instruction. No general arbitrary-pointer claim.
    ptrs=[2,0x91]
    def translate(r,to_private):
        r=bytearray(r)
        for p in ptrs:
            v=r[p]+256*r[p+1]
            if to_private and P.DATA_LO<=v<P.DATA_HI:v=data+v-P.DATA_LO
            elif not to_private and data<=v<data+P.DATA_HI-P.DATA_LO:v=P.DATA_LO+v-data
            else:continue
            r[p]=v&255;r[p+1]=v>>8
        return r
    def original(r,entry,regs):
        c=D.T.NesMPU(memory=D.Bus(),pc=entry);c.memory[:2048]=r
        if entry==0xca82:
            c.a,c.x,c.y,c.p=regs;c.sp=0xfd;c.stPushWord(0x5ffe)
            D.until(c,0xcabf)
            c.sp+=2
            return c,(c.a,c.x,c.y,c.p,c.sp,0)
        result=D.T.run(c,entry,*regs,limit=60000)
        return c,result
    def relocated(r,entry,regs):
        nonlocal minimum_sp
        m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob;m[0xc000:0xc800]=translate(r,True)
        m.writes=[];m.apu=[];m.ppuwrites=[]
        c=D.T.NesMPU(memory=m,pc=L[f'D_{entry:04x}']);c.a,c.x,c.y,c.p=regs;c.sp=0xfd;c.stPushWord(0x5ffe)
        n=0
        while c.pc!=0x5fff:
            minimum_sp=min(minimum_sp,c.sp)
            if c.pc in imports:
                imp=imports[c.pc];impcounts[f'{imp:04X}']+=1
                q=D.T.NesMPU(memory=D.Bus(),pc=imp)
                q.memory[:2048]=translate(m[0xc000:0xc800],False)
                q.memory[0x100:0x200]=m[0x100:0x200]
                q.a,q.x,q.y,q.p,q.sp=c.a,c.x,c.y,c.p,c.sp
                ret=m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1
                D.until(q,ret&65535,limit=60000)
                m[0xc000:0xc800]=translate(q.memory[:2048],True)
                m[0x100:0x200]=q.memory[0x100:0x200]
                c.a,c.x,c.y,c.p,c.sp,c.pc=q.a,q.x,q.y,q.p,q.sp,q.pc
            else:
                assert m[c.pc]!=0,('Component BRK',hex(c.pc),hex(entry))
                c.step()
            n+=1;assert n<60000,(hex(entry),hex(c.pc))
        return translate(m[0xc000:0xc800],False),(c.a,c.x,c.y,c.p,c.sp)
    def compare(r,entry,regs=(0,0,0,0x20),cohort='natural'):
        q,z=original(r,entry,regs);a,got=relocated(r,entry,regs)
        expected=bytes(q.memory[:2048]);indices=list(range(256))+list(range(0x200,0x800))
        diff=[(i,expected[i],a[i])for i in indices if expected[i]!=a[i]]
        assert not diff,(cohort,hex(entry),diff[:12])
        assert z[:3]==got[:3] and z[3]&0xef==got[3]&0xef and z[4]==got[4],(hex(entry),z,got)
        cases[cohort]+=1;digest.update(entry.to_bytes(2,'little')+expected[:256]+expected[0x200:])
        return q
    selected={0xce6c,0xcea2,0xcf37,0xf1af,0xd251,0xd412,0xd43a,0xd955,0xdbb3,0xdb20,0xdaf7}
    for stage in range(1,5):
        for fill in [0,0x55,0xaa,0xff]:
            for flags in [0x20,0xf1]:
                r=bytearray([fill]*2048);r[0x4a]=stage
                compare(r,0xca82,(12,7,9,flags),'source-actor-initialize')
    natural_frames=0;earned_vine=None;boot_frames=None
    sequences=[('idle',[0]*100),('walk',[1]*105),('jump',[1]*48+[0x88]*80+[0]*45),
               ('climb',[1]*48+[0x81]*9+[8]*70),('two-vines',[1]*48+[0x81]*9+[1]*18+[8]*60)]
    for name,controls in sequences:
        c,boot_frames=D.active()
        def trace(q):
            if q.pc in selected:compare(bytes(q.memory[:2048]),q.pc,(q.a,q.x,q.y,q.p),'natural-'+name)
        for f,pad in enumerate(controls):
            D.frame(c,pad,trace);natural_frames+=1;states[c.memory[0x6b]]+=1
            if name=='climb'and f==57:earned_vine=bytes(c.memory[:2048])
    assert earned_vine and earned_vine[0x6b]==2
    # Continue the naturally earned vine actor without the donor's independently
    # scheduled enemies. Original controller/probes/actor/fruit still execute.
    continuations=[];poses=set()
    for name,controls in [('single-up',[8]*220),('single-down',[4]*100),
                           ('spread-up',[1]*20+[8]*130),('spread-down',[1]*20+[4]*100),
                           ('release-right',[1]*65+[0]*20),('jump-off',[0x81]*70)]:
        c=D.T.NesMPU(memory=D.Bus(),pc=0);c.memory[:2048]=earned_vine
        start_y=c.memory[0x210];min_y=start_y;max_y=start_y;seen=set();grips=set();fruit=False
        for f,pad in enumerate(controls):
            c.memory.pad=[pad,0];D.T.run(c,0xf219)
            for entry in [0xce6c,0xcea2,0xd251,0xd412,0xdbb3,0xf1af]:
                r=bytes(c.memory[:2048]);regs=(c.a,c.x,c.y,c.p)
                c=compare(r,entry,regs,'earned-vine-'+name)
            c.memory[0x55]=c.memory[0x54]
            z=D.state(c);seen.add(z['state']);grips.add(z['vine_grip']);poses.add((z['pose'],c.memory[0x212]))
            min_y=min(min_y,z['y']);max_y=max(max_y,z['y']);fruit|=bool(c.memory[0x8c])
        continuations.append(dict(name=name,epochs=len(controls),start_y=start_y,min_y=min_y,max_y=max_y,
                                  states=sorted(seen),grips=sorted(grips),fruit_dropped=fruit,final=D.state(c)))
    # No-vine jump on original starting platform: exact source input/transition/
    # movement sequence, Up+A prevents horizontal travel into the first vine.
    c,_=D.active()
    for _ in range(48):D.frame(c,1)
    ys=[]
    for f in range(60):
        c.memory.pad=[0x88 if f==0 else 0,0];D.T.run(c,0xf219)
        for entry in [0xce6c,0xcea2,0xd251,0xd412,0xf1af]:c=compare(bytes(c.memory[:2048]),entry,(c.a,c.x,c.y,c.p),'jump-envelope')
        c.memory[0x55]=c.memory[0x54];ys.append(c.memory[0x210])
    assert min(ys)==184 and c.memory[0x6b]==1
    jump_receipt=dict(start_y=199,min_y=min(ys),rise=199-min(ys),epochs=len(ys),final_y=ys[-1],airborne_epochs=c.memory[0x7e])
    climb_receipts=[]
    for name,entry,direction,grip,delta in [('single-up',0xd72b,1,1,-8),('single-down',0xd72b,2,1,42),
        ('double-up',0xd8a3,1,2,-20),('double-down',0xd8a3,2,2,18)]:
        c=D.T.NesMPU(memory=D.Bus(),pc=0);c.memory[:2048]=earned_vine
        c.memory[0x210]=128;c.memory[0x54]=direction;c.memory[0x71]=grip;c.memory[0x78]=0;c.memory[0x56]=0
        for _ in range(32):c=compare(bytes(c.memory[:2048]),entry,cohort='unblocked-vine-kinematic-leaf')
        assert c.memory[0x210]==128+delta,(name,c.memory[0x210])
        climb_receipts.append(dict(name=name,epochs=32,delta_y=delta,px_per_epoch=delta/32,
                                   explicit_unblocked_grip_fixture=True))
    c,_=D.active();c.memory[0x6b]=5;c.memory[0x210]=0xd8
    compare(bytes(c.memory[:2048]),0xdaf7,cohort='source-defeat-life-boundary')
    # Every actual authored fruit, contact at a table-derived position. These
    # are explicit contact fixtures, not earned traversal claims.
    fruit_receipts=[]
    for stage in range(1,5):
        seed,_=D.active();seed.memory[0x4a]=stage
        p=seed.memory[0xc309+2*(stage-1)]+256*seed.memory[0xc30a+2*(stage-1)]
        seed.memory[0x91]=p&255;seed.memory[0x92]=p>>8;seed.memory[0x93]=seed.memory[p]
        for fi in range(seed.memory[p]//7):
            fx,fy=seed.memory[p+1+fi*7:p+3+fi*7]
            c=D.T.NesMPU(memory=D.Bus(),pc=0);c.memory[:2048]=seed.memory[:2048]
            c.memory[0x213]=(fx-20)&255;c.memory[0x210]=fy
            c=compare(bytes(c.memory[:2048]),0xd2bd,cohort='authored-fruit-bounds')
            c=compare(bytes(c.memory[:2048]),0xd955,cohort='authored-fruit-touch')
            assert c.memory[0x8c]==fi+1,(stage,fi,c.memory[0x8c])
            dropped=bytes(c.memory[:2048]);ys=[]
            for _ in range(110):
                c=compare(bytes(c.memory[:2048]),0xdbb3,cohort='authored-fruit-fall');ys.append(c.memory[0x230])
            assert not c.memory[0x8c] and ys[-1]==255
            # Original first enemy family has two cells; later-family enemies
            # have four. Both original hit paths are retained below.
            if stage in [1,3,4]:
                c.memory[:2048]=dropped;c.memory[0xa0]=1;c.memory[0xb0]=1
                if stage in [1,4]:enemy=0x2c0;c.memory[0xa3]=0;family=1
                else:enemy=0x240;family=2
                c.memory[enemy]=fy;c.memory[enemy+3]=fx
                c=compare(bytes(c.memory[:2048]),0xd43a,cohort='authored-fruit-enemy-contact')
                assert c.memory[0x68]==family,(stage,fi,c.memory[0x68])
                c=compare(bytes(c.memory[:2048]),0xd1ae,cohort='authored-fruit-hit')
                assert c.memory[enemy]==255 and c.memory[0x66]==1
                for _ in range(70):
                    c=compare(bytes(c.memory[:2048]),0xd1ae,cohort='authored-fruit-hit-animation')
                    if not c.memory[0x66]:break
                assert not c.memory[0x66] and not c.memory[0x68]
            fruit_receipts.append(dict(stage=stage,fruit=fi+1,x=fx,y=fy,fall_px_per_epoch=2))
    # Original renderer raster versus equivalent four 8x16 pairs per pose.
    raw=D.donor();chr_data=raw[16400:];art=bytearray(chr_data[:0x58*16]);packets=[];pixel_cases=0
    def tile(t,x,y):
        p=t*16+y;b=7-x;return (chr_data[p]>>b&1)|((chr_data[p+8]>>b&1)<<1)
    for base in range(0,0x58,8):
        for facing in [0,1]:
            c,_=D.active();c.memory[0]=64;c.memory[1]=96;c.memory[2]=base
            c=compare(bytes(c.memory[:2048]),0xe9ee,(facing,7,9,0xf1),'pose')
            cells=[list(c.memory[0x210+i:0x214+i])for i in range(0,32,4)]
            old=bytearray(32*16);new=bytearray(32*16);pairs=[]
            for y,t,at,x in cells:
                for py in range(8):
                    for px in range(8):
                        old[(y-96+py)*32+x-64+px]=tile(t,7-px if at&64 else px,7-py if at&128 else py)
            for i in range(0,8,2):
                y,t,at,x=cells[i];bottom=cells[i+1]
                assert t&1==0 and bottom==[y+8,t+1,at,x] and not at&128
                pairs.append(dict(x=x-64,y=y-96,tile=t,attr=at))
                for py in range(16):
                    for px in range(8):new[py*32+x-64+px]=tile(t+py//8,7-px if at&64 else px,py&7)
            assert old==new
            packets.append(dict(base=base,render_mode=facing,cells=pairs,raster_sha256=hashlib.sha256(old).hexdigest()));pixel_cases+=len(old)
    fruit_art=[]
    for base in [0xa4,0xa8,0xac]:
        mapped=len(art)//16;art.extend(chr_data[base*16:(base+4)*16])
        fruit_art.append(dict(source_base=base,paired_base=mapped,paired_cells=2))
    hit_art=[]
    for tile_id in range(0x90,0x94):
        mapped=len(art)//16;art.extend(chr_data[tile_id*16:(tile_id+1)*16]+bytes(16))
        hit_art.append(dict(source_tile=tile_id,paired_base=mapped,paired_cells=1,transparent_lower_half=True))
    (O/'body.chr').write_bytes(art)
    (O/'body-poses.json').write_text(json.dumps(dict(width=32,height=16,poses=packets,
                  palette=[0x0f,0x30,0x06,0x36],original_hardware_palette_slot=1,
                  source_8x8_cells=8,paired_8x16_cells=4,body_CHR_bytes=1408,fruit_art=fruit_art,
                  hit_art=hit_art,source_sprite_palettes=[[0x0f,0x30,0x2a,0x16],[0x0f,0x30,0x06,0x36],[0x0f,0x2a,0x17,0x37]],
                  CHR_bytes=len(art)),indent=2)+'\n')
    receipt=dict(passed=True,donor_sha256=D.SHA,code_sha256=layout['code_sha256'],
                 CPU_cases=sum(cases.values()),cohorts=dict(cases),natural_NMI_frames=natural_frames,
                 natural_boot_frames=boot_frames,states={str(k):v for k,v in states.items()},
                 imports=dict(impcounts),minimum_CPU_SP=minimum_sp,trace_sha256=digest.hexdigest(),
                 state_compared='All original RAM except hardware stack, plus AXYP (B ignored) and SP. Original immutable pointers normalized only at two declared state pairs.',
                 jump=jump_receipt,unblocked_vine_kinematics=climb_receipts,
                 earned_vine_continuations=continuations,pose_cases=len(packets),pixel_comparisons=pixel_cases,
                 authored_fruit_contacts=fruit_receipts,body_CHR_bytes=1408,total_CHR_bytes=len(art),
                 scope='Untimed original reset/NMI sequences, isolated continuations of a naturally earned vine state and explicit authored-fruit contact fixtures. Imports independently execute original donor services on equivalent state. No host/native/ISR qualification.')
    (O/'CPU.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
