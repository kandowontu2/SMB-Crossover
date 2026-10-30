"""Execute both assembled queue validators over valid and invalid PPU commands."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from verify_native_relocation import NesMPU


def main():
    out=ROOT/'build/menu-fourth-row-fix-v2/queue-controls.json';assert not out.exists()
    folders=[ROOT/'build/pit-retold-host-v3',out.parent]
    images=[]
    for folder in folders:
        labels={name:int(value,16)for value,name in re.findall(r'^al ([\dA-Fa-f]+) \.(\w+)$',(folder/'candidate.lbl').read_text(),re.M)}
        raw=(folder/'candidate.nes').read_bytes();m=[0]*65536
        m[0xa000:0xc000]=raw[16+66*8192:16+67*8192]
        images.append((m,labels))
    changes=[];cases=0
    for hi in range(256):
      for lo in [0,0x10,0x22,0x28,0x46,0xff]:
       for count in [1,3,16,20]:
        outcomes=[]
        for m,L in images:
            offset=L['VRAM_Buffer1_Offset'];base=offset+1
            m[offset]=count+3;m[base:base+count+4]=[hi,lo,count]+[0x24]*count+[0]
            c=NesMPU(memory=m,pc=L['MenuQueueValidate']);c.sp=253;c.stPushWord(0x5aff)
            for _ in range(500):
                if c.pc==0x5b00:break
                assert m[c.pc]!=0,'Unexpected BRK in validator';c.step()
            assert c.pc==0x5b00 and c.sp==253
            outcomes.append(bool(c.p&1))
        expected_change=hi==0x22 and count==1
        if expected_change:
            assert outcomes==[False,True],(hi,lo,count,outcomes)
            changes.append(dict(high=hi,low=lo,count=count,before=False,after=True))
        else:assert outcomes[0]==outcomes[1],(hi,lo,count,outcomes)
        cases+=1
    proof=dict(passed=True,source_CPU_only=True,cases=cases,only_changed_accepted_commands=changes,
        findings='Only six tested fourth-row cursor commands change from rejected to accepted; all other6138 tested command shapes retain original results.',
        bindings={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),
            *[d/n for d in folders for n in ['candidate.nes','candidate.lbl']]]})
    out.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=cases,changed=len(changes))))


if __name__=='__main__':main()
