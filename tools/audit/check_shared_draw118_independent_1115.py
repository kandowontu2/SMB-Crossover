"""Independent current67 static HotDraw ingress/tail census; no CPU/image edit."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import check_ff_white_mushroom_current_1110 as W

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='67e3b8e7d4b01ea549fe9dc15c09b5a0b5f7085ee396d672a9c963d24287d0b5'
START,END,TAIL_END=0xb4a4,0xb51a,0xb586
FILE=545972
H=lambda v:sha256(v).hexdigest()
NEW=bytes.fromhex('08488a489848a20cad0260c909d005adeb5fd027ad0260c914b018c90fb011c90ad009ade55f2944c940f007a20dd00baad008a214c921d002a20ebdf1b48d6c01bdfab48d6d01bd03b58d620168a868aa688d6a01284c5d01ecf0269ec1e80dfaa2b0a8b0a5a6aaaaa3a1cfcfd7dde0dacdd9fcd9fc')


def listing(data,start,roots):
    memory=[0]*65536;memory[start:start+len(data)]=data
    cpu=MPU(memory=memory);decoder=Disassembler(cpu);todo=list(roots);seen={}
    while todo:
        pc=todo.pop()
        if pc in seen or not start<=pc<start+len(data):continue
        size,text=decoder.instruction_at(pc);op=memory[pc]
        assert op and not text.startswith('???'),(hex(pc),text)
        seen[pc]=dict(pc=pc,size=size,bytes=bytes(memory[pc:pc+size]).hex(),op=text)
        if op in(0x60,0x40):continue
        if op==0x4c:todo.append(memory[pc+1]+256*memory[pc+2]);continue
        assert op!=0x6c,('Unclosed indirect control',hex(pc))
        todo.append(pc+size)
        if cpu.disassemble[op][1]=='rel':
            delta=memory[pc+1];todo.append(pc+size+(delta if delta<128 else delta-256))
    return [seen[k]for k in sorted(seen)]


def census(raw):
    assert H(raw)==PIN
    body=raw[FILE:FILE+118];tail=raw[FILE+118:FILE+226]
    assert H(body)=='0991df9191ae7b3cf47a4c520515e5f91598d0004e4c57d80bebd09067fdd22e'
    assert len(tail)==108
    b=dict(W.Symbols.bundle(),raw=raw)
    assert H((R/'tools/audit/plan_hot_draw_bt_67e_1115.py').read_bytes())=='0bc656412e3c1a2d32bd4fea10ebb6574ceb81207d0d510a021d5536a35a197d'
    assert len(NEW)==118 and H(NEW)=='dd8cd717d8bb2f8e97a768e2b346d488060fd80d3d7bf56924cd460ca7a6b869'
    assert (W.address(b,'HotNewCharacterDraw'),W.location(b,'HotNewCharacterDraw'))==(START,FILE)
    assert W.address(b,'ThSharedDrawHot')==END
    symbols=[]
    for name,s in b['syms'].items():
        if'val'not in s:continue
        pc=int(s['val'],0)
        if not START<=pc<TAIL_END:continue
        try:at=W.location(b,name)
        except(KeyError,AssertionError):continue
        if FILE<=at<FILE+226:symbols.append(dict(name=name,pc=pc,file=at,size=s.get('size'),record=s))
    code=listing(body,START,[START])
    table=body[-27:]
    rows=[dict(row=i,bank=table[18+i],pc=table[i]+256*table[9+i])for i in range(9)]
    assert rows[1]==dict(row=1,bank=207,pc=0xa8f0)and rows[2]==dict(row=2,bank=207,pc=0xa8f0)
    bank=raw[16+66*8192:16+67*8192]
    # Complete same-bank word census includes data; list rather than silently
    # treating arbitrary matches as decoded instructions or pointer consumers.
    words=[]
    for i in range(8191):
        target=int.from_bytes(bank[i:i+2],'little')
        if START<=target<TAIL_END:
            pc=0xa000+i
            near=[(name,int(s['val'],0))for name,s in b['syms'].items()
                if'val'in s and'::'not in name and int(s['val'],0)<=pc]
            qualified=[]
            for name,point in near:
                if pc-point>512:continue
                try:at=W.location(b,name)
                except(KeyError,AssertionError):continue
                if(at-16)//8192==66:qualified.append((point,name))
            nearest=max(qualified)if qualified else None
            words.append(dict(word_pc=pc,target=target,context_pc=pc-4,
                context_hex=bank[max(0,i-4):i+7].hex(),nearest_global_symbol=nearest))
    prg=raw[16:1048592];far=[];absolute=[];triples=[]
    # Actual split immediate target publishers used by FarCallCommon. BankC2
    # is essential: the same16-bit PC in another mapped bank is not this code.
    for i in range(len(prg)-15):
        if prg[i]==0xa9 and prg[i+2:i+6]==bytes.fromhex('8d6c01a9')and prg[i+7:i+11]==bytes.fromhex('8d6d01a9'):
            target=prg[i+1]+256*prg[i+6]
            if prg[i+11]==0xc2 and START<=target<TAIL_END:
                far.append(dict(file=i+16,bank=i//8192,pc=0xa000+i%8192,target=target,bytes=prg[i:i+15].hex()))
        if prg[i]in(0x20,0x4c,0x6c):
            target=prg[i+1]+256*prg[i+2]
            if START<=target<TAIL_END:absolute.append(dict(file=i+16,bank=i//8192,pc=0xa000+i%8192,opcode=prg[i],target=target,
                same_mapped_bank_66=i//8192==66,raw_candidate_not_automatically_instruction=True))
        if prg[i+2]==0xc2 and START<=int.from_bytes(prg[i:i+2],'little')<TAIL_END:
            triples.append(dict(file=i+16,bank=i//8192,target=int.from_bytes(prg[i:i+2],'little'),layout='lo-hi-bank',raw_candidate=True))
    # Current actual byte targets; no new target is called or mounted here.
    targets=[]
    for tag,pc,n in((0xcf,0xa8f0,32),(0xd7,0xb026,3)):
        at=16+(tag&127)*8192+(pc&8191)
        targets.append(dict(tag=tag,pc=pc,file=at,bytes=raw[at:at+n].hex(),SHA256=H(raw[at:at+n])))
    def context(at):
        candidates=[]
        for name,s in b['syms'].items():
            if'val'not in s or'::'in name:continue
            try:here=W.location(b,name)
            except(KeyError,AssertionError):continue
            if(here-16)//8192==(at-16)//8192 and 0<=at-here<=1024:candidates.append((here,name))
        return dict(nearest_global_symbol=max(candidates)if candidates else None,
            context_file=at-6,context_hex=raw[at-6:at+10].hex())
    for row in triples:row.update(context(row['file']))
    for row in absolute:
        if row['target']in(START,END)and row['bank']!=66:
            row.update(context(row['file']))
            local_names=[]
            for name,s in b['syms'].items():
                if'val'not in s or int(s['val'],0)!=row['target']:continue
                try:at=W.location(b,name)
                except(KeyError,AssertionError):continue
                if(at-16)//8192==row['bank']:local_names.append(name)
            row['local_namespace_target_symbols']=local_names
    kinds={0xaabd:'LDA immediate highbyte B4, not pointer',0xab01:'LDA immediate highbyte B4, not pointer',
        0xb3c3:'JMP operand to protected HotPlayerGraphics helper B55E',
        0xb456:'LDA immediate highbyte B4, not pointer',0xb480:'LDA immediate highbyte B4, not pointer',
        0xb495:'JMP operand to protected Mini helper B57A',
        0xb4e2:'Only Lo table indexed-reader operand',0xb4e8:'Only Hi table indexed-reader operand',
        0xb4ee:'Only Bank table indexed-reader operand',0xb536:'LDA immediate highbyte B4, not pointer',
        0xb54a:'JMP operand to public HotNew entry B4A4',
        0xb598:'Relative branch operand plus following LDA zp,X opcode',
        0xb84e:'Relative branch operand plus following LDA zp,X opcode',
        0xb918:'JSR opcode plus low byte of target98B5',
        0xbc9a:'LDA abs,X opcode plus low byte of address04B4',
        0xbcfb:'LDA abs,X opcode plus low byte of address04B4',
        0xbd5f:'LDA abs,X opcode plus low byte of address04B4'}
    assert set(kinds)=={row['word_pc']for row in words}
    for row in words:row['instruction_boundary_classification']=kinds[row['word_pc']]
    new_listing=listing(NEW,START,[START]);newtable=NEW[89:116]
    expected=bytearray(table);expected[2]=0x26;expected[11]=0xb0;expected[20]=0xd7
    assert newtable==expected and NEW[116:]==body[-2:]
    new_readers=[]
    for row in new_listing:
        data=bytes.fromhex(row['bytes'])
        if data[0]==0xbd:
            base=int.from_bytes(data[1:3],'little')
            new_readers.append(dict(pc=row['pc'],indexed_base=base,effective_X12_through20=[base+12,base+21]))
    return dict(passed=True,owning_ROM_SHA256=PIN,static_only=True,CPU_executed=False,ROM_composed=False,
        body=dict(file=[FILE,FILE+118],pc=[START,END],SHA256=H(body),hex=body.hex(),reachable=code,records=rows),
        following_live108=dict(file=[FILE+118,FILE+226],pc=[END,TAIL_END],SHA256=H(tail),hex=tail.hex(),
            roots_symbols=symbols,listing=listing(tail,END,[END,0xb55e,0xb57a]+[x['pc']for x in symbols if x['pc']>=END])),
        complete_same_bank_word_candidates=words,split_immediate_C2_publishers=far,
        bank66_or_exact_public_absolute_control_candidates=[x for x in absolute if x['bank']==66 or x['target']in(START,END)],
        other_bank_raw_control_candidate_counts=dict(sorted(Counter(str(x['bank'])for x in absolute if x['bank']!=66 and x['target']not in(START,END)).items())),
        all_PRG_lo_hi_C2_candidates=triples,
        current_target_prefixes=targets,
        independently_measured_new118=dict(SHA256=H(NEW),bytes=118,instruction_bytes=89,table_bytes=27,
            table_pc=[0xb4fd,0xb506,0xb50f],retained_suffix=NEW[116:].hex(),
            table_readers=new_readers,reachable=new_listing,all_other_8_records_exact=True,
            only_repurposed_row=dict(row=2,bank=215,pc=0xb026),no_ROM_composition=True),
        limitations='Raw byte candidates require instruction/data and mapping classification; source split tables or generated decoded caches are not declared closed by a literal scan alone.',
        output_files=0,Mesen=False,plan_or_game_mutations=False)


if __name__=='__main__':
    raw=ROM.read_bytes();q=census(raw)
    text=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('RESULT '+text,flush=True);print('RECEIPT '+H(text.encode()),flush=True)
