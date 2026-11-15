"""Measure combined decoded encoding only; never rebuild a combined ROM."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import current_prince_body_research_ae66_1114 as Current
import compose_prince_body_world_1114 as Body
import check_prince_window567_render_1114 as Gfx


def run(raw):
    current=Current.normalize(raw,kind='bt-service-ae66')
    reference=current.reference1daca;historical,body=Body.proposal(reference)
    assert Body.digest(historical)=='e4185311a7031c88570467dc99225ee42baad7c4931b5cfa1d57d37e7720dd08'
    head,original,_=Gfx.Packet.extract(current.referenceF11)
    assert original==Gfx.Packet.extract(reference)[1]
    parts,_=Gfx.arrays(current.referenceF11);combined=list(map(bytearray,parts))
    fitted=Gfx.Packet.extract(historical)[1]
    for row in Body.allocation()['decoded_spans']:
        stream=row['decoded_stream'];lo,hi=row['decoded_half_open']
        assert Body.digest(fitted[stream][lo:hi])==row['proposed_SHA256']
        combined[stream][lo:hi]=fitted[stream][lo:hi]
    allowed={stream:set()for stream in range(3)}
    for row in Body.allocation()['decoded_spans']:
        allowed[row['decoded_stream']].update(range(*row['decoded_half_open']))
    for row in json.loads(Gfx.GRANT.read_bytes())['envelopes']:
        allowed[row['stream']].update(range(row['offset'],row['offset']+row['bytes']))
    for stream,(before,after)in enumerate(zip(original,combined,strict=True)):
        assert len(before)==len(after)and all(a==b for at,(a,b)in enumerate(zip(before,after,strict=True))if at not in allowed[stream])
    packed=[Gfx.Packet.encode(bytes(part))for part in combined];sizes=list(map(len,packed))
    spare=len(Gfx.Packet.PAGES)*1024-len(head)-sum(sizes)
    assert spare>=0 and sizes[0]<=6528 and 0xe100-sizes[1]>=0xc900
    q=dict(passed=True,input=current.metadata(),historical_body_image=Body.digest(historical),
        combined_decoded_SHA256=[Body.digest(bytes(part))for part in combined],
        packed_stream_bytes=sizes,existing_carrier_spare=spare,
        runtime_staging6528_pass=True,metadata_source_C900_floor_pass=True,
        all_other_decoded_bytes_exact=True,extra_physical_storage=0,
        scope='Pure combined array encoding measurement under existing two-span body and three-span graphics leases',
        combined_ROM_composed=False,importer_proposal_included=False,Mesen=False,outputs=0)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Encoding measurement attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
