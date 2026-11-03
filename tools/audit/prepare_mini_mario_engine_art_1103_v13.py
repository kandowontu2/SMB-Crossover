"""Apply the pinned compiler animation-type mapping before native state dispatch."""
import json,zipfile
from pathlib import Path
import prepare_mini_mario_art_1103_v12 as P


def main():
    O=P.O;q=json.loads((O/'layout.json').read_text());receipt=json.loads((O/'receipt.json').read_text())
    assert receipt['passed']and not(O/'engine-art-v13.json').exists()
    with zipfile.ZipFile(O/'compiler-inputs.zip')as z:helper=z.read('src/shared/lib/sprites/helpers.ts').decode()
    assert 'return fn(items[0], false)'in helper and 'return fn(items[index % 4], false)'in helper
    sequences=[];data=bytearray();index=bytearray();rows=[];comparisons=0
    for name,form in q['forms'].items():
        for state in form['states']:
            kind=state['animationType'];assert kind in['platform_player','fixed','multi','multi_movement']and(kind=='fixed'or not state['flipLeft'])
            state_rows=[]
            for engine,source in enumerate([3,0,2,1,7,4,6,5]):
                selected=0 if kind=='fixed'else source%4 if kind=='multi'else source
                ids=state['animations'][selected]['pose_ids']
                if ids not in sequences:
                    sequences.append(ids);at=len(data);data.extend([len(ids)]+ids)
                else:
                    si=sequences.index(ids);at=sum(1+len(s)for s in sequences[:si])
                index.extend(at.to_bytes(2,'little'))
                assert list(data[at+1:at+1+data[at]])==ids
                comparisons+=len(ids);state_rows.append(dict(engine_animation=engine,source_animation=selected,offset=at,pose_ids=ids))
            rows.append(dict(form=name,state=state['name'],animationType=kind,engine_rows=state_rows))
    (O/'engine-animation-index.bin').write_bytes(index)
    (O/'engine-animation-frames.bin').write_bytes(data)
    out=dict(passed=True,source_only=True,rows=rows,engine_rows=len(index)//2,unique_sequences=len(sequences),
        index_bytes=len(index),sequence_bytes=len(data),exact_frame_references=comparisons,
        source_roles={'platform_player':['idleRight','idleLeft','jumpingRight','jumpingLeft','movingRight','movingLeft','climbing','unused'],
            'engine_order':['source3','source0','source2','source1','source7','source4','source6','source5']},
        note='v12source rows remain immutable/raw editor metadata. This supplement applies real fixed->source0/multi->source%4 before toEngineOrder. Use these engine pointers for Death/Static/PipeTransition; empty sourceeditor rows are not implicit deletion of compiledfixed poses.',
        source_priority=True,native_anchor_qualified=False,NES_native=False,ROM_written=False,
        bindings={str(p.relative_to(P.R)):P.sha(p.read_bytes())for p in[Path(__file__),O/'layout.json',O/'receipt.json',O/'compiler-inputs.zip',O/'body.chr',O/'poses.bin']})
    (O/'engine-art-v13.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','engine_rows','unique_sequences','index_bytes','sequence_bytes','exact_frame_references']}))


if __name__=='__main__':main()
