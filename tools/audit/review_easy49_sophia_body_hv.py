"""Bind real emulator calls, source geometry and single-bank relocation."""
from pathlib import Path
import collections
import csv
import hashlib
import importlib.util
import json
import sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-source-body-hs'
P=V/'agent-lsr-link-firebar-h/source'
G=V/'ryu49-head-status-bridge-g'
sys.path.insert(0,str(G))
s=importlib.util.spec_from_file_location('sophia_hv_bus',G/'check.py')
g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=D/'review-hv.json';assert not out.exists()
    prep=json.loads((D/'preparation.json').read_text())
    assert len(prep['source_sha256'])==444
    for n,h in prep['source_sha256'].items():assert sha(D/'source'/n)==h,n
    geometry=json.loads((D/'compiled-geometry-ht.json').read_text())
    assert geometry['status']=='PASS_COMPILED_RATIONAL_BODY_AND_FIREBAR_EDGES'
    report=dict(status='RUNNING',source_preparation_sha256=sha(D/'preparation.json'),
        script_sha256=sha(__file__),sources=444,geometry_sha256=sha(D/'compiled-geometry-ht.json'),maps=[],
        scope='Private normal Sophia body/consumer stage. Native bitmap/phase, positive contact equivalence, terrain head/side consumers and rotated source anchors remain open. No release or complete-route admission.')
    try:
        for mapper in ['mmc3','mmc5']:
            old=g.Image(P/'build'/('smb-crossover-'+mapper+'.nes'))
            im=g.Image(D/'source/build'/('smb-crossover-'+mapper+'.nes'))
            assert all(im.ram[n]==v for n,v in old.ram.items())
            assert old.raw[:16]==im.raw[:16] and old.raw[16+524288:]==im.raw[16+524288:]
            assert sha(D/'source/build'/('smb-crossover-'+mapper+'-baseline.nes'))==sha(P/'build'/('smb-crossover-'+mapper+'-baseline.nes'))
            unchanged={}
            for seg in old.segs.values():
                name=seg['name']
                if not seg.get('size')or'ooffs'not in seg:continue
                if any(x in name for x in ['AUDIO','MUSIC','DPCM','SMCCODE']) and name!='REMAINING_AUDIO':
                    new=next(x for x in im.segs.values()if x['name']==name)
                    assert (seg['start'],seg['size'],seg['ooffs'])==(new['start'],new['size'],new['ooffs']),name
                    assert old.raw[seg['ooffs']:seg['ooffs']+seg['size']]==im.raw[new['ooffs']:new['ooffs']+new['size']],name
                    unchanged[name]=seg['size']
            # Decode the unchanged Ryu procedures. Only internal absolute code
            # addresses may change with relocation; every other opcode/operand
            # is literal. No branch/data behavior can silently change here.
            first=old.sym('RyuSourceBodyBox')['val']
            last=old.sym('RyuSourceBodyPlatformFinish')['val']+old.sym('RyuSourceBodyPlatformFinish')['size']
            delta=im.sym('RyuSourceBodyBox')['val']-first
            c=CPU();relocations=[];instructions=0
            lengths={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'rel':2,'inx':2,'iny':2,'abs':3,'abx':3,'aby':3,'ind':3}
            for name in ['RyuSourceBodyBox','RyuSourceBodyPlatformBasic','RyuSourceBodyPlatformOverlap','RyuSourceBodyPlatformPrepare','RyuSourceBodyPlatformFinish']:
                a=old.hook(name);b=im.hook(name);size=old.sym(name)['size']
                assert size==im.sym(name)['size'] and b['address']-a['address']==delta
                assert b['physical_bank']==58
                before=old.raw[a['rom_offset']:a['rom_offset']+size]
                after=im.raw[b['rom_offset']:b['rom_offset']+size]
                expected=bytearray(before);i=0
                while i<size:
                    op=before[i];mnemonic,mode=c.disassemble[op];length=lengths[mode]
                    if op in [0x20,0x4c]:
                        target=before[i+1]+256*before[i+2]
                        if first<=target<last:
                            adjusted=target+delta
                            expected[i+1:i+3]=adjusted.to_bytes(2,'little')
                            relocations.append(dict(procedure=name,offset=i,opcode=mnemonic,old=target,new=adjusted))
                    i+=length;instructions+=1
                assert i==size and bytes(expected)==after,('Exact decoded algorithm relocation',mapper,name)
            # Link's scoped leaf remains byte-identical after its bank move.
            a=old.hook('EasyLinkFirebarStart');b=im.hook('EasyLinkFirebarStart')
            assert old.raw[a['rom_offset']:a['rom_offset']+184]==im.raw[b['rom_offset']:b['rom_offset']+184]
            folder=D/('native-hp-'+mapper)
            binding=json.loads((folder/'binding.json').read_text())
            actual=json.loads((folder/'actual.json').read_text())
            assert actual['exit']==0 and actual['result']=={'cases':46,'failures':0}
            for n,h in actual['files'].items():assert sha(folder/n)==h,n
            assert binding['ROM']['rom']['sha256']==sha(im.path)
            events=list(csv.DictReader((folder/'events.csv').open()))
            writes=list(csv.DictReader((folder/'writes.csv').open()))
            calls=[];interrupted=[]
            for cid,case in enumerate(binding['cfg']['cases'],1):
                rows=[x for x in events if int(x['case'])==cid]
                pre=next(x for x in rows if x['event']=='FirebarCollision-native-piece')
                post=next(x for x in rows if x['event']=='FirebarCollision-return')
                ws=[x for x in writes if int(x['case'])==cid]
                if any(int(x['depth'])for x in ws):
                    interrupted.append(cid);continue
                before=(folder/f'{cid:02d}-pre.bin').read_bytes();after=(folder/f'{cid:02d}-post.bin').read_bytes()
                registers=[int(pre[n])for n in ['A','X','Y','P','SP']]
                banks={0x8000:62,0xa000:0,0xc000:before[g.at(im.ram['CurrentBankC'])]&127,0xe000:63}
                got=g.execute(im,CPU,before,registers,banks,int(pre['PC']),int(post['PC']),native_status=True)
                assert got['regs']==[int(post[n])for n in ['A','X','Y','P','SP','PC']],('Native registers',mapper,cid)
                assert got['ram']==after,('Native all10240RAM',mapper,cid)
                assert [(x[2],x[4])for x in got['trace']]==[(int(x['address']),int(x['value']))for x in ws],('Native every ordered write',mapper,cid)
                assert after[0x101+registers[4]:0x200]==before[0x101+registers[4]:0x200],('Live caller stack',mapper,cid)
                calls.append(dict(case=cid,name=case['name'],cycles=got['cycles'],writes=len(ws),all10240RAM=True,allRegisters=True))
            report['maps'].append(dict(mapper=mapper,ROM=im.metadata(),all_old_RAM_names=len(old.ram),
                audio_DPCM_SMC_literal=unchanged,baseline_exact=True,header_CHR_exact=True,
                Ryu_decoded_instructions=instructions,Ryu_exact_absolute_relocations=relocations,
                unchanged_Link_leaf184=True,native46=actual['result'],strict_calls=calls,interrupted_gaps=interrupted,
                actual_receipt_sha256=sha(folder/'actual.json')))
            out.write_text(json.dumps(report,indent=2)+'\n')
        report['status']='PASS_PRIVATE_BODY_STAGE_STATIC_NATIVE_AND_RELOCATION'
    except Exception as exc:
        report.update(status='FAIL_RETAINED',error=str(exc));raise
    finally:out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],maps=[dict(mapper=x['mapper'],strict_calls=len(x['strict_calls']),interrupted=x['interrupted_gaps'])for x in report['maps']])))


if __name__=='__main__':main()
