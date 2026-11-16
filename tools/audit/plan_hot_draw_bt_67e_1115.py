"""Detached exact118-byte BT draw routing plan; no ROM/mounted overlay."""
from functools import lru_cache
from pathlib import Path
import json
import compose_bub_selected_star_palette_prince_1115 as Current
import replay_battletoads_attribution_7fb_1115 as Reference

R,ROM=Current.R,Current.ROM
W,N=Reference.W,Reference.N
PIN='67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
CURRENT_SHA='79699547d00efeb3e90d2fb321d0a9195f02b7e1e91965759a5f6c888df9aeaa'
FILE,BASE,SIZE=545972,0xb4a4,118
OLD_SHA='0991df9191ae7b3cf47a4c520515e5f91598d0004e4c57d80bebd09067fdd22e'
FOLLOW_SHA='0d651d53d3e24002ce7592c7a7a99081f5869329f48cf6c5ef77699a650d5a40'
UNIT=0x4020
H=Reference.C.digest


@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(Current.__file__).read_bytes())==CURRENT_SHA
    assert isinstance(raw,bytes)and H(raw)==PIN,'Expected exact owning67e input'
    old=Current.inverse(raw);assert H(old)==Reference.PIN
    assert raw[FILE:FILE+226]==old[FILE:FILE+226]
    # Bind transfer by the direct declared72-byte inverse, not an old model.
    owned=set(range(Current.FILE,Current.FILE+56))|set(range(Current.COOKIE,Current.COOKIE+16))
    assert len(owned)==72 and {i for i,(a,b)in enumerate(zip(raw,old,strict=True))if a!=b}<=owned
    return old


def load_current():
    raw=ROM.read_bytes();reference(raw);return raw


class Code:
    def __init__(self,base):self.base=base;self.data=bytearray();self.labels={};self.fix=[]
    def emit(self,text):self.data.extend(bytes.fromhex(text))
    def label(self,name):self.labels[name]=self.base+len(self.data)
    def branch(self,op,label):self.fix.append((len(self.data)+1,label,'rel',0));self.data.extend((op,0))
    def absolute(self,op,label,bias=0):self.fix.append((len(self.data)+1,label,'abs',bias));self.data.extend((op,0,0))
    def done(self):
        for at,label,kind,bias in self.fix:
            value=self.labels[label]+bias
            if kind=='rel':
                value-=self.base+at+1;assert -128<=value<=127
                self.data[at]=value&255
            else:self.data[at:at+2]=value.to_bytes(2,'little')
        return bytes(self.data)


def new_code(raw,base=BASE):
    reference(raw);old=raw[FILE:FILE+SIZE];assert H(old)==OLD_SHA
    table=bytearray(old[-27:]);assert all(table[i+1]==table[i+2]for i in(0,9,18))
    table[2]=0x26;table[11]=0xb0;table[20]=0xd7
    a=Code(base);a.label('Entry');a.emit('08488a489848a20cad0260c909');a.branch(0xd0,'Classify')
    a.emit('adeb5f');a.branch(0xd0,'Pick')
    a.label('Classify');a.emit('ad0260c914');a.branch(0xb0,'Default')
    a.emit('c90f');a.branch(0xb0,'Middle');a.emit('c90a');a.branch(0xd0,'Low')
    a.emit('ade55f2944c940');a.branch(0xf0,'Default')
    a.label('Low');a.emit('a20d');a.branch(0xd0,'Pick')
    a.label('Middle');a.emit('aa');a.branch(0xd0,'Pick')
    a.label('Default');a.emit('a214c921');a.branch(0xd0,'Pick');a.emit('a20e')
    a.label('Pick');a.absolute(0xbd,'Lo',-12);a.emit('8d6c01');a.absolute(0xbd,'Hi',-12);a.emit('8d6d01')
    a.absolute(0xbd,'Bank',-12);a.emit('8d620168a868aa688d6a01284c5d01')
    a.label('Lo');a.data.extend(table[:9]);a.label('Hi');a.data.extend(table[9:18]);a.label('Bank');a.data.extend(table[18:])
    code=a.done();assert len(code)==116
    return code+old[-2:],dict(a.labels),list(table)


def old_code(raw,base=BASE):
    reference(raw);out=bytearray(raw[FILE:FILE+SIZE]);assert H(out)==OLD_SHA
    if base!=BASE:
        readers=[]
        for index in range(91):
            if out[index]==0xbd and int.from_bytes(out[index+1:index+3],'little')in(0xb4ff,0xb508,0xb511):
                word=int.from_bytes(out[index+1:index+3],'little');out[index+1:index+3]=(base+word-BASE).to_bytes(2,'little');readers.append(index)
        assert len(readers)==3
    return bytes(out)


def descriptor(raw):
    old=old_code(raw);new,labels,table=new_code(raw)
    assert H(raw[FILE+SIZE:FILE+226])==FOLLOW_SHA
    differences=[i for i,(a,b)in enumerate(zip(old,new,strict=True))if a!=b]
    branches=[]
    # All conditional branches are within the89-byte instruction body.
    from py65.devices.mpu6502 import MPU
    from py65.disassembler import Disassembler
    memory=[0]*65536;memory[BASE:BASE+SIZE]=new;c=MPU(memory=memory);dis=Disassembler(c);pc=BASE
    while pc<labels['Lo']:
        size,text=dis.instruction_at(pc)
        if c.disassemble[memory[pc]][1]=='rel':
            delta=memory[pc+1];target=pc+2+(delta if delta<128 else delta-256)
            assert BASE<=target<labels['Lo'];branches.append(dict(PC=pc,target=target,hex=bytes(memory[pc:pc+size]).hex()))
        pc+=size
    assert pc==labels['Lo']
    return dict(owning_ROM_SHA256=PIN,reference7fb_SHA256=H(reference(raw)),direct72_inverse=True,
        file_half_open=[FILE,FILE+SIZE],physical_PRG_bank=66,CPU_half_open=[BASE,BASE+SIZE],
        old_SHA256=H(old),new_SHA256=H(new),old_hex=old.hex(),new_hex=new.hex(),changed_bytes=len(differences),
        code_bytes=89,data_bytes=27,retained_old_suffix_bytes=2,labels=labels,relative_branches=branches,
        old_rows=[dict(row=i,bank=old[109+i],PC=old[91+i]+256*old[100+i])for i in range(9)],
        new_rows=[dict(row=i,bank=table[18+i],PC=table[i]+256*table[9+i])for i in range(9)],
        repeated_Cd_rows1_2_share_original_CF_A8F0=True,new_raw33_public_target=dict(bank=215,PC=0xb026),
        ThShared_following108_SHA256=FOLLOW_SHA,Kb50_SHA256=H(raw[40924:40974]),
        all_other_bytes_not_composed_or_touched=True,no_ROM_image_composed=True,no_mounted_overlay=True,
        new_RAM_CHR_or_filler_lease_bytes=0,all_full_BtCheck_and_BtDraw_code_unchanged=True,
        proposal_only=True,ROM_native_or_delivery_authorized=False,outputs=0)


if __name__=='__main__':
    raw=load_current();q=descriptor(raw);q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
