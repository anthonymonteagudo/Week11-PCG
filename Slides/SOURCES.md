## 1. Proceduralism
READ ALOUD
Procedural content generation (PCG) creates content by applying rules to inputs. Today we will use Unreal PCG to see what those rules do, then look beyond environment dressing. The cover is a graphic illustration, not a claim about our demo output.

## 2. Agenda
READ ALOUD

## 3. Tech setup
Open the class project while we get settled. Let shaders finish compiling before judging performance. Find the museum and check viewport navigation. Think of one repetitive task in your work and the controls you would want to expose.

## 4. GUEST: Amritha Immaneni
READ ALOUD
Introduce Amritha and switch to her supplied presentation, Intro to PCG in Unreal Engine. Her deck covers points, mesh sampling, data assets and assemblies, performance and production examples. Ask how she decides what artists should control and how a graph becomes maintainable. Return here after her presentation. The background is an guest-provided reference, not Amritha’s project.
ASK
Which part of a procedural tool usually needs the most artist feedback?
VISUAL REFERENCE
Guest: Amritha Immaneni · 30 minutes. EVE Vanguard image supplied in her guest deck; CCP Games.

## 5. Break
READ ALOUD
Take a fifteen-minute break after the guest presentation. Then continue with the instructor examples and Unreal demonstrations. Announce the actual return time in class rather than an elapsed minute count.

## 6. GOLF+ road generator
READ ALOUD
This is a procedural road tool used in GOLF+. The artist chooses the route through the environment. The tool uses that input to construct the road and apply the selected road settings. Watch the drawn route become a generated road in the existing course.
This is a production-tool example from GOLF+, not our Unreal PCG graph. The same useful relationship carries over: the artist controls an input and a reusable operation builds the dependent result. Our Unreal examples will make that relationship small enough to inspect node by node.
DISCUSSION
Which decisions should stay with the artist, and which repetitive work should the tool handle?
SOURCE

## 7. Why use a procedural tool?
READ ALOUD
In this second GOLF+ example, the artist provides a parking-lot boundary and adjusts the layout settings. The tool places the repeated elements and builds the result. That is a practical reason to make a procedural tool: an input can change while the tool preserves the relationships between its parts.
The artist still chooses the shape, location and acceptable appearance. A useful tool exposes those choices directly. Before writing a generator, name the repeated task and decide which controls another artist will need.
SOURCE

## 8. GOLF+ course generator
This is my whole-course generator. The road and parking-lot examples are individual systems; here the scope is the whole course. Identify the artist inputs, the repeated work, and what still needs visual review.
https://new.express.adobe.com/publishedV2/urn:aaid:sc:US:8c5ccf0b-31df-5637-85c3-330a564b574f
Play the linked 85-second course-generator recording.

## 9. Inputs and generated results
READ ALOUD
Inputs are part of the design of the tool. A small 2D image can encode a dungeon layout if we define what each pixel means. Here the white cells become floors and the dark cells become walls. The system still needs a policy for doors, connectivity and scale. This diagram illustrates the mapping; it is not our trail demo or a Diablo II implementation.
ASK
What information would a room generator need that a black-and-white image does not specify?
SOURCES
https://www.pcgbook.com/chapter01.pdf

## 10. A PCG graph works like a program
A PCG graph processes data through connected operations. This row is one example: read terrain and path inputs, create candidate points, apply placement rules, and spawn meshes. Other graphs can process different data and do not have to create points. Each node operates on the data passed through the graph.

## 11. Points before meshes
READ ALOUD
A point stores placement information before it becomes a visible rock or tree. These two native captures use the same twelve point transforms and the same camera. The left renders cubes as teaching markers; the right uses the rock mesh. The cubes are an explicit point visualization, not a claim that PCG points are geometry. In the editor, we can also enable a node’s Debug display to inspect intermediate data.

