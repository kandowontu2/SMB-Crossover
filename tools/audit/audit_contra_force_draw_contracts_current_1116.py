"""Read-only draw/palette semantics and source capacity; no proposed bytes."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import argparse,json,re
import current_contra_force_readonly_9826_1116 as M

P,N,W,Frames=M.P,M.N,M.W,M.Frames
SOURCES={
 'build/contra-force-projectile-contact-1031-v3/kernel/p1-runtime.s':'e15911ff74498252b944ce25075ff80706214729197a0b0b219ab250247e2483',
 'build/contra-force-scroll-publisher-1031-v2/kernel/render.s':'ec13de394b343ff25413ee5dd19b44decda54beb6682d9ef432ecd4efa5ebf11',
 'build/contra-force-p1-kernel-v1/phase-bridge.s':'60eb976ec170b47881c0a8921ff74c0da8dbf91ddcb284b1679634796a03ec19',
 'build/contra-force-projectile-contact-1031-v3/kernel/runtime.cfg':'87cde222a35c4dede2a11d0202b16c3b87be9c1acd327ac79d4f4343616bc55d'}


def metadata(raw):
    q=M.bindings(raw);segments={};symbols=[]
    for line in(P.KERNEL/'runtime.dbg').read_text().splitlines():
        if line.startswith('seg\t'):
            row=P.fields(line);segments[int(row['id'])]=row
        elif line.startswith('sym\t'):symbols.append(P.fields(line))
    def symbol(name):
        matches={(int(s['val'],0),int(s['seg']))for s in symbols if s.get('name')==name and'val'in s and'seg'in s}
        assert len(matches)==1,(name,matches)
        pc,seg=matches.pop();row=segments[seg]
        if 'oname'in row:tag=int(row['oname'][3])
        else:
            # ld65 BSS symbols have no output file. CF_STATE is explicitly
            # assigned to the bank2 C2 MEMORY in the pinned runtime.cfg.
            assert row['name']=='CF_STATE'and row['type']=='rw'and int(row['start'],0)==0xc000
            assert 0xc000<=pc<0xc500
            tag=2
        return tag,pc
    return q,segments,symbols,symbol


def audit(raw):
    q,segs,syms,symbol=metadata(raw);texts={}
    for path,pin in SOURCES.items():
        data=(M.R/path).read_bytes()
        if pin:assert M.H(data)==pin,(path,'Changed retained source')
        texts[path]=data.decode()
    render=texts[next(p for p in texts if p.endswith('/render.s'))]
    p1=texts[next(p for p in texts if p.endswith('/p1-runtime.s'))]
    assert 'PlayerOutlinesOff'not in render and'PlayerOutlinesOff'not in p1
    assert all(s.get('name')!='PlayerOutlinesOff'for s in syms)
    assert 'CfRenderClip=CfState+$02fa'in render and'CfRenderTurn=CfState+$02fb'in render
    assert 'CfP1Visible=CfState+$02fa'in p1 and'CfP1Choice=CfState+$02fb'in p1
    assert 'sta CfRenderClip'in render and 'sta CfRenderTurn'in render
    assert 'cmp #240\n bcs Next'in p1 and'and #$e7\n sta Sprite_Data+2,x'in p1
    capacities=[];leads=[]
    for tag in(1,3):
        used=[s for s in segs.values()if s.get('oname')==f'ram{tag}.bin'and int(s.get('size','0'),0)>0]
        last=max(used,key=lambda s:int(s['ooffs'])+int(s['size'],0));end=int(last['ooffs'])+int(last['size'],0)
        limit=8192 if tag==1 else 8160
        assert end<=limit
        tail=q['carrier'][(tag-1)*8192+end:(tag-1)*8192+limit]
        assert tail==bytes([255])*len(tail)
        capacities.append(dict(physical_RAM=tag,last_loaded_segment=last['name'],last_loaded_PC_end=0xa000+end,
            candidate_code_half_open=[0xa000+end,0xa000+limit],bytes=len(tail),source='A1/A3 explicitly declared full8KB linker MEMORY; no later loaded DBG segment; exclude protected C3 trailer32',
            allocation=False,reader_ingress_closure_complete=False))
        # Conservative all-byte transfer leads, not a code-execution census.
        block=q['carrier'][(tag-1)*8192:tag*8192]
        for i in range(len(block)-2):
            if block[i]in(0x20,0x4c,0x6c):
                target=block[i+1]+256*block[i+2]
                if 0xa000+end<=target<0xa000+limit or 0xc000+end<=target<0xc000+limit:
                    leads.append(dict(physical_RAM=tag,PC=0xa000+i,opcode=block[i],target=target))
    recordRows=[]
    for family,count in(('Body',156),('Shot',123)):
        def table(name,n):
            tag,pc=symbol(name);at=(tag-1)*8192+(pc&8191);return tag,q['carrier'][at:at+n]
        bank,sizes=table('Cf'+family+'Bytes',count);_,lo=table('Cf'+family+'Lo',count);_,hi=table('Cf'+family+'Hi',count)
        attrs=Counter();end=0;xs=[];ys=[]
        for i,n in enumerate(sizes):
            pc=lo[i]+256*hi[i];at=(bank-1)*8192+(pc&8191);data=q['carrier'][at:at+n]
            assert n>0 and n%4==0 and len(data)==n;attrs.update(data[3::4]);end=max(end,(pc&8191)+n)
            xs.extend(v if v<128 else v-256 for v in data[1::4]);ys.extend(v if v<128 else v-256 for v in data[0::4])
        recordRows.append(dict(family=family,records=count,parts=sum(attrs.values()),bank=bank,record_end=0xa000+end,
            optional_outline_bit04_parts=sum(n for a,n in attrs.items()if a&4),tag18_parts=sum(n for a,n in attrs.items()if a&24),attributes=dict(attrs),
            source_part_bounds=dict(min_dx=min(xs),max_dx=max(xs),min_dy=min(ys),max_dy=max(ys)),maximum_parts_per_record=max(sizes)//4))
    names=('CfHostDraw','CfHostGraphics','CfHostPortrait','CfHostRenderAll','CfHostRenderBody','CfHostRenderShot','CfRenderRecord','CfRenderPart',
        'CfP1EarlyTag','CfP1LateEntry','CfP1Late','CfP1Packet','CfP1PacketGate','CfCallA','CfP1Visible','CfP1Choice','CfRenderClip','CfRenderTurn')
    points=[]
    for name in names:
        tag,pc=symbol(name);at=(tag-1)*8192+(pc&8191)
        refs=[]
        for s in syms:
            if s.get('name')==name and'ref'in s:refs.extend(map(int,s['ref'].split('+')))
        points.append(dict(name=name,tag=tag,PC=pc,first8=q['carrier'][at:at+8].hex(),DBG_symbolic_ref_count=len(set(refs))))
    return dict(passed=True,owning_SHA256=M.H(raw),binding=q['current_proof'],
        source_SHA256={p:M.H((M.R/p).read_bytes())for p in SOURCES},points=points,
        P1_is_palette_address_3F15_not_players=True,tag08='accepted CF loan-shot part',tag10='native actor part using palette1',
        visible_bits='1 loan shot /2 native, only rowsY<240; both toggles Turn',choice='0 native palette1 /1 loan colors; losers hidden; all64 attributes18 cleared',
        visible_alias=[0xc2fa,'CfRenderClip'],choice_alias=[0xc2fb,'CfRenderTurn'],private_renderer_has_no_outline_option_dependency=True,
        all_records=recordRows,capacity_leads=capacities,conservative_tail_control_leads=leads,
        no_code_arrays_CPU_ROM_native_or_allocation=True,outputs=0)


if __name__=='__main__':
    raw=M.load_current_image();reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=M.ROM.resolve(),'No second mutable ROM read'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only draw contract audit attempted output/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=audit(raw)
    out['receipt_SHA256']=M.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
