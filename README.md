# mod_utils
Small utility scripts to help me with mod development. Invocations for a mod usually bundled together in a shell script located in the project's "scripts/" directory.

- **fixCamelCaseResources.pl** : changes all the filenames in a directory from CamelCase to snake_case. Used for old mod textures, primarily.
- **gen_blockstate_jsons.pl** (deprecated) : prompt-driven perl script to create blockstates. Results usually need editing.
- **gen_blockstate_jsons.py** (WIP) : command-line python script to create blockstates from args. Based on the old gen_blockstate_jsons.pl script, but more reliable.
- **gen_model_jsons.pl** (deprecated) : prompt-driven perl script to create block & item models. Results usually need editing. TODO: replace with command-line python script.
- **gen_model_jsons.py** (TODO/WIP) : command-line python script to create block & item models.
- **generator.pm** : common perl functions for the various mod_utils perl scripts.
- **make_custom_recipes.py** : command-line python script to create standard crafting, smelting, blasting, cooking, and Fusion furnace recipes. Not used as much now that datagen handles this kind of recipes.
- **make_loot_drops.py** : command-line python script to create standard "drop myself on harvest" loot table jsons.
- **make_recipe_advancements.py** (deprecated) : command-line python script to create recipe advancements. Not used as much now that datagen creates recipe advancements along with recipes.
- **make_silents_recipes.py** : command-line python script to create Silent's Mechanisms crushing and alloy smelting recipes.
- **make_storage_recipes.py** (deprecated): command-line python script to create standard item (default: ingot), block, and smaller item (default: nugget) storage recipe jsons. Not used as much now that datagen handles this.
- **make_tool_recipes.py** (deprecated): command-line python script to create standard tool recipes, given material input. Not used as much now that datagen handles this.

