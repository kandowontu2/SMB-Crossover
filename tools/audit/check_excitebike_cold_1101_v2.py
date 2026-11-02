"""Repeat only the changed cold ISR proof on the repaired current image."""
import check_excitebike_cold_1101_v1 as L
from compose_excitebike_current_1101_v2 import bundle
from prepare_excitebike_dispatch_1101_v1 import save

if __name__=='__main__':
    L.bundle=bundle
    L.save=lambda name,q:save('cold2-CPU.json',q)
    L.main()
