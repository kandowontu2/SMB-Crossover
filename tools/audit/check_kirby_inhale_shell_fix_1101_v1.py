"""Compact actual-source Kirby contact regressions; no native/Main claim."""
from pathlib import Path
import hashlib,itertools,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from check_karnov_actor_1101_v1 import Memory
O=R/'build/kirby-inhale-shell-fix-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def labels(path):
    rows=[];scopes={}
    for line in path.read_text().splitlines():
        d=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line))
        if line.startswith('scope\t'):scopes[d['id']]=d['name'].strip('"')
        elif line.startswith('sym\t')and'val'in d:rows.append(d)
    return {((scopes.get(d.get('scope'),'')+'::')if scopes.get(d.get('scope'),'')else'')+d['name'].strip('"'):int(d['val'],0)for d in rows}

class Proof:
    def __init__(self,mode='baseline'):
        self.mode=mode;self.q=json.loads((O/'current-witness.json').read_text());self.s={n:int(s['val'],0)for n,s in self.q['symbols'].items()};self.l=labels(O/(mode+'.dbg'));self.s.update(self.l);self.count=0;self.low=224;self.code=(O/(mode+'.bin')).read_bytes();self.box=json.loads((O/'native-box-witness.json').read_text())['rows']['BoundBoxCtrlData'];self.blob=(O/'current-kirby-code.bin').read_bytes()
    def make(self):
        m=Memory();b=self.code;m[0xa000:0xa000+len(b)]=b
        # Native bbox source table fixture; actual ROM table binding is a
        # separate integration gate, not implied by this source CPU test.
        box=self.box;at=box['CPU'];m[at:at+84]=bytes.fromhex(box['bytes'])
        for n,v in dict(KbVariant=0,KbHurt=0,KbAction=1,KbActionAge=0,SavedJoypadBits=64,PlayerFacingDir=1,Player_X_Position=80,Player_PageLoc=1,Player_Y_Position=176,ObjectOffset=3).items():m[self.s[n]]=v
        self.enemy(m,0,100,184,1);m.writes=[];return m
    def enemy(self,m,x,world,y,high=1,kind=6):
        for n,v in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=0,Enemy_X_Position=world&255,Enemy_PageLoc=world>>8,Enemy_Y_Position=y,Enemy_Y_HighPos=high).items():m[self.s[n]+x]=v
        m[0x646+x]=9
    def run(self,m,entry,x=0,y=0,p=0x31,hooks=None):
        c=NesMPU(memory=m,pc=self.s[entry]);c.a=85;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff);hits=[]
        for steps in range(3000):
            if c.pc==0x5b00:break
            if hooks and c.pc in hooks:
                hooks[c.pc](c,m);c.pc=c.stPopWord()+1;continue
            if c.pc in[self.s['ShellOrBlockDefeat'],self.s['HandleEnemyFBallCol']]:hits.append((c.pc,c.x));c.pc=c.stPopWord()+1;continue
            if c.pc==0x15a:
                target=m[0x16c]+256*m[0x16d]
                # Genuine source KbInputs in another bank; emulate only this
                # declared bank switch boundary. Native FarCall/ISR closure
                # is deliberately not claimed by these isolated tests.
                assert target==self.s['KbInputs'],hex(target)
                seg=next(s for s in self.q['segments']if s['name']=='KIRBY_CORE');bank=bytes(m[0xa000:0xc000]);data=self.blob[seg['witness_offset']:seg['witness_offset']+seg['bytes']];m[0xa000:0xa000+len(data)]=data
                c.a=m[0x16a];c.pc=target;ret=m[0x100+c.sp+1]+256*m[0x100+c.sp+2]+1
                for _ in range(60):
                    if c.pc==ret:break
                    c.step()
                else:raise AssertionError('KbInputs bank boundary')
                m[0xa000:0xc000]=bank;continue
            self.low=min(self.low,c.sp);assert m[c.pc]!=0,(entry,hex(c.pc));c.step()
        else:raise AssertionError(('CPU bound',entry,hex(c.pc)))
        assert c.sp==224;self.count+=1;return c,hits

def baseline(p):
    inhale=[]
    for age in range(9):
        m=p.make();p.enemy(m,0,356,184);m[p.s['KbActionAge']]=age;c,_=p.run(m,'KbBodyContact');inhale.append(bool(c.p&1))
    assert inhale==[True]+[False]*8
    misses=[]
    for sy in[196,197,200]:
        m=p.make();p.enemy(m,0,356,184)
        for n,v in dict(KbSavedSlot=0,KbShotType=3,KbShotKind=2,KbShotX=100,KbShotPage=1,KbShotY=sy).items():m[p.s[n]]=v
        _,hits=p.run(m,'KbWeapons::EnemyContacts');misses.append(bool(hits))
    assert misses==[True,False,False]
    velocity=[]
    for kind,direction in itertools.product([2,3],[1,2]):
        m=p.make();m[p.s['KbCopy']]=kind;m[p.s['PlayerFacingDir']]=direction;p.run(m,'KbWeapons::CopyAttack');velocity.append(m[p.s['KbShotVXHi']])
    assert velocity==[4,252,4,252]
    return dict(passed=True,opening_inhale_contact_C=inhale,ground_shell_centers=[196,197,200],ground_shell_hits=misses,shell_velocity=velocity,first_bad_conditions=['KbBodyContact startup ActionAge nonzero returns C0 before active mouth guard','EnemyContacts origin-radius25 excludes origin184 from shell197/200 despite native bbox198..204 overlapping shell center+-8'],native=False,actual_Main=False)

def main():
    p=Proof();r=dict(passed=True,source_CPU=True,native=False,actual_Main=False,baseline=baseline(p),CPU_cases=p.count,min_SP=p.low,
        bindings={str(x.resolve()):sha(x)for x in[Path(__file__),O/'current-witness.json',O/'current-kirby-code.bin',O/'baseline.bin',O/'baseline.dbg',O/'baseline-assembly.json']})
    (O/'baseline-negative.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='bindings'}))
if __name__=='__main__':main()
