"""Same finite Bill controls with the genuine graphics-owned C-bank entry."""
from pathlib import Path
import json
import sys
import final_bill_lance_hard_gallery_source_v1 as original


class BillArena(original.BillArena):
    def __init__(self,b,variant=0):
        super().__init__(b,variant)
        # Actual RosterPose -> RosterGraphicsBank establishes BILL_GFX C19.
        # Its direct BillSourceBounds caller is not valid with the generic
        # renderer audit's unrelated default C88. Execute the real gateway;
        # never stub that bounds consumer or its terrain/enemy queries.
        self.invoke('PlayerGfxHandler')
        assert self.m.banks[2]==19 and self.get('CurrentBankC')==147


def main():
    original.BillArena=BillArena
    original.main()
    out=Path(sys.argv[sys.argv.index('--output')+1])
    manifest=json.loads((out/'manifest.json').read_text())
    files=[Path(__file__),original.D/'final-bill-lance-hard-gallery-source-v1/failure.json',
           original.D/'final-bill-lance-hard-gallery-source-diagnostic-v1/instruction-boundary-failure.json',
           original.D/'final-bill-lance-hard-gallery-source-diagnostic-v1/first-invalid-fetch.json']
    manifest['bindings'] += [dict(path=str(f),sha256=original.sha(f),bytes=f.stat().st_size)for f in files]
    original.put(out/'manifest.json',manifest)
    proof=json.loads((out/'proof.json').read_text())
    proof.update(manifest_sha256=original.sha(out/'manifest.json'),
        caller_fixture_correction='Actual PlayerGfxHandler/RosterGraphicsBank establishes required C19; original wrong-C88 exception retained.',
        successor_checker_sha256=original.sha(__file__))
    original.put(out/'proof.json',proof)
    print(json.dumps(dict(successor=True,**proof)))


if __name__=='__main__':main()
