"""Measure semantics-preserving conditional-branch relaxation privately."""
import hashlib,json,re,subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-1102-v47'
P=R/'build/bubble-bobble-source-1101-v1'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
OPS={'jeq':'beq','jne':'bne','jmi':'bmi','jpl':'bpl','jcs':'bcs','jcc':'bcc','jvs':'bvs','jvc':'bvc'}

def main():
    O.mkdir(exist_ok=True);rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=rom.read_bytes();assert sha(rom)==PIN
    source=(P/'component.s').read_text();cfg=(P/'component.cfg').read_text();cc=R/'tools/Windows/cc65/bin'
    def assemble(text):
        (O/'component.s').write_text(text);(O/'component.cfg').write_text(cfg)
        for command in[[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'component.bin','-Ln',O/'component.lbl']]:
            p=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert p.returncode==0,p.stderr
        labels={name:int(at,16)for at,name in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',(O/'component.lbl').read_text(),re.M)}
        return(O/'component.bin').read_bytes(),labels
    old,oldlabels=assemble(source);assert oldlabels['BbCodeEnd']==0xb53a
    pages=[301,305,337,362,363,440,819,666]
    current=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
    assert current[0x100:0x153a]==old[0x100:0x153a]
    lines=source.splitlines();edits=[];iteration=0
    while True:
        _,labels=assemble('\n'.join(lines)+'\n');pending=[];previous=None
        for i,line in enumerate(lines):
            label=re.fullmatch(r'(BbOriginal_[0-9A-F]{4}):',line)
            if label:previous=label[1]
            branch=re.fullmatch(r' (j(?:eq|ne|mi|pl|cs|cc|vs|vc)) (BbOriginal_[0-9A-F]{4})(.*)',line)
            if branch:
                assert previous is not None
                offset=labels[branch[2]]-labels[previous]-2
                if -128<=offset<=127:pending.append((i,previous,branch[1],branch[2],branch[3],offset))
        if not pending:break
        for i,origin,opcode,target,comment,offset in pending:
            lines[i]=' '+OPS[opcode]+' '+target+comment
            at=oldlabels[origin]-0xa000
            was_long=old[at+1]==3 and old[at+2]==0x4c
            edits.append(dict(source_label=origin,target_label=target,original_macro=opcode,short_opcode=OPS[opcode],iteration=iteration,measured_offset=offset,original_was_long=was_long))
        iteration+=1;assert iteration<20
    code,labels=assemble('\n'.join(lines)+'\n');gain=oldlabels['BbCodeEnd']-labels['BbCodeEnd']
    long_count=sum(e['original_was_long']for e in edits)
    assert gain==3*long_count and gain>0,(gain,long_count,len(edits))
    # Each shortened branch consumes two bytes; actual encoded target must
    # equal the named relocated original label on both outcomes.
    for e in edits:
        at=labels[e['source_label']];operand=code[at-0xa000+1];delta=operand if operand<128 else operand-256
        assert at+2+delta==labels[e['target_label']]
        original=oldlabels[e['source_label']]-0xa000
        if e['original_was_long']:
            assert int.from_bytes(old[original+3:original+5],'little')==oldlabels[e['target_label']]
            assert code[at-0xa000]==old[original]^0x20
        else:
            assert code[at-0xa000]==old[original]
            d=old[original+1];assert oldlabels[e['source_label']]+2+(d if d<128 else d-256)==oldlabels[e['target_label']]
    q=dict(passed=True,proposal_only=True,ROM_written=False,installed=False,base_ROM_sha256=PIN,original_core_reproduced=True,original_core_bytes=5434,relaxed_conditional_branches=long_count,already_short_macros=len(edits)-long_count,reclaimed_bytes=gain,original_end=oldlabels['BbCodeEnd'],new_end=labels['BbCodeEnd'],iterations=iteration,edits=edits,scope='Actual admitted A100..B53A source component reproduced first. Only conditional macro inverse-branch-over-JMP is shortened to the corresponding relative branch when the final label target fits; encoded instruction targets/opcode pairs verified. This proves branch semantics, not whole-body/native/ISR equivalence. Native literal ingress addresses/imports/vectors/cookie have NOT been relinked; no cartridge emitted or pickup implemented.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),P/'component.s',P/'component.cfg',O/'component.s',O/'component.bin',O/'component.lbl']})
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['edits','bindings']}))

if __name__=='__main__':main()
