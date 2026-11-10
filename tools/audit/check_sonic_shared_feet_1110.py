"""Source-funded current shared feet adapter; RAM/stdout only."""
from collections import Counter
import argparse
from hashlib import sha256
import json
import sys

import check_sonic_native_effects_aligned_1110 as Aligned
import check_wwf_native_powerups_1110 as Parent

W,N,L=Parent.W,Parent.N,Parent.L
sys.path.insert(0,str(W.R/'tools/reference'))
import sonic_sms_compact_cold_worker_1110 as Asm

SOURCE=W.R/'tools/reference/sonic_shared_feet_1110.s'
off=lambda bank,pc:16+bank*8192+(pc&8191)
SECTIONS={'HEAD':(127,0xe45b,15),'FOOT':(127,0xe46a,45),'SIDE':(127,0xe497,3),
          'DEFAULT':(65,0xbc93,44),'UNION':(65,0xbfb0,40),'SH_TAIL':(65,0xac10,5)}


def proposal(raw):
    fixed=raw[off(127,0xe45b):off(127,0xe49a)]
    assert fixed==bytes.fromhex('8d6a01a9e38d6c01a9b98d6d01a9854c5a01ad0260c904f010c90bf00cc916f008c91af004c91cd00fa9e78d6c01a9b68d6d01a9bf4c5a014c8695ea4ce490')
    assert raw[off(65,0xbc93):off(65,0xbcbf)]==bytes.fromhex('ad0260c91cf022c90bd00cc01fd0082c0f6b10034c86958d6a01a98f8d6c01a9a68d6d01a9c74c5a014cbfbc')
    assert raw[off(65,0xbfb0):off(65,0xbfd8)]==bytes.fromhex('ad02608d6a01c916f031c91af0034c93bc8d6a01a9778d6c01a9b88d6d01a9988d620168684c6101')
    assert raw[off(5,0xb9e3):off(5,0xb9e3)+2]==bytes.fromhex('a900')
    assert raw[off(71,0xa68f):off(71,0xa68f)+3]==bytes.fromhex('ad0260')
    assert raw[off(24,0xb877):off(24,0xb877)+6]==bytes.fromhex('c8a9004c7fb8')
    assert raw[off(65,0xb0f5):off(65,0xb0f5)+3]==bytes.fromhex('4c40a7')
    sh,_=Aligned.E.S.Funding.assemble()
    assert raw[off(65,0xabd5):off(65,0xac10)]==sh
    assert raw[off(65,0xac10):off(65,0xac15)]==bytes([0xea])*5
    assert raw[off(65,0xac15):off(65,0xac1d)]==bytes.fromhex('f7f8f90581818182')
    p=Asm.assemble(SOURCE.read_text(),{name:(pc,size)for name,(_,pc,size)in SECTIONS.items()})
    assert p['symbols']['SonicLow']==0xbfcf and p['symbols']['SonicHigh']==0xbcb6
    assert p['symbols']['Gimmick']==0xbfc2
    image=bytearray(raw);patches=[]
    for name,(bank,pc,size)in SECTIONS.items():
        new=p['images'][name];assert len(new)==size,(name,len(new),size)
        at=off(bank,pc);image[at:at+size]=new;patches.append(dict(bank=bank,pc=pc,bytes=size,section=name))
    relocations={0xe46d:0xe46a}
    refs={}
    for old,new in relocations.items():
        matches=[i for i in range(16,1048590)if raw[i:i+2]==old.to_bytes(2,'little')]
        assert matches and all(raw[i-1]in(0x20,0x4c)for i in matches),(hex(old),matches)
        for at in matches:image[at:at+2]=new.to_bytes(2,'little')
        refs[hex(old)]=matches
    # The only whole-word E496 matches are unrelated data, not references.
    # The unused source-declared side veneer moves to E497; preserve data.
    sidewords=[i for i in range(16,1048590)if raw[i:i+2]==bytes.fromhex('96e4')]
    assert sidewords==[358452,693168]
    assert not any(raw[i-1]in(0x20,0x4c)for i in sidewords)
    assert bytes.fromhex('a9968d6c01a9e48d6d01')not in raw[16:1048592]
    for at in sidewords:assert image[at:at+2]==raw[at:at+2]
    assert image[off(65,0xbfd8):off(65,0xc000)]==raw[off(65,0xbfd8):off(65,0xc000)]
    return bytes(image),dict(parent_SHA256=sha256(raw).hexdigest(),image_SHA256=sha256(image).hexdigest(),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),sections=patches,retargeted_operands=refs,
        unused_side_source_symbol_rebind=[0xe496,0xe497],unrelated_side_word_matches_preserved=sidewords,
        funding='Dead incoming-A publications/duplicate LDA/JMP-next; equivalent standard nested Gimmick FarCall; qualified Sh5 tail',
        preserved_DK_FF_helper_and_export=[0xbfd8,0xc000])


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--qualify',action='store_true');a=cli.parse_args()
    raw,program,p=Aligned.proposal();image,record=proposal(raw)
    result=qualify_existing(raw,image) if a.qualify else None
    print(json.dumps(dict(passed=True,source_only=True,output_files=0,ROM_written=False,
        record=record,existing_profiles=result,
        scope='Current-profile qualification is optional; raw43 common admission/full getter and its header guard remain separately required.')),flush=True)


