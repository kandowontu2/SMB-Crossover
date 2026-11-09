"""Bind old successful native controllers to the exact offscreen constructor code."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile

from check_helper_camera_admission_1110_v1 import DP_LEFTS, DP_TICK, TH_LEFTS, bank_at
from check_mini_funded_actor_1108_v3 import install
from prepare_selected_native_packet_v1 import R, prepare, sha


OBSERVER = R / 'tools/reference/helper_camera_constructor_observer_1110_v1.lua'
THOMAS = R / 'build/thomas-current-candidate-1102-v3/native-six-lifts/controller.lua'
GOKU = R / 'build/goku-current-last-gap-1108/controller.lua'
KARNOV = R / 'docs/qa/checkpoints/2026-11-02/karnov-full11-v6/inputs.zip'
KARNOV_MEMBER = 'build/karnov-crouch-route-1102-v1/native-stair/controller.lua'
KARNOV_SHA = '776b98638773c91cfe9e9554959f29523469d090aba1c03d71bcfb3a818742cf'
ACTORS = ('thomas','goku','karnov')
POLICIES = [
    R / 'tools/playthroughs/dragon_power_11_current_1108.lua',
    R / 'build/goku-gap-1102-v4/policy.lua',
    R / 'build/goku-source-route-1102-v3/policy.lua',
    R / 'tools/playthroughs/full_roster_policy_og.lua',
    *(R / f'tools/playthroughs/dragon_power_11_v{i}.lua' for i in range(3,8)),
]


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old,new)


def goku(text, raw):
    # Old policy v4 read the second platform through the single slot and
    # assumed the same tag as v7's first. Keep its controller thresholds.
    text=once(text,'  b=choose(c)',"""  c.r=function(name,index)
   if c.x>=800 and name=='HpActorSlot' and index==nil then return r(name,1)end
   local value=r(name,index)
   if c.x>=800 and name=='HpActorOwner' and value==0x84 then return 0x83 end
   return value
  end
  b=choose(c)""")
    text=once(text,' if done then return end;done=true;inputFile:close()',
              ' if done then return end;passed,why=helperCameraFinish(passed,why);done=true;inputFile:close()')
    for label in ('GameLoopOwned','NmiEntry','NmiReturn','IrqEntry','IrqReturn','DmaComplete'):
        match=re.search(r'\["'+label+r'"\]=\{\["pc"\]=(\d+),\["banks"\]=\{([\d,]+)\},'
                        r'\["bytes"\]=\{([\d,]+)\}',text)
        assert match,label
        pc=int(match[1]); expected=bytes(map(int,match[3].split(',')))
        for bank in map(int,match[2].split(',')):
            at=bank_at(bank,pc)
            assert raw[at:at+len(expected)]==expected,(label,bank,hex(pc))
    return text


def lua_list(values):
    return '{'+','.join(map(str,values))+'}'


def controller(raw, expected, proof, character):
    assert proof['passed']
    for patch in proof['patches']:
        at=patch['file_offset']; wanted=bytes.fromhex(patch['new_hex'])
        assert raw[at:at+len(wanted)]==wanted,patch['role']
    refs=[Path(__file__),OBSERVER]
    if character=='thomas':
        text=THOMAS.read_text()
        refs.append(THOMAS)
        owner,tag,pc,y,lefts,pipes=10,3,0xb341,192,TH_LEFTS,(448,608,736,912,2608,2864)
        text=once(text,' if done then return end\n if ok then',
                  ' if done then return end\n ok,reason=helperCameraFinish(ok,reason)\n if ok then')
    else:
        at=bank_at(26,DP_TICK)
        worker=raw[at:bank_at(26,proof['symbols']['DpPlatformEnd'])]
        marker=bytes.fromhex('a982205a01a60d')
        assert worker.count(marker)==1
        tag,pc,y,lefts,pipes=154,DP_TICK+worker.index(marker)+2,208,DP_LEFTS,(736,912)
        if character=='goku':
            owner=24
            text=goku(GOKU.read_text(),raw)
            refs.extend([GOKU,*POLICIES])
        else:
            owner=34
            assert sha(KARNOV)==KARNOV_SHA
            with ZipFile(KARNOV) as archive:
                text=archive.read(KARNOV_MEMBER).decode()
            refs.append(KARNOV)
            text=once(text,'   trace:close();shot(\'stage-endpoint\')',
                      '   won=helperCameraFinish(won,won and "Reached active1-2" or '
                      '(dead and "Natural death" or "Controller deadline"))\n'
                      '   trace:close();shot(\'stage-endpoint\')')
    # Karnov's historical receipt lacks an inline ROM pin; the observer
    # and the launcher bind it independently. The other sources include one.
    if character!='karnov':
        text,replacements=re.subn(r'(?<==")[0-9a-f]{64}(?=")',expected,text,count=1)
        assert replacements==1
    prefix=OBSERVER.read_text()+(
        f'\nlocal helperCameraFinish=helperCameraObserver{{owner={owner},tag={tag},pc={pc},'
        f'y={y},lefts={lua_list(lefts)},pipes={lua_list(pipes)},sha="{expected}"}}\n'
    )
    return prefix+text,refs


def packet(rom, expected, output, proof_path, character):
    raw=rom.read_bytes()
    assert sha(rom)==expected
    proof=json.loads(proof_path.read_text())
    text,refs=controller(raw,expected,proof,character)
    scope=('Cold controller-only 1-1 into active 1-2. Require actual offscreen constructor '
           'relative left edge 256–287, reciprocal ownership for both Goku/Karnov actors, '
           'native support and assisted crossings. Output is one aggregate helper receipt.')
    prepare(output,rom,text,[*refs,proof_path],expected=expected,timeout=240,scope=scope,allow_interactive=True)
    ready=output/'ready.json'
    bindings=json.loads(ready.read_text())
    bindings['timeout']={'thomas':450,'goku':360,'karnov':450}[character]
    ready.write_text(json.dumps(bindings,indent=2)+'\n')


def compose_and_prepare(parent, output, proof_path, vectors_path, actors):
    proof=json.loads(proof_path.read_text())
    vectors=json.loads(vectors_path.read_text())
    assert proof['passed'] and vectors['passed'] and sha(parent)==vectors['parent_SHA256']
    for source in (proof,vectors):
        for path,digest in source['bindings'].items():
            assert sha(Path(path))==digest,path
    image=install(parent.read_bytes(),proof['patches'])
    expected=vectors['memory_only_SHA256']
    assert sha256(image).hexdigest()==expected
    # Validate all controller byte anchors before producing any output.
    for actor in actors:
        controller(image,expected,proof,actor)
    output.mkdir(exist_ok=True)
    rom=output/'candidate.nes'
    assert not rom.exists()
    rom.write_bytes(image)
    assert sha(rom)==expected
    for ext in ('.dbg','.lbl'):
        rom.with_suffix(ext).write_bytes(parent.with_suffix(ext).read_bytes())
    manifest=dict(passed=True,native=False,parent_SHA256=sha(parent),candidate_SHA256=expected,
                  parent=str(parent.resolve()),source_proof=str(proof_path.resolve()),
                  irq_proof=str(vectors_path.resolve()),actors=actors)
    (output/'candidate.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for actor in actors:
        packet(rom,expected,output/actor,proof_path,actor)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    kind=ap.add_mutually_exclusive_group(required=True)
    kind.add_argument('--rom',type=Path)
    kind.add_argument('--parent',type=Path)
    ap.add_argument('--expected')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--character',choices=ACTORS)
    ap.add_argument('--proof',type=Path,default=R/'build/helper-camera-admission-1110/proof.json')
    ap.add_argument('--irq',type=Path,default=R/'build/helper-camera-admission-1110/a226-irq.json')
    args=ap.parse_args()
    if args.parent:
        compose_and_prepare(args.parent,args.output,args.proof,args.irq,
                            (args.character,) if args.character else ACTORS)
    else:
        assert args.expected and args.character
        packet(args.rom,args.expected,args.output,args.proof,args.character)


if __name__=='__main__':
    main()
