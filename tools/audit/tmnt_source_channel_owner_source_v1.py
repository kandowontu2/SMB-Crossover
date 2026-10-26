"""Source-exact ACE8 channel owner: remove only redundant nonzero-X stack use."""
from pathlib import Path
import argparse
import difflib
import json
import re
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, sha, source_data

PARENT = 'd9d69ea1a8e6b4eee0f753fd4c33f9873f713a0bde35d2ce61c7ba24718dd523'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['parent', 'output']: p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    assert sha(a.parent/'candidate.nes') == PARENT
    assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    old = load(a.parent/'candidate.nes'); base = 16+63*8192
    assert old['raw'][base+0x2e0:base+0x300] == b'\xff'*32
    _, mem, cpu, dis, seen, words = source_data()
    callers = [pc for pc in seen if mem[pc] == 0x20 and mem[pc+1]+256*mem[pc+2] == 0x8ce8]
    assert sorted(callers) == [0x8744, 0x8a46, 0x8a91, 0x8c04, 0x8c18, 0x8d0c, 0x8f39]
    closure = []
    for pc in sorted(callers):
        incoming = []; roots = []
        for at in seen:
            width, _ = dis.instruction_at(at); op, mode = cpu.disassemble[mem[at]]
            if mode == 'rel':
                rel = mem[at+1]; tos = [at+width, at+width+(rel-256 if rel>=128 else rel)]
            elif op in ['JSR','JMP'] and mode == 'abs': tos = [mem[at+1]+256*mem[at+2]]
            elif op not in ['RTS','RTI','JMP','BRK']: tos = [at+width]
            else: tos = []
            incoming += [(at, to) for to in tos if pc <= to < pc+3]
        roots = [(at, mem[at]+256*mem[at+1]) for at in words if pc <= mem[at]+256*mem[at+1] < pc+3]
        assert all(to == pc for at, to in incoming+roots)
        closure.append(dict(original_PC=pc, runtime_PC=pc+0x2000, incoming=incoming, pointer_roots=roots))
    a.output.mkdir(parents=True); s = a.output/'source'
    shutil.copytree(a.parent/'source', s, ignore=shutil.ignore_patterns('__pycache__'))
    p = s/'src/tmnt-native.inc'; text = p.read_text(); assert text.count('  JSR $ace8\n') == len(callers)
    text = text.replace('  JSR $ace8\n', '.if ::TN_RAW_APU\n  JSR $ace8\n.else\n  JSR ::TnSourceChannelOwner\n.endif\n')
    p.write_text(text)
    body = '''; Same original channel selection, carry and final A/N/Z/V/D/I.
; X!=0 never changes A before PLA; ORA#0 supplies those exact original N/Z.
; The complete original X=0 branch retains its PHA/PLA and conditional carry.
.pushseg
.segment "TMNT_DURATION_HELPER"
.proc TnSourceChannelOwner
 cpx #0
 beq Zero
 ldx a:TnAudioRam+$93
 clc
 ora #0
 rts
Zero:
 pha
 lda a:TnAudioRam+$0e
 beq Clear
 sec
 pla
 rts
Clear:
 clc
 pla
 rts
.endproc
.assert TnSourceChannelOwner=$a2e0,lderror,"Verified last32B writer slack"
.assert *<=$a300,lderror,"Keep genuine duration products and note stream"
.export TnSourceChannelOwner
.popseg
'''
    (s/'src/tmnt_source_channel_owner.s').write_text(body)
    p=s/'src/tmnt_audio.s'; text=p.read_text(); anchor='.include "tmnt_parser_tail_writers.s"\n'; assert text.count(anchor)==1
    p.write_text(text.replace(anchor, anchor+'.include "tmnt_source_channel_owner.s"\n'))
    command=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    result=subprocess.run(command,cwd=s,capture_output=True,text=True)
    (a.output/'build.log').write_text(result.stdout+result.stderr); assert result.returncode==0,(result.stdout+result.stderr)[-5000:]
    new=load(a.output/'candidate.nes'); assert qualified(a.parent/'candidate.nes').items() <= qualified(a.output/'candidate.nes').items()
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    delta={n:sum(x!=y for x,y in zip(bank(old['raw'],n),bank(new['raw'],n)))for n in range(128)}; delta={n:v for n,v in delta.items()if v}
    assert set(delta)=={63} and old['raw'][:16]==new['raw'][:16] and old['raw'][1048592:]==new['raw'][1048592:]
    assert old['raw'][base+0xce8:base+0xcfb]==new['raw'][base+0xce8:base+0xcfb]
    assert all(new['raw'][base+pc+0x2000-0xa000:base+pc+0x2000-0xa000+3]==bytes([0x20,0xe0,0xa2])for pc in callers)
    manifest={};patch=''
    for name in ['src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_source_channel_owner.s']:
        p,q=a.parent/'source'/name,s/name
        manifest[name]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (a.output/'review.patch').write_text(patch)
    for filename in ['preparation.json','fast-preparation.json']:
        if (a.parent/filename).exists():
            prep=json.loads((a.parent/filename).read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
            (a.output/filename).write_text(json.dumps(prep,indent=2)+'\n')
    q=dict(prepared=True,source_only=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
           changed_PRG_bytes=delta,all_old_qualified_symbols_exact=True,helper_PC=address(new,'TnSourceChannelOwner'),helper_size=int(new['syms']['TnSourceChannelOwner']['size'],0),
           verified_FF_tail=[0xa2e0,0xa300],original_ACE8_body_and_raw_mode_exact=True,complete_original_instructions=len(seen),complete_original_pointer_words=len(words),
           replaced_real_direct_calls=closure,source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'channel-owner-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
