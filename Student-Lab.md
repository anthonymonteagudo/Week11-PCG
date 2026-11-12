# Art Director vs. Algorithm

Work in pairs for **20 minutes**. One person describes the intended appearance; the other changes one exposed control and explains the result. Then swap roles.

Open **Tools > Week 11 PCG Museum > Full trail exercise**. The map is `Content/Trail/Maps/Trail_Student`. Duplicate the map before editing. The project is already configured and includes its assets.

## One graph, several profiles

`PCG_Trees`, `PCG_Rocks` and `PCG_Scrub` reference graph-instance presets of **PCG_BiomeScatter**. The shared graph defines the placement rules. A graph-instance asset supplies reusable defaults; the component's parameter overrides apply local changes to that actor.

Select an actor and its **PCG component** in Details. Edit its graph-instance parameters rather than replacing the parent graph. Click **Generate** after a change. Reset an override to return to the preset.

| Control | What it means |
| --- | --- |
| AssetSet | Weighted mesh collection. Weights are relative chances, not quotas. |
| SpacingCm | Candidate spacing; smaller values propose more points. |
| ScaleMin / ScaleMax | Uniform scale range; keep minimum at or below maximum. |
| VariationSeed | Repeatable variation under fixed inputs, rules, assets and engine version. |
| HabitatTag / ClearingTag | Tagged closed spline inputs defining permitted regions and exclusions. |
| ReservationTag | Prepared trail exclusion compatible with the chosen layer's size. |
| PatchCutoff | Threshold on spatial noise that shapes habitat patches. |
| KeepFraction | Random candidate survival after other decisions. |
| SlopeMinDot | Ground normal alignment with up; higher values favor flatter ground. |
| PruneRadiusCm | Neighborhood used for competing point bounds. |
| FavorClearings | Chooses the complementary spatial preference used by a layer. |

## 1. Brief — 3 minutes

Find the winding path and a clearing. Predict which vegetation should change if the clearing moves. Identify the requirement that the walking corridor remains clear.

## 2. Change and compare — 10 minutes

1. Keep `PCG_Scrub` at seed **41**. Change **KeepFraction** from **0.78 to 0.50**, Generate and compare. Keep the other layers unchanged.
2. Move one `Habitat_Clearing` input about **3500 cm (35 m)** sideways. Generate the affected layers. Explain the empty region using the closed spline, not a lucky seed.
3. Inspect a path bend from near the ground. Check the final mesh footprint as well as the point centre, and check that objects contact the terrain.

## 3. Partner test — 4 minutes

Swap roles. Reset the moved clearing. On Scrub, change **AssetSet** to the supplied **DT_JuniperOnly** table and regenerate. This compatible collection contains three juniper forms. Explain why a collection change should leave the tree and rock layers stable.

Open a variation map to compare a different density or spline layout. The region maps add forest and snow asset/material profiles using the same placement system. Arbitrary new assets may require different scale limits and reservation margins.

## 4. Handoff — 3 minutes

Reset local overrides and restore the clearing; regenerate the baseline. Tell your partner the purpose, a required input, the control you changed, expected behavior and one limitation.

The final count depends on multiple filters and pruning. KeepFraction is not an exact fraction of the final mesh count. A seed alone does not guarantee identical results after changes to the graph, assets or engine.

## Optional: building rules

Open the building examples from the museum menu. On Lodge, compare **Cells** `(3,4,2)` and `(5,2,3)`. X/Y count bays and Z counts floors. Restore the baseline, switch compatible FacadeSet tables, and rotate the actor. Predict which topology should remain stable when only the facade profile changes.

Broader procedural level design also includes room connectivity, encounter budgets and gameplay reachability. These are useful future constraints, not implemented systems in this trail exercise. An environment generator should respond to gameplay requirements as well as visual preferences.
