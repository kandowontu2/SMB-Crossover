"""Strict graphics-only inverse and actual new-cookie cold transport."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,struct
import compose_prince_window567_1115 as C
import check_prince_natural_sword_1113 as Game
import check_bub_current_budget_1113 as Frames
N,W=Game.N,Game.W


def cold(raw):
    assert C.digest(raw)==C.CANDIDATE
    with patch.object(Game,'proof_parent',lambda image:raw if image==raw else (_ for _ in()).throw(AssertionError('Wrong graphics image'))):
        return Game.cold(raw)


def transport(raw):
    head,chunks,lengths=C.Packet.extract(raw);fields=struct.unpack_from('<12H',head,len(head)-54)
    wrap=bytes.fromhex('c9dcd008a9808503a9c28504');assert head[C.Packet.LOADER:].count(wrap)==1
    stages=[dict(start=fields[i],dest=fields[i+1],packed=fields[i+2],size=fields[i+3])for i in(0,4,8)]
    active=None;owner=None;results=[];published=[];bus=W.ControllerBus;cpu=N.NesMPU
    def finish():
        assert active['cursor']==len(active['addresses'])and active['written']==active['size']
        results.append(dict(stage=active['stage'],packed_bytes=active['cursor'],decoded_bytes=active['written'],
            every_output_byte_exact=True,minimum_unread_margin=active['margin']))
    class Bus(bus):
        def __getitem__(self,key):
            if self is owner and active is not None and isinstance(key,int):
                index=active['cursor'];addresses=active['addresses']
                if index<len(addresses)and key==addresses[index]:active['cursor']+=1
            return super().__getitem__(key)
        def __setitem__(self,key,value):
            if self is owner and active is not None and isinstance(key,int)and 0<=key-active['dest']<active['size']:
                unread=active['indices'].get(key)
                if unread is not None:
                    assert unread<active['cursor'],'Unread compressed input overwritten'
                    active['margin']=min(active['margin'],active['cursor']-unread)
                i=key-active['dest'];count=active['written']
                if count<active['size']:
                    assert i==count and value==chunks[active['stage']][i],('Actual decoder output differs',active['stage'],i)
                    active['written']+=1
            return super().__setitem__(key,value)
    class CPU(cpu):
        def step(self):
            nonlocal active,owner
            m=self.memory
            if self.pc==0xc000 and m.rawtags[2]==2:
                owner=m
                if active is not None:finish()
                stage=len(results);assert stage<3;spec=stages[stage];start=spec['start'];count=spec['packed'];end=min(start+count,0xdc00)
                addresses=list(range(start,end))+list(range(0xc280,0xc280+count-(end-start)))
                assert len(addresses)==len(set(addresses))==count
                active=dict(spec,stage=stage,addresses=addresses,indices={a:i for i,a in enumerate(addresses)},cursor=0,written=0,margin=65536)
            if self.pc==0xbbc1 and m.rawtags[1]==3:
                if active is not None:finish();active=None
                assert len(results)==3
                cookie=raw[C.Packet.COOKIE:C.Packet.COOKIE+16]
                assert all(bytes(m.ram[bank][0x1fe0:0x1ff0])==cookie for bank in(2,3))
                for row in C.allocation()['decoded_envelopes']:
                    bank=3 if row['stream']==0 else 2;lo=(0xa000 if bank==3 else 0xc800)+row['offset']
                    assert bytes(m.ram[bank][lo&8191:(lo&8191)+row['bytes']])==chunks[row['stream']][row['offset']:row['offset']+row['bytes']]
                if not published:published.append(dict(PC=self.pc,SP=self.sp,full16byte_cookie_before_first_renderer=True,three_graphics_extents_read_back=True))
            return super().step()
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):
        m,opening=cold(raw)
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert len(results)==3 and published
    return m,dict(opening=opening,actual_decoder_stages=results,before_first_graphics_publication=published,
        warm_whole_Main_returns=8,scope='Actual new-ROM compiled menu/parser/cold; peripheral unit lacks physical vblank cadence')


def run(parent,*,source=False):
    attempts=[]
    def deny(*args,**kwargs):attempts.append('write or launch');raise AssertionError('Read-only candidate proof')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw,info=C.proposal(parent);C.inverse.cache_clear();C.proposal.cache_clear()
        reader=Path.read_bytes
        def read(path,*args,**kwargs):
            assert path.resolve()!=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').resolve(),'Mutable nightly reread'
            return reader(path,*args,**kwargs)
        with patch.object(Path,'read_bytes',read):assert C.inverse(raw)==parent
        rejects=[]
        for name,fn,image in(('parent_as_candidate',C.inverse,parent),('candidate_as_parent',C.proposal,raw),
            ('candidate_truncated',C.inverse,raw[:-1]),('dirty_parent',C.proposal,parent[:100]+bytes([parent[100]^1])+parent[101:]),
            ('dirty_candidate',C.inverse,raw[:100]+bytes([raw[100]^1])+raw[101:])):
            try:fn(image)
            except AssertionError:rejects.append(name)
            else:raise AssertionError('Unknown input accepted')
        q=dict(passed=True,composition=info,portable_inverse_actual_owning_parent=True,mutable_Downloads_rereads=0,
            unknown_input_rejections=rejects,write_or_launch_attempts=attempts,outputs=0,Mesen=False)
        if source:_,q['actual_new_ROM_transport']=transport(raw)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');args=parser.parse_args()
    print(json.dumps(run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),source=args.source),separators=(',',':')),flush=True)