def call(mem,pc,y=0,flags=0x31,observe=None):
    mem[0x16a]=85;mem[0x16c]=pc&255;mem[0x16d]=pc>>8
    c=N.NesMPU(memory=mem,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=255,71,y,flags,224;c.stPushWord(0x5aff)
    W.clear_logs(mem);L.finish(mem,c,(0x5b00,224),observe)
    return c


def qualify_existing(raw,image):
    old=W.Symbols.bundle();old['raw']=raw
    inventory=Parent.C.Starts.C.inventory(raw);rows=Counter();samples={};names=[];minimum=224
    for row in inventory['rows']:
        if row['raw']not in (4,11,22,26,28,32)and not(row['slot']==0 and row['cycle']==0):continue
        _,seed=Parent.C.cold(old,row);names.append(row['name'])
        for y in (0,1,30,31,32):
            for flags in (0x31,0xf5):
                pairs=[]
                for index,rom in enumerate((raw,image)):
                    m=L.clone(seed);m.bundle=dict(m.bundle,raw=rom)
                    for page,tag in enumerate(m.rawtags):
                        if tag&128:m.raw_page(page,tag)
                    N.put(m,R0=167,R1=90,Local_eb=y,NmiDisable=255)
                    def observe(mem,cpu):
                        nonlocal minimum
                        if not index:return
                        if row['raw']==26 and cpu.sp<minimum:
                            minimum=cpu.sp;samples['DEEPEST_GIMMICK']=L.clone(mem,cpu)
                        if cpu.pc<0x8000:return
                        tag=mem.rawtags[(cpu.pc-0x8000)//8192]
                        section=next((name for name,(bank,start,size)in SECTIONS.items()
                            if tag==(bank|128)and start<=cpu.pc<start+size),None)
                        if section and section not in samples:samples[section]=L.clone(mem,cpu)
                    c=call(m,0xe46d if not index else 0xe46a,y,flags,observe)
                    pairs.append((L.regs(c),L.app(m)))
                assert pairs[0]==pairs[1],(row['name'],y,hex(flags),'shared feet ABI/state')
                rows['actual_cold_profile_feet_pairs']+=1
        if row['raw']==11:
            for y in (0,3,6,31):
                pair=[]
                for rom in(raw,image):
                    m=L.clone(seed);m.bundle=dict(m.bundle,raw=rom)
                    for page,tag in enumerate(m.rawtags):
                        if tag&128:m.raw_page(page,tag)
                    c=call(m,0xe45b,y,0x31);pair.append((L.regs(c),L.app(m)))
                assert pair[0]==pair[1]
                rows['actual_Sophia_head_tail_pairs']+=1
    assert 'SH_TAIL'in samples and 'UNION'in samples
    vectors=Counter()
    for section,(state,cpu)in samples.items():
        for kind in('NMI','IRQ'):
            m,c=L.clone(state,cpu);n,d=L.clone(state,cpu);n.bundle=dict(n.bundle,raw=raw)
            for page,tag in enumerate(n.rawtags):
                if tag&128:n.raw_page(page,tag)
            def protected(mem,z):
                body,shared=L.body(mem);shared=bytearray(shared)
                if kind=='NMI' and N.get(mem,'SelectedCharacter')==26:
                    # Existing GmNmiClock intentionally advances these three
                    # declared fields on the genuine outer-NMI audio path.
                    for name in('GmClock','GmFresh','GmPrevious'):
                        at=W.address(mem.bundle,name);assert 0x5c37<=at<0x5c3a
                        shared[at-0x5c00]=0
                return L.regs(z),bytes(mem[3:11]),bytes(mem[0x15a:0x17b]),bytes(mem[0x101+z.sp:0x200]),body,bytes(shared)
            before=protected(m,c)
            left=L.isr(m,c,kind);right=L.isr(n,d,kind)
            assert left==right and protected(m,c)==before,(section,kind,'ISR live state')
            exact=lambda mem,z:(L.regs(z),L.app(mem),mem.vram,mem.chr_latches,mem.upper,mem.ppu_log,mem.writes)
            assert exact(m,c)==exact(n,d),(section,kind,'paired original ISR')
            # Resume the new foreground after either identical native ISR.
            n.bundle=dict(n.bundle,raw=image)
            for page,tag in enumerate(n.rawtags):
                if tag&128:n.raw_page(page,tag)
            L.finish(m,c,(0x5b00,224));L.finish(n,d,(0x5b00,224))
            assert (L.regs(c),L.app(m))==(L.regs(d),L.app(n))
            vectors[kind+'_'+left]+=1
    return dict(names=names,cases=dict(rows),representative_sections=sorted(samples),minimum_Gimmick_foreground_SP=minimum,
        actual_paired_ISR=dict(vectors),no_Mesen=True,
        scope='Directed getter/head callbacks from actual current menu/cold/60-update seeds, plus real paired ISRs at changed transport sections; no natural Sonic movement claim.')


if __name__=='__main__':main()
