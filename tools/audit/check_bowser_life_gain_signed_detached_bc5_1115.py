"""Detached original/signed CPU cases and native INC/DEC counter boundaries."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import inspect,itertools,json
import check_bowser_life_gain_detached_bc5_1115 as OldCheck
import plan_bowser_life_gain_signed_bc5_1115 as Plan

OLD_CHECK_SHA='3c9422038141ea6b323f483843d69a6e0c3bdb25ee407b6d6aeaf5d192ed2851'

def boundaries(raw):
    b,before,after,row=Plan.proposal(raw);_,_,unsigned,oldrow=Plan.Previous.proposal(raw)
    address=lambda name:Plan.Current.W.address(b,name)
    fields={name:address(name)for name in('BwReady','BwPlayerKey','BwVariant','BwHP','BwTier','BwPersistent','CurrentPlayer','FmAlts','NumberofLives','BwEnsure','BwConstruct')}
    counts=0;negative=None;ctorcases=0
    class Memory(bytearray):
        def __setitem__(self,at,value):
            if isinstance(at,int)and hasattr(self,'writes'):self.writes.append((at,value))
            return super().__setitem__(at,value)
    for oldlife,delta,variant,player in itertools.product(range(256),(-1,1,7),(0,1),(0,1)):
        newlife=(oldlife+delta)&255;seed=bytearray(65536);seed[0xa000:0xc000]=before
        seed[0xbe00:0xbe40]=bytes((13*i+7)&255 for i in range(64));key=player*4
        for name,value in(('BwReady',0xb7),('BwPlayerKey',key),('BwVariant',variant),('BwHP',4 if variant else 33),('BwTier',2),
            ('CurrentPlayer',player),('FmAlts',variant*8),('NumberofLives',newlife)):seed[fields[name]]=value
        for member in(0,4):seed[fields['BwPersistent']+member:fields['BwPersistent']+member+4]=bytes((4 if variant else 33,2,oldlife,0xb7))
        seed[0x1dc]=255;seed[0x1dd]=0x5a;results=[]
        # The frozen unsigned case is exercised once as a retained negative.
        versions=(before,unsigned,after)if oldlife==0 and delta==-1 else(before,after)
        for version in versions:
            m=Memory(seed);m[row['start']:row['end']]=version[row['start']-0xa000:row['end']-0xa000]
            m.writes=[];c=Plan.NesMPU(memory=m,pc=fields['BwEnsure']);c.sp=219;c.a=169;c.x=109;c.y=135;c.p=0x71;ctors=0
            for _ in range(1000):
                if c.pc==0x5b00:break
                assert 0xa000<=c.pc<0xaa37
                if c.pc==fields['BwConstruct']:ctors+=1
                c.step()
            else:raise AssertionError('Counter-boundary primitive bound')
            results.append((m,(c.a,c.x,c.y,c.p,c.sp),ctors))
        original,signed=results[0],results[-1];saved=fields['BwPersistent']+2+key
        assert original[1]==signed[1]
        if delta<0:
            assert original[2]==signed[2]==1
            assert original[0].writes==signed[0].writes
            assert all(x==y for at,(x,y)in enumerate(zip(original[0],signed[0]))if not row['start']<=at<row['end'])
            ctorcases+=1
        else:
            assert signed[2]==0 and signed[0].writes==[(saved,newlife)]
            assert all(x==y for at,(x,y)in enumerate(zip(seed,signed[0]))if not row['start']<=at<row['end']and at!=saved)
        if len(results)==3:
            assert results[1][2]==0,'Unsigned rejection witness must show wrong missing constructor'
            negative=dict(old_lives=0,new_lives=255,original_Construct_calls=original[2],unsigned_Construct_calls=results[1][2],signed_Construct_calls=signed[2],
                unsigned_saved_life=results[1][0][saved],scope='Flat last-life DEC underflow; not gameplay')
        counts+=1
    assert negative
    return dict(passed=True,cases=counts,old_counts=256,steps=[-1,1,7],variants=2,players=2,
        real_death_paths_byte_and_ordered_write_exact=ctorcases,INC_wrap_preserves_tier_HP_pose=True,
        only_active_saved_life_written_on_gain=True,caller_AXYP_SP_exact=True,retained_unsigned_negative=negative,
        domain='Native per-update small INC/DEC deltas; actual last-life underflow0->FF and INCwrapFF->00 included')

def run(raw):
    assert sha256(Path(OldCheck.__file__).read_bytes()).hexdigest()==OLD_CHECK_SHA
    namespace=dict(OldCheck.__dict__);namespace['Plan']=Plan
    exec(compile(inspect.getsource(OldCheck.run),__file__+':original-scopes-signed-bytes','exec'),namespace)
    q=namespace['run'](raw);q['native_counter_boundaries']=boundaries(raw)
    q['receipt_SHA256']=Plan.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    raw=Plan.Current.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Detached boundary proof attempted output/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
