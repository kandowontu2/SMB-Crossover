"""Lossless dictionary search for the unchanged qualified Prince decoder.

The frozen codec already parses tokens optimally for each fixed dictionary.
This source-only tool searches dictionary choices; it writes no output files.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import json
import re

import check_prince_native_foot_motion_1110 as Foot

C,N,I=Foot.C,Foot.N,Foot.I


class Optimizer:
    def __init__(self,data):
        self.data=data;self.matches=[];positions=defaultdict(list);self.cache={}
        for i in range(len(data)):
            best=(0,0)
            for at in reversed(positions[data[i:i+3]]):
                distance=i-at
                if distance>4095:break
                n=0
                while n<18 and i+n<len(data) and data[at+n]==data[i+n]:n+=1
                if n>best[0]:best=n,distance
                if n==18:break
            self.matches.append(best);positions[data[i:i+3]].append(i)

    def parse(self,dictionary,full=False):
        key=frozenset(dictionary)
        if not full and key in self.cache:return self.cache[key]
        lookup=[False]*256
        for v in dictionary:lookup[v]=True
        n=len(self.data);cost=[0]*(n+1);choice=[1]*n if full else None
        for i in range(n-1,-1,-1):
            value=(6 if lookup[self.data[i]] else 10)+cost[i+1];step=1
            longest=self.matches[i][0]
            if longest>=3:
                options=cost[i+3:i+longest+1];best=min(options)+17
                if best<value:
                    value=best
                    if full:step=options.index(best-17)+3
            cost[i]=value
            if full:choice[i]=step
        self.cache[key]=cost[0]
        return (cost[0],choice) if full else cost[0]

    def encode(self,dictionary):
        assert len(dictionary)==len(set(dictionary))==16
        bits,choice=self.parse(dictionary,True);lookup={v:i for i,v in enumerate(dictionary)}
        output=[]
        def emit(value,n):output.extend((value>>b)&1 for b in range(n))
        i=0
        while i<len(self.data):
            size=choice[i]
            if size==1:
                emit(0,1);value=self.data[i]
                if value in lookup:emit(1,1);emit(lookup[value],4)
                else:emit(0,1);emit(value,8)
            else:
                distance=self.matches[i][1]
                emit(1,1);emit(distance&255,8);emit(((distance>>8)<<4)|(size-3),8)
            i+=size
        assert len(output)==bits
        result=bytearray(dictionary)
        for off in range(0,len(output),8):result.append(sum(v<<b for b,v in enumerate(output[off:off+8])))
        return bytes(result)

    def search(self,initial,name,rounds=5):
        assert self.encode(list(initial[:16]))==initial
        current=list(initial[:16]);best=self.parse(current);history=[]
        universe=[v for v,_ in Counter(self.data).most_common()]
        # Every possible literal value can replace one dictionary slot.
        for epoch in range(rounds):
            candidate=None;cost=best
            for slot in range(16):
                for incoming in universe:
                    if incoming in current:continue
                    trial=current[:];trial[slot]=incoming
                    value=self.parse(trial)
                    if value<cost:cost=value;candidate=trial
            history.append(dict(round=epoch,bits=cost,bytes=16+(cost+7)//8,evaluations=len(self.cache)))
            print('DICTIONARY_SEARCH '+json.dumps(dict(chunk=name,**history[-1])),flush=True)
            if candidate is None:break
            current,best=candidate,cost
        return self.encode(current),dict(history=history,one_swap_local_optimum=candidate is None,
            dictionary=current,evaluations=len(self.cache))


def actual_decoder(data,packed,dest):
    path=C.P.V.O
    decoder=(path/'cold-decoder-v25.bin').read_bytes()
    labels={name.lstrip('.'):int(value,16) for value,name in
        re.findall(r'^al ([0-9a-fA-F]+) (\S+)$',(path/'cold-decoder-v25.lbl').read_text(),re.M)}
    assert len(decoder)==254
    memory=[0]*65536;memory[0xc000:0xc000+len(decoder)]=decoder
    memory[0x8000:0x8000+len(packed)]=packed
    for label,value,off in (('PpLdLoad',0x8000,1),('PpLdRemain',len(data),0)):
        at=labels[label]+off;memory[at:at+2]=value.to_bytes(2,'little')
    memory[3:5]=dest.to_bytes(2,'little')
    cpu=N.NesMPU(memory=memory,pc=labels['PpLdDecode']);cpu.sp=224;cpu.y=0
    cpu.stPushWord(0x5ffe)
    for count in range(2000000):
        if cpu.pc==0x5fff:break
        assert memory[cpu.pc]!=0,hex(cpu.pc)
        cpu.step()
    else:raise AssertionError('actual decoder bound')
    assert cpu.sp==224 and bytes(memory[dest:dest+len(data)])==data
    return dict(instructions=count,CPU=cpu.processorCycles,bytes_exact=len(data),
        decoder_SHA256=sha256(decoder).hexdigest(),output_SHA256=sha256(data).hexdigest())


def main():
    raw=Foot.F.Exit.ROM.read_bytes();assert C.digest(raw)==Foot.F.Exit.PIN
    bundle=C.Start.W.bundle(raw);seed,_=C.P.Q.C.C.cold(bundle,38)
    original,_,state=C.P.Q.source_images();seed=Foot.apply(seed)
    rt=bytearray(seed.ram[3][:len(original)]);rt[0x1fa3:0x1fd8]=original[0x1fa3:0x1fd8]
    chunks=[bytes(rt),bytes(seed.ram[2][0x800:0x1fcc]),state]
    rows=[]
    for name,data,dest in zip(('runtime','metadata','state'),chunks,(0xa000,0xc800,0xc100)):
        initial=C.P.Q.M.CODEC.encode(data)
        optimizer=Optimizer(data);packed,search=optimizer.search(initial,name)
        roundtrip=actual_decoder(data,packed,dest)
        row=dict(name=name,old_bytes=len(initial),new_bytes=len(packed),saved=len(initial)-len(packed),
            search=search,actual_decoder=roundtrip)
        rows.append(row);print('CHUNK_RESULT '+json.dumps(row),flush=True)
    print('TOTAL '+json.dumps(dict(saved=sum(r['saved'] for r in rows),
        new_bytes=sum(r['new_bytes'] for r in rows),required_saving=64,ROM_written=False,rows=rows)),flush=True)


if __name__=='__main__':main()
