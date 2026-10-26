"""Complete relocated segment bytes and emitted reference operand catalog."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def kv(line):return dict(q.split('=',1)for q in line.split('\t',1)[1].split(',')if'='in q)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    old,new=scoped_load(a.parent),scoped_load(a.candidate);expected=bytearray(old['raw']);tables=[]
    pairs={
        'Z2_GFX':[('Z2PoseLeft',27),('Z2PoseRight',27),('Z2ItemPtr',10),('Z2LateSmallRow',8)],
        'MIKE_GFX':[('JnBodyR',7),('JnBodyL',7),('JnShot0',13),('JnShot1',13),('JnItem',14),('JnShotAll',52)]}
    segs={q['name'].strip('"'):q for q in old['segs'].values()}
    moves=[('Z2_GFX',0x340),('MIKE_GFX',0x6c0),('BILL_ORBIT_2',0)]
    ranges=[]
    for name,delta in moves:
        seg=segs[name];lo=int(seg['ooffs'],0);n=int(seg['size'],0);start=int(seg['start'],0)
        target=next(q for q in new['segs'].values()if q['name'].strip('"')==name);dest=int(target['ooffs'],0)
        raw=bytearray(old['raw'][lo:lo+n])
        for pre,count in pairs.get(name,[]):
            l,h=location(old,pre+'Lo'),location(old,pre+'Hi')
            for i in range(count):
                v=old['raw'][l+i]+256*old['raw'][h+i];assert start<=v<start+n,(pre,i,v)
                w=v+delta;raw[l-lo+i]=w&255;raw[h-lo+i]=w>>8
                nl,nh=location(new,pre+'Lo'),location(new,pre+'Hi')
                assert new['raw'][nl+i]+256*new['raw'][nh+i]==w,(pre,i)
                tables.append(dict(name=pre,index=i,parent_pointer=v,relocated_pointer=w))
        assert bytes(raw)==new['raw'][dest:dest+n],('Non-pointer asset data changed',name)
        expected[lo:lo+n]=bytes([255])*n;expected[dest:dest+n]=raw
        ranges.append(dict(segment=name,old_offset=lo,new_offset=dest,bytes=n,table_entries=sum(z[1]for z in pairs.get(name,[])),all_nonpointer_bytes_exact=True))
    # Bank table has five intentional physical ownership changes. CPU address
    # and each vector byte remain fixed, including indexed page-cross costs.
    banktable=location(old,'BillFlareLoadLate::Banks')
    for i in range(29):
        oldbank=(location(old,f'BillFlareLate{i}')-16)//8192
        newbank=(location(new,f'BillFlareLate{i}')-16)//8192
        assert old['raw'][banktable+i]==oldbank and new['raw'][banktable+i]==newbank
        expected[banktable+i]=newbank
    changes=[i for i,(x,y)in enumerate(zip(expected,new['raw']))if x!=y]
    assert len(changes)==52,len(changes)
    # Bind every remaining code change to an actual emitted load instruction
    # span and a genuine moved data symbol, never an unrelated fake alias.
    spans=[];lines=[];files={}
    for line in a.parent.with_suffix('.dbg').read_text().splitlines():
        if line.startswith('span\t'):
            d=kv(line)
            if d.get('size')in ['2','3']and d.get('seg')in old['segs']and'ooffs'in old['segs'][d['seg']]:
                d['physical']=int(old['segs'][d['seg']]['ooffs'],0)+int(d['start'],0);spans.append(d)
        elif line.startswith('line\t'):lines.append(kv(line))
        elif line.startswith('file\t'):
            d=kv(line);files[d['id']]=d['name'].strip('"')
    spanlines={}
    for line in lines:
        for sp in line.get('span','').split('+'):
            if sp:spanlines.setdefault(sp,[]).append(dict(file=files.get(line.get('file')),line=int(line['line'])))
    moved=[]
    for name,s in old['syms'].items():
        if'seg'in s and old['segs'][s['seg']]['name'].strip('"')in ['Z2_GFX','MIKE_GFX']:
            moved.append((name,int(s['val'],0),int(new['syms'][name]['val'],0)))
    records=[];covered=set()
    for at in changes:
        if at in covered:continue
        choices=[]
        for sp in spans:
            first=sp['physical'];size=int(sp['size'])
            if not first<at<first+size:continue
            before=old['raw'][first:first+size];after=new['raw'][first:first+size]
            if before[0]!=after[0]:continue
            if size==3 and before[0]in [0xad,0xbd,0xb9,0xae,0xbe,0xac,0xbc]:
                x=before[1]+256*before[2];y=after[1]+256*after[2]
                matches=[n for n,v,w in moved if v==x and w==y]
                if matches:choices.append((sp,before,after,'absolute moved data',matches))
            if size==2 and before[0]in [0xa9,0xa2,0xa0]:
                matches=[n for n,v,w in moved if(v&255,w&255)==(before[1],after[1])or(v>>8,w>>8)==(before[1],after[1])]
                if matches:choices.append((sp,before,after,'immediate moved pointer byte',matches))
                if(before[1],after[1])in [(70|128,95|128),(97|128,95|128)]:
                    choices.append((sp,before,after,'immediate actual data bank',[]))
        assert choices,('Unclassified changed code operand',at,old['raw'][at-3:at+3].hex(),new['raw'][at-3:at+3].hex())
        sp,before,after,kind,matches=min(choices,key=lambda q:(q[3]!='absolute moved data',int(q[0]['size'])))
        first=sp['physical'];seg=old['segs'][sp['seg']];pc=int(seg['start'],0)+int(sp['start'],0)
        records.append(dict(physical_bank=(first-16)//8192,CPU=pc,parent_bytes=before.hex(),candidate_bytes=after.hex(),kind=kind,
                            matching_genuine_symbols=matches,source_locations=spanlines.get(sp['id'],[])))
        expected[first:first+len(after)]=after;covered.update(range(first,first+len(after)))
    assert expected==new['raw'],'An unaccounted ROM change remains'
    assert old['raw'][16+127*8192:16+128*8192]==new['raw'][16+127*8192:16+128*8192]
    proof=dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),
               entire_ROM_equals_only_declared_asset_moves_pointer_reassembly_and_real_load_references=True,
               complete_segments=ranges,internal_pointer_entries=len(tables),intentional_vector_bank_table_changes=5,
               other_reassembled_load_operand_bytes=len(changes),load_instruction_spans=len(records),fixed_DPCM_code_vectors_exact=True,CHR_exact=True,
               genuine_reference_catalog=records,checker_sha256=sha(__file__),
               limits='Complete binary/source reference accounting, plus separate assembled caller tests. No native PPU or cadence qualification.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'tables.json').write_text(json.dumps(tables,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='genuine_reference_catalog'},indent=2))
if __name__=='__main__':main()
