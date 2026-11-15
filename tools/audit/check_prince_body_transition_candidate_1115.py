"""Exact16a composition/inverse and real cold decoder, no mounted arrays."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,struct
import compose_prince_body_transition_590_1115 as C
import check_prince_natural_sword_1113 as Game
import check_bub_current_budget_1113 as Frames

N,W=Game.N,Game.W


def cold(raw):
    assert C.digest(raw)==C.CANDIDATE
    with patch.object(Game,'proof_parent',lambda image:raw if image==raw else (_ for _ in()).throw(AssertionError('Wrong actual16a image'))):
        return Game.cold(raw)


def transport(raw):
    head,chunks,sizes=C.Packet.extract(raw);grant=C.allocation();fields=struct.unpack_from('<12H',head,len(head)-54)
    stages=[dict(start=fields[i],dest=fields[i+1],packed=fields[i+2],size=fields[i+3])for i in(0,4,8)]
    active=None;owner=None;pending=None;results=[];consumers={};published=[]
    native_bus=W.ControllerBus;native_cpu=N.NesMPU
    def finish():
        nonlocal active
        assert active['cursor']==active['packed']and active['written']==active['size']
        results.append(dict(stage=active['stage'],packed_bytes=active['cursor'],decoded_bytes=active['written'],
            every_output_byte_exact=True,minimum_unread_margin=active['margin']))
        active=None
    def compare(m,row):
        stream=row['stream'];lo,hi=row['decoded_half_open'];bank=3 if stream==0 else 2
        origin=0xa000 if stream==0 else 0xc800 if stream==1 else 0xc0b0
        at=(origin+lo)&8191;actual=bytes(m.ram[bank][at:at+hi-lo])
        assert actual==chunks[stream][lo:hi]and C.digest(actual)==row['proposed_SHA256']
    class Bus(native_bus):
        def __getitem__(self,key):
            if self is owner and active is not None and isinstance(key,int):
                i=active['cursor'];addresses=active['addresses']
                if i<len(addresses)and key==addresses[i]:active['cursor']+=1
            return super().__getitem__(key)
        def __setitem__(self,key,value):
            if self is owner and active is not None and isinstance(key,int)and 0<=key-active['dest']<active['size']:
                unread=active['indices'].get(key)
                if unread is not None:
                    assert unread<active['cursor'],'Unread compressed input overwritten'
                    active['margin']=min(active['margin'],active['cursor']-unread)
                i=key-active['dest'];count=active['written']
                if count<active['size']:
                    assert i==count and value==chunks[active['stage']][i],('Actual new decoder output differs',active['stage'],i)
                    active['written']+=1
            return super().__setitem__(key,value)
    class CPU(native_cpu):
        def step(self):
            nonlocal active,owner,pending
            m=self.memory
            if m is owner and pending==(self.pc,self.sp):finish();pending=None
            if self.pc==0xc000 and m.rawtags[2]==2:
                owner=m;assert active is None and pending is None
                stage=len(results);assert stage<3;spec=stages[stage];start=spec['start'];count=spec['packed'];end=min(start+count,0xdc00)
                addresses=list(range(start,end))+list(range(0xc280,0xc280+count-(end-start)))
                assert len(addresses)==len(set(addresses))==count
                active=dict(spec,stage=stage,addresses=addresses,indices={a:i for i,a in enumerate(addresses)},cursor=0,written=0,margin=65536)
                ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                pending=(ret,(self.sp+2)&255)
            if m is owner:
                for index,row in enumerate(grant['decoded_spans']):
                    bank=3 if row['stream']==0 else 2;origin=0xa000 if bank==3 else 0xc800 if row['stream']==1 else 0xc0b0
                    entry=origin+row['decoded_half_open'][0]
                    if self.pc in((entry,entry+3)if index==0 else(entry,))and m.rawtags[(self.pc-0x8000)//8192]==bank:
                        compare(m,row)
                        consumers.setdefault(index,dict(PC=self.pc,SP=self.sp,exact_before_first_execution=True,SHA256=row['proposed_SHA256']))
                if self.pc==0xbbc1 and m.rawtags[1]==3 and not published:
                    assert active is None and pending is None and len(results)==3
                    cookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16]
                    assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in(2,3))
                    for row in grant['decoded_spans']:compare(m,row)
                    for row in C.Plan.Current.Graphics.allocation()['decoded_envelopes']:
                        stream=row['stream'];bank=3 if stream==0 else 2;origin=0xa000 if bank==3 else 0xc800
                        lo=row['offset'];size=row['bytes'];at=(origin+lo)&8191
                        assert bytes(m.ram[bank][at:at+size])==chunks[stream][lo:lo+size]
                    published.append(dict(PC=self.pc,SP=self.sp,complete_candidate_cookies=True,all_three_candidate_extents_exact=True,
                        all_preserved_graphics3174_plus3_plus2_exact=True,no_source_array_mounts=True))
            return super().step()
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):
        m,opening=cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(results)==3 and len(consumers)==3 and published
    return m,dict(opening=opening,actual_decoder_stages=results,before_first_consumers=consumers,
        before_first_graphics_publication=published,warm_whole_Main_returns=8,
        scope='Actual newly encoded16a compiled cold/menu/parser; source peripheral lacks physical vblank/native cadence')


def run(parent,*,source=False):
    attempts=[]
    def deny(*args,**kwargs):attempts.append('write or launch');raise AssertionError('Read-only candidate proof')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=C.proposal(parent);C.inverse.cache_clear()
        reader=Path.read_bytes
        def read(path,*args,**kwargs):
            assert path.resolve()!=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').resolve(),'Mutable nightly reread'
            return reader(path,*args,**kwargs)
        with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent
        assert C.proposal(C.inverse(raw))[0]==raw
        rejects=[]
        for name,fn,image in(('parent_as_candidate',C.inverse,parent),('candidate_as_parent',C.proposal,raw),
            ('candidate_truncated',C.inverse,raw[:-1]),('parent_truncated',C.proposal,parent[:-1]),
            ('dirty_parent',C.proposal,parent[:100]+bytes([parent[100]^1])+parent[101:]),
            ('dirty_candidate',C.inverse,raw[:100]+bytes([raw[100]^1])+raw[101:]),
            ('olderAE',C.proposal,C.Plan.Current.Graphics.inverse(parent))):
            try:fn(image)
            except AssertionError:rejects.append(name)
            else:raise AssertionError('Unknown input accepted')
        q=dict(passed=True,composition=info,portable_inverse_exact590=True,forward_inverse_byte_equality=True,
            compact_preimage_compressed_bytes=len(bytes.fromhex(C.ORIGINAL_ZLIB_HEX)),mutable_Downloads_rereads=0,
            unknown_input_rejections=rejects,write_or_launch_attempts=attempts,outputs=0,Mesen=False)
        if source:_,q['actual_new_ROM_transport']=transport(raw)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',action='store_true');args=p.parse_args()
    print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),source=args.source),separators=(',',':')),flush=True)
