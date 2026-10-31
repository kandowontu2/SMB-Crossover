"""Use the unchanged live33SMC/stack checker at every new consumer site."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_peach_vectors_1031_v1.py';text=prior.read_text()
    old='M,B=P.M,P.B'
    new="P.O=R/'build/smb3plus-peach-gravity-consumer-1031-v1';P.J=P.O/'joint'\nM,B=P.M,P.B"
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace("O/'movement-controls-v1.json'","O/'regressions-v1.json'")
    text=text.replace("O/'graphics-controls-v2.json'","O/'regressions-v1.json'")
    text=text.replace("('form5_graphics',0,False)","('form5_graphics',0,False),('big_jump',0,False),('leaf_hover',34,False),('tanooki',0,False),('sink_direct',0,False)")
    old="else P.peach_seed(b)"
    new="else P.peach_seed(b,form=1 if name=='big_jump' else 3 if name=='leaf_hover' else 5 if name=='tanooki' else 0)"
    assert text.count(old)==1;text=text.replace(old,new)
    old="        held=q.get('SavedJoypadBits')"
    new="""        if name=='sink_direct':
            q.set('M3Native::Player_SandSink',1);q.put(MbFloatReady=2)
            q.m.page(2,91);q.set('CurrentBankC',0xdb)
        held=q.get('SavedJoypadBits')"""
    assert text.count(old)==1;text=text.replace(old,new)
    text=text.replace("label='M3Graphics' if name=='form5_graphics' else 'M3Movement'",
        "label='M3Graphics' if name=='form5_graphics' else 'MbPeachAfterJump' if name=='sink_direct' else 'M3Movement'")
    text=text.replace("-{'MbPeachFloatSink'}",'-set()')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_actual_gravity_vectors'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
