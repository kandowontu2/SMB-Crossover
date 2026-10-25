"""Single-cell weapon/block contacts, page carries and protected terrain."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,re,sys
R=Path(__file__).resolve().parents[2]
O=R/'build/verification/cv3-blocks-mt'
P=O/'cv3-blocks-v3.nes'

def main():
    sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
    s=importlib.util.spec_from_file_location('mt_cpu',R/'build/player-guide-agent/check_mmc5_expand.py')
    g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
    l=g.labels(P)
    for line in (R/'src/cv3_state.inc').read_text().splitlines():
        if m:=re.match(r'(\w+)\s*=\s*\$([0-9a-f]+)',line):l[m[1]]=int(m[2],16)
    c=g.make(P,l);m=c.memory;smc=bytes(m.ram[0x15a:0x1f0])
    def w(n,v,i=0):m.ram[l[n]+i]=v&255
    def r(n,i=0):return m.ram[l[n]+i]
    def reset():
        m.ram[:]=bytes(65536);m.ram[0x15a:0x15a+len(smc)]=smc;m.banks=[126,84,83,127]
        for n,v in dict(CurrentBank=212,CurrentBankC=211,SelectedCharacter=5,GameEngineSubroutine=8,PlayerFacingDir=1,Player_X_Position=80,Player_PageLoc=3,Player_Y_Position=176,Player_Y_HighPos=1,Player_Y_Speed=3,ObjectOffset=4).items():w(n,v)
        m.ram[0x5fe7]=1
    def call(n):return g.execute(c,l[n])
    points=0
    for x,page,width,face in itertools.product(range(256),range(2),(12,20),(1,2)):
        reset();w('Cv3RectX',x);w('Cv3RectPage',page);w('Cv3RectW',width);w('Cv3RectY',160);w('PlayerFacingDir',face)
        call('Cv3MeleeBlocks')
        expected=x+page*256+(width-1 if face==1 else 0)
        assert r('MmProbeX')+256*r('MmProbePage')==expected,(x,page,width,face)
        assert r('MmProbeY')==164;points+=1
    protected=contacts=0
    for char,variant,tile,foundation,full in itertools.product((5,),range(1,4),(0,0x23,0x26,0xc2,0xc3,0xc1,0x51,0x52,0x54,0x10),range(2),range(2)):
        reset();m.ram[0x5fe7]=variant;w('Block_Buffer_1',tile,166);w('MmSolidTerrain',foundation,166)
        w('Block_Buffer_1',0xc1,165);w('Block_Buffer_1',0xc1,167)
        if full:w('Block_State',1);w('Block_State',1,1)
        w('MmProbeX',104);w('MmProbePage',0);w('MmProbeY',192)
        names=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','PlayerSize','CrouchingFlag','Player_Y_Speed','ObjectOffset']
        before={n:r(n) for n in names}
        call('Cv3BlockPoint')
        assert all(r(n)==v for n,v in before.items()),(variant,tile,foundation,full,before,{n:r(n) for n in names})
        assert r('Block_Buffer_1',165)==r('Block_Buffer_1',167)==0xc1,'No neighboring cell activation'
        mutable=tile in (0xc1,0x51) or (tile==0x52 and not foundation)
        if not mutable or full:
            assert r('Block_Buffer_1',166)==tile,(variant,tile,foundation,full);protected+=1
        else:
            assert r('Block_Buffer_1',166)!=tile,(variant,tile,foundation,full);contacts+=1
    report=dict(passed=True,sha256=hashlib.sha256(P.read_bytes()).hexdigest(),leading_edge_page_cases=points,protected_or_full_pool_cases=protected,exact_target_cell_activations=contacts,native_player_and_object_state_preserved=True,neighbor_questions_unchanged=True)
    (O/'cpu-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
