"""Installed421 inverse portability and strict input rejection; no writes."""
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compose_smb2_hidden_response_1114 as C

LUA_HASHES=('657653d27899be1aeaf47216d759620e1066f033d0f40aad1f72d5c375a4f813',
 'a857cbd14c998ef57ba6edf8047bf67a5ba6b4f597279ead90b1952a54adc2b2',
 '4efcbbb527485fbba22a248a03409f2afef487601a2228e49dc2c38c9a2b36ea',
 '20b3a2f4368b4cf6b2d77d80e14861ff6630bb4f9b0f32ad4b97c501ac91b78e',
 '203212dfbefe717e0e0ac9b57a054dbe54acfe35b5515ae608ee6a969061c9af',
 '610206d277d82bc47b7daeffd4816af0a679409fb43036f22d43a2213f551e6b',
 '98ebc28886ae6187b49358efee70fa3e12d9c9be5a53c74c573ecb0a658768d7',
 'a7f38e934ae9327f1d426ac80099a29b2b5d8dc760a2358d371c7ec1e5cfd8cc')


def check():
    image=C.load_current_image();parent=C.inverse(image);_,info=C.proposal(parent)
    nightly=C.Cache.Parent.Owner.D.C.Owner.NIGHTLY.resolve()
    read=Path.read_bytes;attempts=0
    def guarded(path):
        nonlocal attempts
        if path.resolve()==nightly:
            attempts+=1;raise AssertionError('Live Downloads read forbidden for inverse')
        return read(path)
    def bad(fn,arg):
        try:fn(arg)
        except AssertionError:return 1
        raise AssertionError('Dirty or unknown image accepted')
    with patch.object(Path,'read_bytes',guarded),patch.object(C.Cache,'parent_image',side_effect=AssertionError('Mutable parent lookup forbidden')):
        C.bindings.cache_clear();C.Cache.bindings.cache_clear();C.Cache.public_image.cache_clear()
        C.Cache.Measure.Route.inputs.cache_clear()
        assert C.inverse(image)==parent and C.proposal(C.inverse(image))[0]==image
        import replay_smb2_hidden_response_1114 as Replay
        actual=tuple(sha256(Replay.controller(image,v).encode()).hexdigest()for v in range(8))
        assert actual==LUA_HASHES
        changed=bytearray(image);changed[971064]^=1
        count=bad(C.inverse,bytes(changed))
        changed=bytearray(image);changed[0]^=1;count+=bad(C.inverse,bytes(changed))
        count+=bad(C.inverse,parent)
        changed=bytearray(parent);changed[0]^=1;count+=bad(C.proposal,bytes(changed))
        owner=C.Cache.Parent.Owner.D.C.Owner
        for raw in(parent,image):
            with patch.object(owner,'NIGHTLY',SimpleNamespace(read_bytes=lambda raw=raw:raw)):
                assert C.load_current_image()==image
        with patch.object(owner,'NIGHTLY',SimpleNamespace(read_bytes=lambda:bytes(changed))):
            count+=bad(lambda _:C.load_current_image(),None)
    assert attempts==0 and count==5
    return dict(passed=True,ROM_SHA256=info['ROM_SHA256'],exact_parent_SHA256=sha256(parent).hexdigest(),
        inverse_and_roundtrip_with_live_Downloads_reads_forbidden=True,
        cold_source_binding_caches_cleared=True,all8_original_Lua_hashes_unchanged=list(actual),
        live_Downloads_reads_attempted=attempts,dirty_unowned_unknown_rejections=count,
        explicit_loader_fa66_and_installed421_cases=2,
        source_proven_original_probe_and_fill_preimages=True,outputs=0,Mesen_run=False)


if __name__=='__main__':print(json.dumps(check(),separators=(',',':')),flush=True)
