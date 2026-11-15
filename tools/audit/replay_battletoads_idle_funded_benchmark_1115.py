"""Exact parent/candidate cadence facade; frozen bbee observer body unchanged."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json

import compose_battletoads_idle_funded_1115 as C
import replay_battletoads_idle_funded_1115 as F

C_SHA='2ecaff26b204a7969878f18775369806a9ec3ed267d6f41c8e4fcf691f069856'
F_SHA='401a6b933a9fe84996a4070c92f56da2eb9c8a8f1cfd17287adc9eea9b82cb68'
FROZEN_LUA='bbee821d0038d4074b36747ce743636b2fc643e946f25dd659538294e131963e'
R,ROM=F.R,F.ROM


@lru_cache(maxsize=1)
def sources():
    assert sha256(Path(C.__file__).read_bytes()).hexdigest()==C_SHA
    assert sha256(Path(F.__file__).read_bytes()).hexdigest()==F_SHA
    C.lease()


@lru_cache(maxsize=2)
def candidate(raw):
    sources();pin=sha256(raw).hexdigest()
    if pin==C.PIN:return C.proposal(raw)[0]
    assert pin==C.CANDIDATE,'Expected exact 7a80 parent or exact a90c source image'
    C.inverse(raw);return raw


@lru_cache(maxsize=2)
def config(raw):
    image=candidate(raw);q=deepcopy(F.bindings(image,'rash'))
    reference=F.reference(image)
    q['ram']['NmiSkipped']=F.Previous.Idle.config(F.Previous.parent(reference))['ram']['NmiSkipped']
    q['sha']=sha256(raw).hexdigest()
    for hook in q['hooks'].values():
        at=16+hook['offset'];assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes'])
        if 'bank'in hook:
            at=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=2)
def controller(raw):
    image=candidate(raw);old=F.cadence_reads(image)
    assert sha256(old.encode()).hexdigest()==FROZEN_LUA
    old_config=config(image);new_config=config(raw)
    def opaque(q):
        q=deepcopy(q);q.pop('sha')
        for hook in q['hooks'].values():hook.pop('bank_SHA256',None)
        return q
    assert opaque(old_config)==opaque(new_config),'Facade changed more than pin/bank hashes'
    lua=F.Previous.Stage.Previous.Parent.Frozen.lua
    prefix='local C='+lua(old_config)+'\n';assert old.startswith(prefix)
    text='local C='+lua(new_config)+'\n'+old[len(prefix):]
    assert text.split('\n',1)[1]==old.split('\n',1)[1]
    F.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    assert '\r'not in text
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),controller_SHA256=sha256(text.encode()).hexdigest(),
        observer_body_SHA256=sha256(text.split('\n',1)[1].encode()).hexdigest(),
        frozen_candidate_controller_SHA256=FROZEN_LUA,NmiSkipped_RAM=config(raw)['ram']['NmiSkipped'],
        only_config_ROM_pin_and_actual_hook_bank_hashes_rebound=True,ordinary_controls_only=True,
        literal_reads=True,idle_Main=48,Right_Main=32,outputs=0,Mesen_run=False)


def main():
    parent=C.load_current_image();image=candidate(parent);original=Path.read_bytes
    def guarded(path):
        assert path.resolve()!=ROM.resolve(),'Benchmark reread mutable Nightly'
        return original(path)
    def forbid(*a,**kw):raise RuntimeError('Benchmark attempted file/native output')
    with patch.object(Path,'read_bytes',guarded),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',forbid):
        rows=[metadata(raw)for raw in(parent,image)]
        assert rows[0]['observer_body_SHA256']==rows[1]['observer_body_SHA256']
        assert controller(image)==F.cadence_reads(image)
        rejects=[]
        for label,raw in(('truncated',parent[:-1]),('zero',bytes(len(parent))),('ae66',F.reference(image))):
            try:controller(raw)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong benchmark input accepted',label))
        for label,raw,at in(('dirty_parent',parent,90000),('dirty_candidate',image,90000),('owned_candidate',image,653512),('cookie_candidate',image,765868)):
            dirty=bytearray(raw);dirty[at]^=1
            try:controller(bytes(dirty))
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Dirty benchmark input accepted',label))
    q=dict(controllers=rows,rejections=rejects,portable_after_initial_read=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