## 12. Point data
A point records a proposed placement. First locate the point in the Unreal viewport, then read its position, rotation and scale in the data table. Density, bounds and seed support further decisions; metadata carries additional attributes. The viewport reference and class-project table illustrate separate point examples.

## 13. Artist controls
An artist changes exposed controls and the generated geometry responds. Watch the control and the resulting pipe geometry together. The tool preserves its relationships while the artist directs the result.
Source: SideFX Project Titan EVO. https://www.sidefx.com/titan-evo/

## 14. Requirements and preferences
A requirement must be satisfied: for example, keep the path clear. A preference guides the appearance: for example, favor groups of plants. A heuristic is a practical rule of thumb, not a guarantee of the best result. Noise can vary the likelihood of placement across a surface so plants form patches. Review the final scene even when every requirement passes.

## 15. Examples of spatial distributions
READ ALOUD
Independent placement may create both clumps and empty gaps by chance. Minimum-distance sampling discourages nearby neighbors. A clustered distribution deliberately forms groups. Choose a distribution that supports the intended environment. A visually pleasing pattern does not, by itself, prove that meshes will avoid overlap.

## 16. Repeatable variation
READ ALOUD
Hold the camera, inputs and settings fixed when comparing a seed change. A seed chooses a repeatable sequence of variation under those conditions. If we change the algorithm, assets or engine behavior, the same seed may produce a different result. A seed is not a substitute for rules that protect the path.
VISUAL REFERENCE
Actual class forest in UE 5.7.4, Shader Model 6. A seed is repeatable only under unchanged conditions.

## 17. Debug a node, then inspect its scene output
READ ALOUD
Debug a specific stage to find the first place where the data becomes wrong. Inspect the node output, then look at its points in the scene. Check whether the points exist, whether projection put them on the intended surface, and whether a filter removed the intended region. Follow the data through one operation at a time.
SOURCE
Brandon Vox course, instructor-supplied captures. The local class graphs and demonstrations use Unreal Engine 5.7.
LATEST UDEMY NOTES: RAY HIT 106 TO 111
World Ray Hit Query samples physics surfaces. If a visible rock produces no hits, inspect collision enabled state, response to the query channel, simple versus complex query geometry and actor filters. For meshes generated by PCG, enforce the generation dependency and inspect Ignore Self Hits / Ignore PCG Hits. Do not disable all collisions as a blanket optimization. The transcript's claim that BlockAllDynamic only blocks WorldDynamic is incorrect: the installed default profile blocks all default channels and uses WorldDynamic as its object type. Object type and channel response are separate concepts. This is optional instructor depth until a clean native example has been captured.

## 18. Assets can drive surrounding materials
READ ALOUD
A generated tree can also provide input to the landscape material. In Cloward's example, the tree material writes its influence into a runtime virtual texture, or RVT. The landscape reads it to blend dirt and roots around the trunk. These consecutive captures show the material and mask around the same tree. The mask gives us a way to connect asset placement with surface appearance. The inverse influence can also suppress conflicting grass or puddles.
ASK
If we move or remove the tree, which parts of the result must update?
DEMO CHECK
Inspect the old and new influence locations. A visually raised mound does not establish changed collision. This is attributed tutorial evidence, not an implemented RVT feature of the class trail graph.
SOURCE
Ben Cloward, PCG episode 06, Automatic Landscape Tree Blending. Instructor-supplied captures 25 and 26. https://www.youtube.com/@BenCloward

## 19. Horizon Zero Dawn placement masks
READ ALOUD
This is Guerrilla’s GDC 2017 explanation of procedural placement in Horizon Zero Dawn. Several spatial fields contribute to placement and exclusion. The transferable idea is how the meanings of those fields combine. Their implementation uses Decima and GPU-based placement, so this is not an Unreal node recipe or a performance claim for our class graph.
SOURCES
https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn
VISUAL REFERENCE
Jaap van Muijden, Guerrilla Games, GDC 2017. Diagram excerpt from page 15.

