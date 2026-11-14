"""Exact421 frozen ordinary/contact source replays; no files or Mesen."""
import argparse
from hashlib import sha256
from functools import lru_cache
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import replay_smb2_hidden_ordinary_1114 as Ordinary
import replay_smb2_hidden_invincible_contact_1114 as Contact
import check_smb2_cheat_cold_routes_1113 as Runner
import run_stdout_mesen_1110 as Native

C=Ordinary.C
HARNESS_SOURCE='8a121e7d4df5628c6aceffc46c7deb2dddc3ff536651f421189e652e7363d8fd'


def run(raw,mode='ordinary',*,metadata_only=False):
    assert mode in('ordinary','contact')and sha256(raw).hexdigest()==C.CANDIDATE
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()==HARNESS_SOURCE
    original_read=Path.read_bytes
    nightly=C.Cache.Parent.Owner.D.C.Owner.NIGHTLY.resolve()
    def read(path):
        assert path.resolve()!=nightly,'421 inverse/controller/source replay attempted a mutable Downloads read'
        return original_read(path)
    def forbid(*args,**kwargs):raise RuntimeError('Readonly421 source regression attempted file output or Mesen')
    factory=Contact if mode=='contact'else Ordinary
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',forbid),\
         patch.object(Path,'write_text',forbid),patch.object(Native,'run',forbid),\
         patch.object(C,'inverse',lru_cache(maxsize=1)(C.inverse)),\
         patch.object(factory,'controller',lru_cache(maxsize=1)(factory.controller)):
        parent=C.inverse(raw);assert sha256(parent).hexdigest()==C.PIN
        text=factory.controller(raw)
        assert sha256(text.replace(C.CANDIDATE,C.PIN,1).encode()).hexdigest()==factory.FROZEN_LUA
        info=factory.metadata(raw)
        rejects=[]
        for label,broken in(('parentfa66',parent),('truncated',raw[:-1])):
            try:factory.controller(broken)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong421 adapter input accepted',label))
        grant=json.loads(C.Cache.GRANT.read_bytes())
        owned_probe=grant['spans'][0]['file_half_open'][0]
        for label,at in(('owned_probe',owned_probe),('unowned_header',0)):
            broken=bytearray(raw);broken[at]^=1
            try:factory.controller(bytes(broken))
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Corrupt421 adapter input accepted',label))
        if metadata_only:q=dict(passed=True,metadata=info)
        else:
            # Only this source harness's binding changes. The actual composer,
            # frozen factories, ROM and every game state remain unmodified.
            bound=SimpleNamespace(CANDIDATE=C.CANDIDATE,Owner=Runner.C.Owner)
            with patch.object(Runner,'C',bound),patch.object(Runner,'Ordinary',Ordinary),patch.object(Runner,'Contact',Contact):
                q=Runner.run_controller(raw,mode,600 if mode=='contact'else 6000)
            q['metadata']=info
            q['actual_title_options_UI_authority']='Frozen parentfa66 native UI evidence only; this421 check is source-only'
        assert sha256(Path(C.__file__).read_bytes()).hexdigest()==factory.COMPOSER_SOURCE
        assert sha256(Path(factory.Frozen.__file__).read_bytes()).hexdigest()==factory.FROZEN_SOURCE
        q.update(strict_adapter_rejections=rejects,mutable_Downloads_reads_after_input_load=0,
                 frozen_fa66_harness_source_SHA256=HARNESS_SOURCE,only_source_harness_binding_changed=True,
                 native_run=False,installed=False,outputs=0)
        return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('ordinary','contact','all'),default='all')
    p.add_argument('--metadata',action='store_true')
    args=p.parse_args();raw=C.load_current_image()
    for mode in('ordinary','contact')if args.mode=='all'else(args.mode,):
        q=run(raw,mode,metadata_only=args.metadata)
        receipt=q.pop('receipt',{})
        if receipt:
            q['source_receipt_SHA256']=sha256(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            q['source_result']={k:receipt[k]for k in('flag','castle','entrance','next_area_updates','full_stage','partial_endpoint','all_returned_Main')if k in receipt}
            if 'contact'in receipt:q['source_result']['contact']=receipt['contact']
        print(json.dumps(q,separators=(',',':')),flush=True)
        assert q['passed'],'Strict frozen421 regression scope did not pass'
