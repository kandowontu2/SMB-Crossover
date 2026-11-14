"""Explicit421 input wrapper preserving hidden110 and delegated fa66 fixes."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Literal

import current_smb2_cheat_input_1114 as Previous
import compose_smb2_hidden_response_1114 as Response

HIDDEN=Response.CANDIDATE
CHEAT=Previous.CHEAT
POSTBG=Previous.POSTBG
KINDS={'hidden-421':HIDDEN}
PREVIOUS_SOURCE='f973573e52a2c752da3531ee6bc3706dc8e1096b79cc0fab2740ad4f0fb20f34'
RESPONSE_SOURCE='7d8e2210a38952902694efcbb5334ae9b704902679b6353e43834f361bbee71a'
STEP='hidden_response.inverse 421->fa66'


def digest(raw):return sha256(raw).hexdigest()


def dependencies():
    assert digest(Path(Previous.__file__).read_bytes())==PREVIOUS_SOURCE
    assert digest(Path(Response.__file__).read_bytes())==RESPONSE_SOURCE
    assert digest(Response.Cache.GRANT.read_bytes())==Response.Cache.GRANT_SHA
    assert digest(Response.GRANT.read_bytes())==Response.GRANT_SHA
    Previous.dependencies()


def hidden_envelopes():
    dependencies()
    resource=json.loads(Response.Cache.GRANT.read_bytes())
    spans=tuple((q['file_half_open'][0],q['bytes'])for q in resource['spans'])
    assert sum(size for _,size in spans)==201
    assert all(end==at+size for q,(at,size)in zip(resource['spans'],spans,strict=True)
               for end in(q['file_half_open'][1],))
    return spans


def protected_envelopes():return Previous.protected_envelopes()+hidden_envelopes()


@dataclass(frozen=True)
class CurrentInput:
    kind:Literal['hidden-421']
    original:bytes
    previous:Previous.CurrentInput
    inverse_steps:tuple[str,...]

    @property
    def original_SHA256(self):return digest(self.original)

    @property
    def fa66(self):return self.previous.original

    @property
    def postbg(self):return self.previous.postbg

    def preserve(self,legacy_result,*,legacy_result_SHA256,allowed_component_offsets):
        """Apply a pinned qualified12397 component delta, preserving all421."""
        dependencies()
        assert self.kind=='hidden-421'and isinstance(self.original,bytes)and digest(self.original)==HIDDEN
        assert isinstance(self.previous,Previous.CurrentInput)and self.previous.kind=='cheat-fa66'
        assert digest(self.fa66)==CHEAT and digest(self.postbg)==POSTBG
        expected=(STEP,'cold_mirror.inverse fa66->e8','owner.inverse e8->12397')
        assert self.inverse_steps==expected and self.previous.inverse_steps==expected[1:]
        assert isinstance(legacy_result,bytes)and len(legacy_result)==len(self.original)
        assert digest(legacy_result)==legacy_result_SHA256
        allowed=frozenset(allowed_component_offsets)
        assert all(type(i)is int and 0<=i<len(legacy_result)for i in allowed)
        hidden_spans=hidden_envelopes()
        hidden={i for at,size in hidden_spans for i in range(at,at+size)}
        assert not allowed&hidden,'Component ownership overlaps complete201 hidden-response bytes'
        assert all(legacy_result[at:at+size]==self.postbg[at:at+size]for at,size in hidden_spans)
        # The existing normalizer remains the sole owner of restoring fa66's
        #66 bytes and rejecting complete cheat-envelope overlap/provenance.
        cheated,previous_info=self.previous.preserve(legacy_result,
            legacy_result_SHA256=legacy_result_SHA256,allowed_component_offsets=allowed)
        assert previous_info['current_fix_changed_bytes_preserved']==66
        result=bytearray(cheated)
        for at,size in hidden_spans:result[at:at+size]=self.original[at:at+size]
        result=bytes(result)
        changed={i for i,(a,b)in enumerate(zip(self.postbg,legacy_result,strict=True))if a!=b}
        current={i for i,(a,b)in enumerate(zip(self.postbg,self.original,strict=True))if a!=b}
        hidden_changed={i for i in hidden if self.original[i]!=self.fa66[i]}
        protected={i for at,size in protected_envelopes()for i in range(at,at+size)}
        assert len(hidden_changed)==110 and len(current)==176 and current<=protected
        assert not allowed&protected and changed<=allowed and not changed&current
        assert all(result[i]==self.original[i]for i in range(len(result))if i not in changed)
        assert all(result[i]==legacy_result[i]for i in changed)
        assert all(result[at:at+size]==self.original[at:at+size]for at,size in protected_envelopes())
        info=dict(previous_info)
        info.update(input_kind=self.kind,current_input_SHA256=HIDDEN,
            normalized_cheat_SHA256=CHEAT,output_SHA256=digest(result),
            inverse_steps=list(self.inverse_steps),
            hidden_response_changed_bytes_preserved=110,fa66_changed_bytes_preserved=66,
            current_fix_changed_bytes_preserved=176,complete_hidden_envelope_bytes=201,
            complete_current_hidden_and_cheat_envelopes_exact=True,
            all_current_bytes_outside_component_exact=True,
            native_qualified=False,installed=False,outputs=0)
        return result,info


def normalize(raw,*,kind:Literal['hidden-421']):
    dependencies()
    assert kind=='hidden-421','Caller must explicitly choose hidden-421'
    assert isinstance(raw,bytes)and digest(raw)==HIDDEN
    fa66=Response.inverse(raw);assert digest(fa66)==CHEAT
    previous=Previous.normalize(fa66,kind='cheat-fa66')
    assert Response.proposal(previous.original)[0]==raw
    return CurrentInput(kind,raw,previous,(STEP,)+previous.inverse_steps)