## 20. Open and closed splines
READ ALOUD
These are two different uses of spline input in our original Unreal example. The open curve supplies an ordered route. Spline Sampler places points along that route and wooden posts appear at those positions. Distance is measured along the curve. Closing a curve can also define an area. In the second branch, Spline Sampler uses On Interior to propose points inside the region. We vary the shrub positions and scale, then use Intersection with the same closed region to retain jittered roots inside it.
The green border is a generated teaching guide. Shrub-root containment does not guarantee that every leaf remains inside the boundary. This is positive scatter inside a region, distinct from the following Difference example that removes points from a region.
DEMO
Open Spline examples from the museum menu. Select OpenSpline_Input or ClosedSpline_Input, edit a spline point, select PCG_SplineExamples, and Generate. In the graph, compare the two Spline Sampler nodes: On Spline versus On Interior. Try open distance 250 cm then 125 cm; try interior spacing 240 cm then 160 cm. Restore the values. The structured asset example follows in the building demo.
DISCUSSION
Why would closing the spline and choosing On Interior produce a different result from sampling its boundary?
SOURCE
Original class graph and native UE 5.7.4 offscreen captures, Spline_Examples. All required meshes/materials are bundled. Capture framing isolates the relevant output population; it does not modify their generated transforms.

## 21. Spline sampling
READ ALOUD
Select the Spline Sampler node and look at Dimension in its Details panel. On Spline samples along the curve, with Distance mode controlling the interval. On Interior samples inside a closed curve. The interior spacing controls the area sampling grid. They solve different placement problems even though the node class is the same.
These are native 5.7 controls from our example, not the older tutorial interface. Smaller spacing produces more points. The second branch adds jitter and then rechecks region containment before spawning shrubs. Open only the relevant branch during the demo.
DISCUSSION
Which setting would you change to double the posts along the route? Would the same numeric change double the point count across an area?
SOURCE

## 22. Difference removes points inside a closed spline
READ ALOUD
Difference subtracts the supplied region from the source point data. Here a closed spline becomes a surface. The binary Difference rejects the six point centres inside it, leaving six outside. The orange outline is an actual scene input. This filters point placements; it does not perform a Boolean cut on the terrain mesh or guarantee full mesh collision clearance.
VISUAL REFERENCE
Actual class graph and scene. The before view bypasses Difference; the after view enables it.

## 23. Account for asset size
A point tests a location. A spawned object occupies space. A rock can have its center outside a path and still extend into it. Reserve enough clearance for the mesh footprint, and inspect the final meshes after placement. Bounds can help estimate this space; the final visual check remains important.

## 24. Difference keeps rocks clear of trees
READ ALOUD
We have already used Difference to reserve a closed spline region. The subtracting region can also come from another generated population. Here the accepted tree locations define occupied regions. The Source input carries six proposed rock placements, including two that intersect tree trunks. Difference rejects those conflicts and leaves four rocks. The trees remain fixed.
This is a deliberately small example of priority: accept the trees first, then place rocks around them. If the priority changes, the data flow must change too. These fixed-camera captures come from our own UE 5.7 teaching map. The six candidate locations are explicit input points so that the effect of this one operation is easy to see.
DEMO
Tools > Week 11 PCG Museum > Population exclusion example. Open PCG_PopulationExclusion. Disable node 06 Difference to show six rocks, enable it to restore four. Move one point in 01 Accepted tree locations and Generate. The excluded rock positions follow the input. Restore the point before continuing.
LIMIT
The tree regions use conservative point bounds, not exact mesh collision. Check final footprints when changing assets or scale.
ASK
Which population should have priority in your own tool, and what data must the later population read?
SOURCE
Original class graph and native offscreen camera captures, UE 5.7.4. Concept informed by Ben Cloward, Filtering Overlapping Objects: https://www.youtube.com/watch?v=ikhRzWHisEw

