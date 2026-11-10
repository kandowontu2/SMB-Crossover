"""Genuine GameLoop FF/IRQ cuts for frozen WWF/FF manual native ingress."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_roster_input_1110 as I
import check_manual_roster_motion_1110 as Motion

P,N,R=I.P,I.N,I.R
PROOF=I.OUT/'leaf-proof.json'
SHA=lambda path:sha256(Path(path).read_bytes()).hexdigest()


def vectors(b,labels,axis,identities,scenarios):
    source=inspect.getsource(P.vectors).replace('def vectors(','def qualify(',1)
    source=source.replace('for owner in (41,34)','for owner in identities',1)
    source=source.replace("for scenario in ('birth','full','replacement'):",
                          'for scenario in scenarios:',1)
    source=source.replace('SavedJoypadBits=0x28, SavedJoypad1Bits=0x28',
                          f'SavedJoypadBits={axis}, SavedJoypad1Bits={axis}',1)
    source=source.replace("result = N.invoke(m,'ManualPlatform',y=0xf4 if owner==41 else 0xf8)",
        f"result = N.invoke(m,'ManualPlatform',x={0x42 if axis==0x24 else 0x41},y={24 if axis==0x24 else 248})",1)
    old="""                if tag == 3 and pc == (labels['MiniManualInput'] if owner == 41 else labels['KrManualIngress']):
                    inside = True
                if (tag,pc) == ((3,labels['MiniStep']) if owner == 41 else (2,0xdbf8)):
                    inside = False"""
    new="""                inside = (tag == 154 and (0xa959 <= pc < 0xab59 or 0xb134 <= pc < 0xb140)
                          or tag == 254 and 0x837b <= pc < 0x839a
                          or tag == 192 and (0xb378 <= pc < 0xb400 or 0xbfdd <= pc < 0xc000))"""
    assert source.count(old)==1
    source=source.replace(old,new,1)
    source=source.replace('m.vector_floor,m.written_stack = 0x100+z.sp,set()',
        'm.vector_floor,m.written_stack = 0x100+z.sp,set()\n        m.manual_irq_probe=True',1)
    source=source.replace('m.vector_floor = None\n        after = live(z)',
        'm.vector_floor = None\n        m.manual_irq_probe=False\n        after = live(z)',1)
    env=dict(P.__dict__)
    class Guard(P.StackGuard):
        manual_irq_probe=False
        def __getitem__(self,at):
            if self.manual_irq_probe and isinstance(at,int):
                assert at not in (0x73d1,0x73d2,0x73d3,0x73d7,0x73d9),('ISR helper state read',hex(at))
            return super().__getitem__(at)
    def snapshot(c,fn):
        probe=c.memory.manual_irq_probe;c.memory.manual_irq_probe=False
        try:return (*fn(c),bytes(c.memory[0x7382:0x73dd]))
        finally:c.memory.manual_irq_probe=probe
    def scene(bundle,identity):
        owner,variant=identity
        m=Motion.scene(bundle,owner,variant)
        m[0x73d1]=128;m[0x73d2]=m[0x73d3]=0
        N.put(m,CurrentPlayer=0)
        return m
    env.update(StackGuard=Guard,scene=scene,owned=I.W.D.owned,identities=identities,
        scenarios=scenarios,live=lambda c:snapshot(c,P.live),final=lambda c:snapshot(c,P.final))
    exec(source,env)
    return env['qualify'](b,labels)


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--axis',type=lambda x:int(x,0),choices=(0x28,0x24),required=True)
    cli.add_argument('--identity',help='Optional source probe owner:variant (22:0 or29:0 etc).')
    cli.add_argument('--pressure',action='store_true',help='Also cut full-slot and replacement branches.')
    a=cli.parse_args();q=json.loads(PROOF.read_text())
    assert q['passed'] and q['interrupt_pending'] and not q['native_ingress_pending']
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    base=I.BASE.read_bytes();assert I.SHA(base)==q['parent_SHA256']==I.PIN
    raw=P.install(base,q['patches']);assert I.SHA(raw)==q['expected_memory_only_SHA256']
    b=I.bundle(raw,q['labels'])
    identities=tuple((owner,variant) for owner,count in ((22,4),(29,6)) for variant in range(count))
    if a.identity:
        identity=tuple(map(int,a.identity.split(':')));assert identity in identities
        identities=(identity,)
    result=vectors(b,q['labels'],a.axis,identities,
        ('birth','full','replacement') if a.pressure else ('birth',))
    print('Genuine GameLoop manual vectors',result,flush=True)
    receipt=dict(passed=True,expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
        leaf_proof_SHA256=SHA(PROOF),axis=a.axis,identities=identities,
        genuine_GameLoop_GameCore_full_resumes=True,helper_SRAM_preserved=True,
        source_CPU_only=True,Mesen_run=False,vectors=result,
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),Path(Motion.__file__),Path(I.__file__),PROOF)})
    suffix=('V' if a.axis==0x28 else 'H')+('-'+a.identity.replace(':','-') if a.identity else '')+('-pressure' if a.pressure else '')
    (I.OUT/f'irq-{suffix}.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
