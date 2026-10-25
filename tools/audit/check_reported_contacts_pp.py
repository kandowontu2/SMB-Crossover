"""Execute linked contact code against the actual PM failure and staged repair."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def qualified(b,scope,name):
    # Resolve a local assembler label by its owning routine, never by a
    # same-spelled label in another compiled procedure.
    dbg=b['debug'];owners={}
    for line in dbg.splitlines():
        if line.startswith('scope\t'):
            f=dict(t.split('=',1) for t in line[6:].split(',') if '=' in t)
            if f.get('name')=='"'+scope+'"':owners[f['id']]=True
    found=[]
    for line in dbg.splitlines():
        if line.startswith('sym\t'):
            f=dict(t.split('=',1) for t in line[4:].split(',') if '=' in t)
            if f.get('scope') in owners and f.get('name')=='"'+name+'"' and 'val' in f:found.append(int(f['val'],0))
    assert len(found)==1,(scope,name,found)
    return found[0]

def arena(b,entry,values):
    m=Memory(b);m.page(1,(location(b,entry)-16)//8192)
    m[address(b,'CurrentBank')]=m.banks[1]|128
    for n,v in values.items():
        if isinstance(v,(list,tuple,bytes)):
            for i,x in enumerate(v):m[address(b,n)+i]=x&255
        else:m[address(b,n)]=v&255
    return m
def run(b,m,entry,a=0,x=0,y=0,p=0x20,pc=None):
    c=NesMPU(memory=m,pc=pc if pc is not None else address(b,entry));c.sp=0xed
    c.stPushWord(0x5aff);c.a=a;c.x=x;c.y=y;c.p=p
    for _ in range(50000):
        if c.pc==0x5b00:return c
        c.step()
    raise AssertionError(('CPU timeout',entry,hex(c.pc),m.banks))

def inspect(path):
    b=load(path)
    import gzip
    b['debug']=path.with_suffix('.dbg').read_text() if path.with_suffix('.dbg').exists() else gzip.decompress(path.with_suffix('.dbg.gz').read_bytes()).decode()
    stats={'ROM_sha256':sha(path),'origin_wrong':0,'origin_cases':0,'inhale_body_wrong':0,
        'inhale_body_cases':0,'ground_enemy_displaced':0,'suction_cases':0,'mike_head_wrong':0,'mike_head_cases':0}
    for char,px,page,dx,slot in itertools.product(range(1,20),range(256),[2,3],[-7,0,6,8,15],[0,1]):
        target=page*256+px+dx;col=(target//16)&15;parity=(target//256)&1
        values=dict(SelectedCharacter=char,Player_X_Position=px,Player_PageLoc=page,Player_Y_HighPos=1,
            MmBlockAttack=0,SmCeilingHit=0,R6=(address(b,'Block_Buffer_1')+parity*16+col)&255,
            SmHeadX=target&240,SmHeadPage=target>>8)
        m=arena(b,'SophiaHeadBlockOrigin',values)
        # Sophia's old source-contact cache is populated, because its old
        # dedicated adapter was already correct for an admitted source head.
        m[address(b,'RgTempX')]=target&255;m[address(b,'RgTempPage')]=target>>8
        m[address(b,'SmCeilingHit')]=128
        run(b,m,'SophiaHeadBlockOrigin',x=slot)
        actual=m[address(b,'Block_X_Position')+slot]+256*m[address(b,'Block_PageLoc')+slot]
        stats['origin_cases']+=1;stats['origin_wrong']+=actual!=(target&~15)
    for face,offset,age,held,variant in itertools.product([1,2],[-20,-8,0,8,20],[0,8],[0,64],[0,1]):
        world=512+128;enemy=world+offset
        m=arena(b,'KbBodyContact',dict(SelectedCharacter=13,KbVariant=variant,KbHurt=0,KbCopy=0,
            KbAction=1,KbActionAge=age,SavedJoypadBits=held,PlayerFacingDir=face,
            Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=176,
            Enemy_Flag=[1],Enemy_State=[0],Enemy_ID=[6],Enemy_X_Position=[enemy&255],
            Enemy_PageLoc=[enemy>>8],Enemy_Y_Position=[184],Enemy_Y_HighPos=[1]))
        c=run(b,m,'KbBodyContact',x=0)
        expected=variant==0 and age==0 and held==64 and ((0<=offset<57) if face==1 else (-57<offset<=0))
        stats['inhale_body_cases']+=1;stats['inhale_body_wrong']+=bool(c.p&1)!=expected
    for face,delta,enemy_id in itertools.product([1,2],[16,24,40],[0,1,2,3,5,6,7,9,10,11,12,13,14,15,18,20,51]):
        world=640;enemy=world+(delta if face==1 else -delta)
        m=arena(b,'KbWeapons',dict(SelectedCharacter=13,KbVariant=0,PlayerFacingDir=face,
            Player_X_Position=128,Player_PageLoc=2,Player_Y_Position=176,Enemy_Flag=[1],Enemy_State=[0],
            Enemy_ID=[enemy_id],Enemy_X_Position=[enemy&255],Enemy_PageLoc=[enemy>>8],Enemy_Y_Position=[184],
            Enemy_Y_HighPos=[1],Enemy_Y_Speed=[2],Enemy_Y_MoveForce=[200],ObjectOffset=4))
        c=run(b,m,'KbWeapons',pc=qualified(b,'KbWeapons','Suction'))
        stats['suction_cases']+=1;stats['ground_enemy_displaced']+=m[address(b,'Enemy_Y_Position')]!=184
        assert m[address(b,'ObjectOffset')]==4
    for status,attack in itertools.product(range(3),[0,1]):
        m=arena(b,'NativeRarePlayerHeadCollisionCore',dict(SelectedCharacter=16,PlayerStatus=status,MmBlockAttack=attack))
        c=run(b,m,'CrossoverBlockSize',y=0,p=0x61)
        stats['mike_head_cases']+=1;stats['mike_head_wrong']+=c.y!=0
        assert c.p&0x41==0x41,'size gate must preserve sampled-cell carry and overflow'
    return stats

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    rows={}
    for k,path in [('baseline',a.baseline),('candidate',a.rom)]:
        rows[k]=inspect(path);print(k,json.dumps(rows[k]),flush=True)
        (a.output/'partial.json').write_text(json.dumps(rows,indent=2)+'\n')
    assert rows['baseline']['origin_wrong'] and rows['baseline']['inhale_body_wrong'] and rows['baseline']['ground_enemy_displaced']
    assert all(rows['candidate'][n]==0 for n in ['origin_wrong','inhale_body_wrong','ground_enemy_displaced','mike_head_wrong'])
    q=dict(passed=True,components=rows,driver_sha256=sha(Path(__file__)),scope='Actual linked CPU contact routines; native PPU/gameplay qualification remains separate.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()