## 25. Building a fence spline tool
READ ALOUD
Build the fence tool in visible stages. First use a module length that matches the sample spacing. Next align each piece with the curve direction. Then inspect sharp turns, pivots and the endpoint. Rigid modules and deformed spline meshes solve different problems. These source captures show the progression and its failure cases, rather than a list of mysterious troubleshooting rules.
VISUAL REFERENCE
Ben Cloward episode 08, instructor’s ordered source captures. Rigid and deformed fence pieces behave differently.

## 26. Graph instances
A graph defines reusable operations. A graph instance refers to that graph and stores parameter values. A component can override values for one actor. The upper graph and instance panel show reference interfaces; the scene is our separate class forest example. Follow the graph reference, inspect the overridden control, and then inspect the output.

## 27. Different biomes, one graph
READ ALOUD
These regions share the same parent placement graph. Their asset tables, instance presets and materials provide the regional identity. The framework is a compact biome-like teaching system. It does not simulate a complete ecosystem. New assets can need different scale and clearance settings even when the graph stays the same.
VISUAL REFERENCE
Actual class regions. Shared rules; different compatible assets, presets and materials.

## 28. DEMO: Unreal PCG trail
READ ALOUD
Open the trail example from Tools, Week 11 PCG Museum, Full trail exercise. Show the shared parent graph, then the three population actors. Demonstrate one change at a time. Keep the path visible so students can connect exclusions to their practical purpose. This is an editor-generated environment demo.

## 29. Modular pieces and assembly
READ ALOUD
A modular generator uses a vocabulary of authored pieces and rules for combining them. A grammar is a formal way to describe allowed replacements or arrangements. Our building demo uses explicit assembly rules; we are not claiming it implements a grammar solver. The connection and dimension rules let the modules form a structure instead of a random scatter.
SOURCES
https://www.pcgbook.com/chapter01.pdf
Source: [{"creator":"Elyssa Chou / SideFX","source":"https://www.sidefx.com/tutorials/caelus/"},{"creator":"Elyssa Chou / SideFX","source":"https://www.sidefx.com/tutorials/caelus/"},{"creator":"Elyssa Chou / SideFX","source":"https://www.sidefx.com/tutorials/caelus/"},{"creator":"Elyssa Chou / SideFX","source":"https://www.sidefx.com/tutorials/caelus/"}]

## 30. Building variations
READ ALOUD
The class building graph creates a rectangular cell structure. It removes internal faces, places compatible facade modules and moves the flat roof above the top floor. Different dimensions reuse the same rules. This is an original teaching graph informed by course study, not a redistribution of the Udemy building project. Entrances, circulation and pitched roofs remain outside its current scope.

## 31. DEMO: Unreal PCG building generator
READ ALOUD
Open Tools, Week 11 PCG Museum, Building examples. Select Lodge and its PCG component. Change Cells from three by four bays and two floors to five by two bays and three floors. Regenerate, show how the roof follows the top floor, and restore the baseline. Then show that the same graph produces Cabin and Tower. Keep the flat-roof and rectangular-footprint limits explicit.

## 32. Wave Function Collapse
READ ALOUD
Wave Function Collapse is a different generation technique from our scatter graph. It chooses an option, updates the neighboring possibilities and repeats. If a cell has no permitted option, the implementation needs a recovery policy such as restarting or backtracking. Local compatibility does not guarantee a connected or playable level. The animation comes from the original implementation.
SOURCES
https://github.com/mxgmn/WaveFunctionCollapse
VISUAL REFERENCE
Maxim Gumin: WaveFunctionCollapse. Local compatibility still needs gameplay validation.

## 33. Custom nodes receive PCG datasets
A custom PCG node calls a Blueprint class that implements PCG processing. It receives tagged datasets, runs your logic, and returns PCG datasets to downstream nodes. One pin can carry several datasets. Selecting three points from each of two datasets produces six points. Decide whether a control applies per dataset or across the full input. In Unreal 5.7, new implementations can derive from PCGBlueprintBaseElement and override Execute. The older reference shown uses Execute Blueprint and a legacy Blueprint element.
Sources: Brandon Vox, Unreal Engine PCG course, custom-node demonstration; Epic Games PCG Blueprint API.

