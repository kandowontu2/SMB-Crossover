"""Detached pickup compaction/constructor ABI and existing native menu units."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import json
import plan_prince_sword_tier2_1115 as Plan
import check_prince_native_tier2_primitives_1115 as Units
from verify_native_relocation import NesMPU

def execute(blob,entry,seed,*,oracle_flags=0x20):
    memory=seed[:];memory[0xc7b3:0xc800]=blob
    # Declared flat service oracles exercise the pickup's required transport:
    # SetAction may clobber A/X/flags; native call ignores incoming A/flags.
    for at in(0xaa51,0x8d2f,0x98b5,0xda1b):memory[at]=0x60
    cpu=NesMPU(memory=memory);cpu.pc=entry;cpu.sp=0xdf;cpu.a=0x93;cpu.x=seed[0xc050];cpu.y=0;cpu.p=0x21
    memory[0x1e0:0x1e2]=(0xfe,0x7f);events=[]
    for _ in range(300):
        if cpu.pc==0x7fff:break
        if cpu.pc in(0xaa51,0x8d2f,0x98b5,0xda1b):
            pc=cpu.pc
            if pc==0xaa51:
                events.append(('action',cpu.a,cpu.y));cpu.a=0xff;cpu.x=182;cpu.p=oracle_flags
            elif pc==0x8d2f:events.append(('erase',cpu.x))
            elif pc==0x98b5:events.append(('score',cpu.a,cpu.x))
            else:events.append(('native',cpu.x,cpu.y));cpu.a=17;cpu.p=oracle_flags|1
        cpu.step()
    else:raise AssertionError('Flat pickup did not return')
    assert cpu.pc==0x7fff and cpu.sp==0xe1 and cpu.p&1
    return memory,cpu,events

def detached(raw):
    _,parts,_,rows,labels=Plan.arrays(raw);old,new=rows[1]['old'],rows[1]['new'];counts=Counter();maxcycles=0
    for slot in range(6):
      for hp in(0,1,4,5):
       for kind in(0,1,2,3,127,128,254,255):
        for state in(0,0x80,0xc0):
         for tier in(0,1,2):
          seed=[0]*65536;seed[0xc050]=slot;seed[0xc6cf]=hp;seed[0x34+slot]=kind;seed[0x1f+slot]=state
          seed[0x75b]=tier;seed[0xc6ee]=2 if kind&1 else 0
          a,ca,ea=execute(old,0xc7b3,seed);b,cb,eb=execute(new,0xc7b3,seed)
          assert ea==eb and ca.x==cb.x and ca.y==cb.y
          # Retired stack bytes contain relocated JSR return PCs. The active
          # caller stack above the entry SP must remain exact.
          allowed={*range(0xc7b3,0xc800),*range(0x100,0x1e0),0x75b}
          diff=[at for at,(x,y)in enumerate(zip(a,b))if x!=y and at not in allowed]
          assert not diff,(slot,hp,kind,state,tier,diff[:12])
          accepted=hp>0 and kind<2 and state&0x80
          expected=(2 if kind==1 else max(1,tier))if accepted else tier
          assert b[0x75b]==expected
          counts['cases']+=1;counts['accepted_Flower'if accepted and kind==1 else'accepted_Mushroom'if accepted else'unchanged_native_or_rejected']+=1
          maxcycles=max(maxcycles,cb.processorCycles)
    # HostInit's unchanged original body is bypassed only in this flat suffix
    # primitive. The real caller overwrites A/N/Z immediately after HostInit.
    ctor=[]
    suffix=rows[0]['new'][-10:-1]
    assert suffix==bytes.fromhex('ad5b074a8deec63860')
    for tier in(0,1,2):
      for initial in(0,1,2):
        memory=[0]*65536;memory[0xc000:0xc009]=suffix;memory[0x75b]=tier;memory[0xc6ee]=initial
        cpu=NesMPU(memory=memory);cpu.pc=0xc000;cpu.x=0xff;cpu.y=0;cpu.sp=0xdf;cpu.p=0xe0;memory[0x1e0:0x1e2]=(0xfe,0x7f)
        for _ in range(8):
            if cpu.pc==0x7fff:break
            cpu.step()
        assert cpu.pc==0x7fff and memory[0xc6ee]==tier//2 and cpu.x==0xff and cpu.y==0 and cpu.p&1
        ctor.append(dict(tier=tier,before=initial,Sword=memory[0xc6ee]))
    # Decode every external absolute instruction candidate to either public
    # entry. Raw word aliases are retained as a census, not called ingress.
    words=[]
    for stream,part in enumerate(parts):
      for at in range(len(part)-1):
        target=int.from_bytes(part[at:at+2],'little')
        if 0xc7b3<=target<0xc800 or target==0xc0b0:
            words.append(dict(stream=stream,offset=at,target=target,context=part[max(0,at-1):at+4].hex()))
    return dict(passed=True,scope='Explicit flat CPU primitives with declared service oracles; not gameplay or mounted code',
        pickup_cases=dict(counts),ctor_suffix_cases=ctor,max_pickup_cycles=maxcycles,external_word_census=words,
        source_classifier='Type LSR carries bit0 through LDA Enemy_State/BPL; types>=2 branch native. NativeCall overwrites incoming A/P before dispatch.',
        public_carry_set=True,public_XY_preserved=True,actor_and_other_native_state_exact=True,
        outputs=0,Mesen=False,gameplay_mounts=0)

def menu(raw):
    N,W=Units.N,Units.W
    bundle=dict(W.Symbols.bundle(),raw=raw);prior=N.Bus;N.Bus=W.ControllerBus
    try:m=W.UI.seed(bundle,29)
    finally:N.Bus=prior
    W.UI.key(m,32);assert N.get(m,'SelectedCharacter')==38
    N.put(m,PlayerStatus=2,CrossoverMenuState=1,DisableScreenFlag=1,Mirror_PPUMASK=0,VRAM_Buffer1_Offset=0)
    m.ppumask=0
    before=N.get(m,'PlayerStatus');result=N.invoke(m,'CrossoverMenuInput',a=0,x=0,y=0,p=0x21)
    after=N.get(m,'PlayerStatus');assert before==2 and after==0
    return dict(passed=True,before=before,after=after,result=result,
        scope='Actual compiled menu screen-entry component; source bus lacks real vblank. Native full UI remains separate.')

if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Tier2 detached checker attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();q=detached(raw);q['menu']=menu(raw)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
