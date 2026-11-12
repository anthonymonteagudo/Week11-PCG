# Guided exercise: change the trail vegetation

**Optional practice.** Use the supplied project in Unreal Engine **5.7**. The photoreal meshes, materials and example maps are included. You do not need to download assets, install an extra plugin or build C++.

## Open the prepared example — 2 minutes

1. Open `Unreal/Week11PCGTrail/Week11PCGTrail.uproject` and wait for the initial shaders.
2. Choose **Tools > Week 11 PCG Museum > Full trail exercise**. This opens `Content/Trail/Maps/Trail_Student`.
3. In the World Outliner, select **PCG_Scrub**. In Details, select its **PCG component**. Expand the graph-instance parameters. The parent graph is **PCG_BiomeScatter**.

The path, region inputs and assets are already set up. Leave the tree and rock actors unchanged.

## Predict, change, compare — 4 minutes

Find **KeepFraction**. Its supplied value is **0.78**, with **VariationSeed = 41**.

1. Predict what lowering KeepFraction will do to the vegetation. Should it move the path or change the trees?
2. Override **KeepFraction to 0.50**. Click **Generate** on the PCG component.
3. Compare from the same viewpoint. There should be fewer scrub meshes, while the tree and rock layers stay the same. The prepared baseline has 412 scrub instances; this controlled change produces 268 in the tested UE 5.7.4 project.

KeepFraction gives each candidate a chance of surviving this stage. It does **not** request an exact number of final meshes. Other filters and pruning also affect the final count.

## Restore and explain — 2 minutes

Reset the KeepFraction override to **0.78** and click **Generate**. Explain to a partner what changed and why the other populations stayed stable. With the original inputs and settings restored, the original result should return.

**Success:** you can find one exposed parameter, predict its effect, compare one change and restore the supplied result. This is a guided class exercise, not an additional final-project requirement.

## How the reusable system works

`PCG_Trees`, `PCG_Rocks` and `PCG_Scrub` use graph-instance presets of one parent graph, **PCG_BiomeScatter**. The parent defines the rules. Each preset supplies reusable defaults and an asset set. A component can override those values for one actor.

| Control | Meaning |
| --- | --- |
| AssetSet | A supplied table of meshes and selection weights. Weights are relative chances, not quotas. |
| SpacingCm | Distance between proposed points before later filtering. Smaller values usually propose more points. |
| ScaleMin / ScaleMax | Allowed uniform scale range. Keep the minimum at or below the maximum. |
| VariationSeed | Repeatable variation with otherwise unchanged inputs, rules, assets and engine behavior. |
| HabitatTag / ClearingTag | Tagged closed splines defining allowed regions and exclusions. |
| ReservationTag | The prepared trail exclusion for that asset population. |
| PatchCutoff | Threshold on spatial noise that breaks vegetation into patches. |
| KeepFraction | Random survival probability at one filtering stage. |
| SlopeMinDot | Ground normal alignment with world up. Higher values accept flatter ground. |
| PruneRadiusCm | Point-bound neighborhood used to resolve nearby competitors. |
| FavorClearings | Selects a complementary spatial preference for that population. |

## Optional experiments after the guided task

Choose **one** when you have time. These are alternatives, not a list to finish in class.

- On Scrub, change AssetSet to **DT_JuniperOnly**, generate and restore it. The table contains three compatible juniper forms. A new arbitrary asset set may require different scale and clearance margins.
- Move a **Habitat_Clearing** closed spline and regenerate the affected layers. Observe which region becomes empty, then undo the move and regenerate.
- Open the forest, snow or spline-layout variation maps. Identify which inputs or presets changed while the parent graph stayed shared.
- Open **Building examples** from the museum menu. Select Lodge and compare Cells `(3,4,2)` with `(5,2,3)`. X/Y count bays and Z counts floors. Restore the original values. The example supports rectangular footprints and a flat platform roof; it does not design playable interiors.

Bounds-based point pruning is an approximation. Inspect actual mesh footprints near a path bend. A clear-looking path does not establish collision or navigation correctness.

Return to [Start here](START-HERE.html) or review the [sources](Sources.html).
