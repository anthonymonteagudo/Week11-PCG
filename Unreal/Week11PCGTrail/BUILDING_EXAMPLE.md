# Modular building example

Open **Tools > Week 11 PCG Museum > Building examples** in UE 5.7.4. This is a prepared instructor demonstration and an optional student extension after the guided trail exercise.

Six actors use graph instances of **PCG_ModularBuilding**. Select `Building_Lodge`, open its PCG component and edit its graph-instance parameters. Change **Cells** and click **Generate**. X is the number of bays along local X, Y is the number along local Y, and Z is the floor count. The graph rounds down and clamps each count to 1–12. Keep actor scale at one. Move or rotate the actor to compare local and world space.

| Control | What changes |
| --- | --- |
| Cells | Footprint and number of floors. `(3,4,2)` means 12 floor cells per level, with two levels. |
| FacadeSet | A persistent mesh/weight DataTable. Windows and Solid use the same measured kit contract. |
| VariationSeed | Which compatible facade mesh each surviving face receives. |

The Cabin, Lodge, Tower and Longhouse demonstrate footprint and floor-count changes. Rotated tests the same building under a 30-degree actor rotation. Solid changes the facade collection while keeping the Lodge dimensions.

## What the graph teaches

1. **Dimensions become points.** A 3D grid creates local cell centres. A vertical shift places floor origins at 0, 350, 700 cm and onward. One floor works without a degenerate vertical spline.
2. **Difference removes internal faces.** Four half-bay offsets propose opposite wall faces. Coincident interior faces cancel before mesh pivot corrections. These are hard point bounds with Binary Difference. The tutorial's Minimum approach uses a different density contract, so its density-remap steps are not universally interchangeable.
3. **The kit has a contract.** The local Old West walls span approximately 400 cm along negative Y, rise approximately 350 cm along Z and use a start-edge pivot. Each orientation needs its own pivot correction. The wall's name alone does not establish its height.
4. **Corners belong to the footprint.** A four-corner lattice combines with one point per floor. Copy Points carries all four junctions up the building. The selected 450 cm pillar receives a deliberate Z-only scale to match the 350 cm storey.
5. **Profiles change appearance after topology.** A mesh/weight table selects interchangeable facades. The wall count stays the same when the profile changes.
6. **Local rules precede world placement.** Copy Points applies the building actor transform after local cancellation and assembly. This keeps actor rotation out of orientation classification.

The roof is a flat platform made from the floor modules. This first example demonstrates closure and elevation. It does not yet implement the Udemy pitched roof kit, differentiated base/top floors, trims, arbitrary closed footprints, doors and circulation, or nested building population. Do not present it as a finished architectural generator.

## Short demonstration

Show Cabin and Tower. On Lodge, change Cells from `(3,4,2)` to `(5,2,3)`, Generate, then restore. Inspect one `05 ... remove internal faces` node before spawning and relate the accepted faces to the building outline. Switch between Windows and Solid. Rotate the building and check that the walls, roof and corner posts move together.

Ask students to predict exterior wall count: `2 × (rows + columns) × floors`. A 3-by-4 footprint with two floors has 28 wall modules, 8 corner posts, 24 floor modules and 12 roof modules. Count topology before judging appearance.

## Asset setup and limits

Meshes and materials come from the already-local **Old West Learning** Fab source: https://www.fab.com/listings/785da98f-3c56-4736-b898-826116d8f06f . Source packages retain their `/Game/Northwood/...` paths. Replacement wall meshes must match dimensions, pivot, facing axis and floor height. A differently shaped kit needs an adapter, not arbitrary scaling of every mesh.

The private Week 11 kit already contains the required meshes, materials and native graph assets. Open the project; no migration, setup script or C++ compilation is required. Houdini Engine and marketplace PCG extensions are not dependencies. The building demonstration is original class material; downloaded course projects are references rather than bundled dependencies.