## 34. Return reusable PCG data
Return data another PCG node can use. Initialize the output from its input so metadata remains valid. Preserve transforms and attributes needed downstream. Return each dataset on the correct named output pin, then connect it to a mesh spawner and inspect the result.
Sources: Brandon Vox, Unreal Engine PCG course, custom-node demonstration; Epic Games PCG Blueprint API.

## 35. PCG performance
PCG performance matters in three places. Editor generation affects iteration and responsiveness. Runtime generation uses a gameplay budget if generation runs during play. The generated assets still cost memory, rendering, collision and sometimes tick work. Profile the packaged game on the target device. A saved or detached result avoids certain generation work but retains its asset costs.

## 36. Keep a generated result
For a static result, generate and inspect the scene first. Preserve an editable source copy, then use Clear PCG Link on the PCG component to move generated resources under a new actor and detach them from that component. Save the resulting actors and assets. Check the packaged game. This freezes the output relationship; it does not optimize meshes, materials, shadows or collision. Keeping an editor-generated result and explicitly detaching it are different choices. Runtime generation creates or updates content during play.
Verified against installed Unreal Engine 5.7 PCGComponent.h, ClearPCGLink.
https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/PCG/UPCGComponent/ClearPCGLink

## 37. Far Cry 5 world generation
READ ALOUD
Etienne Carrier’s GDC talk describes procedural world generation for Far Cry 5. The team used Houdini and Houdini Engine with Ubisoft’s Dunia engine. This supports the production argument for reusable rules and fine-tuning during world revisions. It is a supporting example, not the main implementation reference for our Unreal PCG demo.
SOURCES
https://www.gdcvault.com/play/1025215/Procedural-World-Generation-of-Far
https://blog.playstation.com/?p=199418
VISUAL REFERENCE
Etienne Carrier, Ubisoft, GDC 2018. Houdini/Dunia workflow, not Unreal PCG.

## 38. Diablo II level design
READ ALOUD
Diablo II uses random generation for levels, monsters and treasure. Erich Schaefer’s postmortem describes how that variation supports replay and how much testing its combinations required. This is a gameplay application of proceduralism, beyond placing decorative objects. A different layout is only useful if the resulting play experience works.
ASK
What would you validate in a generated dungeon that our scenery generator does not test?
SOURCES
https://www.gamedeveloper.com/design/postmortem-blizzard-s-i-diablo-ii-i-
VISUAL REFERENCE
Erich Schaefer, Diablo II postmortem (2000). Environment image from the original article.
IMAGE: Diablo II: Resurrected (2021), Blizzard Entertainment. Remaster screenshot; the design discussion concerns Diablo II.
https://blizzard.gamespress.com/en/Kit/Details/Diablo-II-Resurrected-Launch-Press-Kit

## 39. Dead Cells: authored rooms, varied levels
READ ALOUD
Dead Cells is a useful example of choosing the boundary between authored and generated work. Its lead designer describes a fully procedural prototype that felt incoherent, then a hybrid using hand-designed room chunks and procedural assembly. The lesson is not that the shipped game abandoned proceduralism. Reserve the parts that need deliberate pacing or composition, and generate variation where it improves play.
ASK
Which part of your project would lose value if it changed on every generation?
SOURCES
https://www.gamedeveloper.com/design/building-the-level-design-of-a-procedurally-generated-metroidvania-a-hybrid-approach-
VISUAL REFERENCE
Sebastien Bénard, 2017 developer article. Authored rooms plus procedural assembly.
IMAGE: Motion Twin, Dead Cells official Steam screenshots.
https://store.steampowered.com/app/588650/Dead_Cells/

