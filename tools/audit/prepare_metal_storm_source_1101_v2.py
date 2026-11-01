"""Bounded one-command original Metal Storm actor/art component recipe.

Run through run_bounded_build_v1.py --output build/metal-storm-component-1101-v2.
The laboratory source component is not a playable host ROM.
"""
import recover_metal_storm_actor_1101_v2 as recovery
import check_metal_storm_actor_1101_v2 as controls
import prepare_metal_storm_art_1101_v2 as art

def main():
    recovery.main()
    controls.main()
    art.main()

if __name__=='__main__':main()