## 40. Houdini beyond scattering
READ ALOUD
Houdini is a separate procedural authoring application used in games and film. Its granular geometry and attribute operations let skilled artists build high-quality assets and precise reusable systems. It supports much more than scattering: procedural modeling, rigging and animation, effects and simulation. That depth takes expertise; it is not an automatic quality guarantee. Students do not need Houdini for this class.
SOURCES
https://www.sidefx.com/products/houdini/
Houdini is used in games and film. More granular control makes sophisticated assets possible for artists with the expertise; it does not automatically make a high-quality result. We are introducing possibilities, not teaching an internal network.
VISUAL REFERENCE
Official SideFX example. Inspiration for possible future tools, not a student setup requirement.

## 41. Anastasia Opara: Procedural Lake Houses
READ ALOUD
Anastasia Opara is a technical artist whose Procedural Lake Houses series shows how deeply a procedural system can shape an asset. This chapter overview progresses from a base form through module placement, weathering, then set dressing and shading. It is a useful example of Houdini beyond a simple fence HDA.
The shape is only part of the deliverable. Our own generators also need valid UVs, sensible material assignments and consistent texture scale when dimensions change. Exported assets need useful normals, pivots and collision as well. This general production checklist is our teaching synthesis; the still does not establish the implementation of each UV operation.
Anthony has the downloaded chapter videos for further study. Students do not need to install Houdini or buy this course for the UE exercise. This is a brief credited teaching excerpt, not a redistribution of the paid course or its project files.
ASK
If a generator doubles a wall's width, what should happen to its texture scale and windows?
SOURCES
https://www.sidefx.com/tutorials/procedural-lake-houses-volume-1/
https://anopara.gumroad.com/l/qaEZ
Local source: C:/Users/antho/Downloads/Ch2_Part0_Intro.mp4, 00:12. Unaltered pixels cropped to the four-stage overview.

## 42. Procedural animation
READ ALOUD
Procedural thinking also applies to movement. A foot-placement rule can adapt a pose to the ground. Retargeting can adapt an animation to a different character structure. Physical simulation can compute motion from forces and constraints. This SideFX Dynamic Motion example shows procedural motion tools; it does not mean every frame of every animation must be generated from scratch.
SOURCES
https://www.sidefx.com/products/whats-new-in-h20/animation/
VISUAL REFERENCE
SideFX Houdini 20 Dynamic Motion example. Optional final-project inspiration.

## 43. Houdini tools inside Unreal
A Houdini Digital Asset packages a procedural tool for use inside Unreal through Houdini Engine. Here the artist changes a building input and the tool rebuilds the facade and roof. Cooking recalculates the tool; baking keeps a native Unreal result.
Source: SideFX Project Titan EVO. https://www.sidefx.com/titan-evo/

## 44. FINAL PROJECT CHECK-IN
READ ALOUD
Your final project project check-in is due before class next week. Show the current project, demonstrate what works, and identify the next issue you will test. A procedural feature is optional inspiration, not a new requirement for the final project.

## 45. Procedural ideas for your final project
READ ALOUD
Choose a small feature that supports the project you already intend to make. Start with one clear input, one useful control and one observable requirement. You do not need to attempt a large biome generator or learn Houdini overnight. A narrow tool that can be revised and explained is a stronger project contribution than a broad system that is difficult to control.
ASK
What would be the smallest useful procedural feature for your existing project?

## 46. Sources: Unreal and production
READ ALOUD
These are the implementation and production references used in the lecture. The actual class project is an original, editable Unreal 5.7 teaching example. A production screenshot supports an explanation of that production’s system; it does not prove that our project implements the same technology.
SOURCES
https://www.unrealengine.com/electric-dreams-environment?lang=en-US
https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-overview
https://www.guerrilla-games.com/read/gpu-based-procedural-placement-in-horizon-zero-dawn
https://www.gdcvault.com/play/1025215/Procedural-World-Generation-of-Far

## 47. Sources: methods and applications
READ ALOUD
Use the linked primary references for further study. The course captures remain attributed teaching studies. Do not redistribute paid course files or describe a tutorial network as our original work. Graphic and icon provenance, image-stage notes and licensing are recorded in the preparation materials.
SOURCES
https://www.pcgbook.com/chapter01.pdf
https://github.com/mxgmn/WaveFunctionCollapse
https://www.gamedeveloper.com/design/postmortem-blizzard-s-i-diablo-ii-i-
https://www.gamedeveloper.com/design/building-the-level-design-of-a-procedurally-generated-metroidvania-a-hybrid-approach-
https://www.sidefx.com/docs/houdini/unreal/intro.html
https://www.youtube.com/@BenCloward
https://www.udemy.com/course/unreal-engine-pcg-english/
ADDITIONAL VISUAL CREDITS
Guest EVE Vanguard image: supplied Amritha Immaneni deck, CCP Games. Surface breakdown: Malte Ekvall, Path of the Pilgrim. Icons: Lucide, ISC with Feather-origin MIT notices. Original schematic sources and generated cover provenance are included with the preparation files. Paid course captures are attributed teaching excerpts; the custom-node pseudocode and class graphs are original.
LAKE HOUSES
Technical artist Anastasia Opara. https://www.sidefx.com/tutorials/procedural-lake-houses-volume-1/
https://anopara.gumroad.com/l/qaEZ

## 48. Custom PCG nodes
READ ALOUD
A graph instance changes the settings of existing rules. A custom PCG node lets us write another operation in Blueprint. In this course example, the author exposes Number of Points. One selects one location; three selects three. The node has separate outputs for the selected points and the points left over. The markers shown here are debug points, not spawned camp assets.
A practical extension to our trail would choose three camp locations from points that already satisfy the terrain and path-clearance rules. A percentage filter changes the chance that a point survives. A fixed-count operation expresses a different requirement. Changing the seed chooses another subset while the requested count remains fixed, provided enough suitable points exist.
DISCUSSION
What happens if two point datasets enter with Number of Points set to three? The course implementation applies the count to each dataset, so it can return six points. Show the optional dataset slide if useful.
SOURCES
https://www.udemy.com/course/unreal-engine-pcg-english/
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/PCGBlueprintBaseElement?application_version=5.7
https://dev.epicgames.com/community/learning/knowledge-base/l574/unreal-engine-pcg-blueprint-elements-in-5-7
TEACHING FOCUS
In Unreal Engine 5.7, a custom Blueprint PCG operation can expose named inputs, outputs and artist-editable settings. Explain the requirement and the visible result before inspecting its implementation. This slide is a course reference; the supplied starter uses its native graphs.

## 49. Procedural tools expose controls to the artist
READ ALOUD
AI can propose an image, an asset or a set of settings. A procedural tool exposes controls the artist or developer can deliberately change: building dimensions, reserved regions, mesh selection or distribution. These approaches can work together. The useful question for a final project is which decisions the creator needs to control and how the tool makes those decisions available.
ASK
Which control would make your own tool more useful to another artist?

## 50. GUIDED EXERCISE: change the scrub density
READ ALOUD
Use the supplied project and assets. This is one controlled change, not a new graph-building assignment. Everyone works on the scrub actor. Keep the seed and all other inputs fixed. Ask students to predict the result before generating, then restore the supplied values. Optional asset swaps and moved splines belong after the guided task.
ASK
Why does KeepFraction = 0.50 not promise exactly half as many final meshes?
VISUAL REFERENCE
Student-Lab.html has the exact steps. No extra asset download or plugin setup.

## 51. OPTIONAL: node order changes the result
READ ALOUD
These operations can produce different accepted subsets. If points inside an exclusion participate in pruning first, they can remove nearby points even though they are later discarded. State the intended semantics before choosing the order. 

## 52. OPTIONAL: slope is a dot-product test
READ ALOUD
For a unit surface normal and unit world-up vector, the dot product is the cosine of the angle between them. A minimum of about 0.94 corresponds to accepting slopes up to about twenty degrees. Read the surface normal after projection, before restoring upright tree rotations. This test measures orientation; it does not assess whether a whole tree footprint fits.