"""Comment and arrange current native graphs. Preserve rules and old node titles."""
import unreal as u,json,traceback
from pathlib import Path
R=Path(u.Paths.project_dir());O=R/'Validation/MuseumPass';A=u.EditorAssetLibrary;bridge=u.TrailBiomeAuthoringLibrary
try:
 g=A.load_asset('/Game/Trail/Biome/PCG_BiomeScatter');nodes={str(n.node_title):n for n in g.nodes}
 chain=['01 Candidates','02 Variation','02e Keep points in habitat','02h Subtract clearings','05 Protect the trail','07 Ground contact','08a Ground suitability','08b Reject steep ground','08c Restore upright rotation','08d Shared habitat patches','08e Open habitat gaps','08f Select survivors','08g Local influence bounds','08h Resolve local crowding','09 Choose asset','10 Spawn selected mesh']
 comments={
 '01 Candidates':'Candidate spacing sets the proposal budget. It does not guarantee final mesh separation.',
 '02 Variation':'Bounded jitter breaks the grid. A shared variation seed makes a controlled comparison repeatable.',
 '02e Keep points in habitat':'Union the selected closed habitat islands, then intersect the candidates with that surface.',
 '02h Subtract clearings':'Remove the union of selected clearing interiors. Point rejection does not repaint the terrain.',
 '05 Protect the trail':'Reject roots inside the prepared wider trail reservation. Final mesh bounds need a separate clearance check.',
 '07 Ground contact':'Project onto the tagged terrain collision, transferring position and surface normal before suitability.',
 '08a Ground suitability':'Dot the projected normal with world up. One means flat; smaller values indicate steeper ground.',
 '08b Reject steep ground':'SlopeMinDot filters the surface normal before orientation is restored.',
 '08c Restore upright rotation':'Plants stand upright while yaw varies. Keep this after normal-based suitability.',
 '08d Shared habitat patches':'World-space noise breaks occupancy into shared patches. This is distribution, not asset choice.',
 '08e Open habitat gaps':'PatchCutoff selects occupied parts. FavorClearings uses the complementary mask for rocks.',
 '08f Select survivors':'KeepFraction randomly thins eligible candidates. It is an expected fraction, not a final quota.',
 '08g Local influence bounds':'PruneRadiusCm controls point influence boxes. These are not full mesh collision bounds.',
 '08h Resolve local crowding':'Resolve competition within this population. Separate layers do not automatically prune against one another.',
 '09 Choose asset':'Choose a compatible Mesh row with relative Weight after placement decisions. Weight is not an exact count.',
 '10 Spawn selected mesh':'Render the accepted points using Mesh metadata. Inspect points before judging the result.'}
 for i,title in enumerate(chain):
  assert title in nodes,title;n=nodes[title];n.set_node_position(i*550,0);bridge.comment_node(n,comments[title]);n.node_title_color=u.LinearColor(.08,.38,.34,1)
 extras={'02b Closed habitat regions':(0,-1100),'02c Spline interiors':(550,-1100),'02d Union habitat islands':(1100,-1100),'02f Multiple clearing splines':(550,-1800),'02g Closed clearing interiors':(1100,-1800),'03 Trail reservation':(1100,-2500),'04 Closed reservation':(1650,-2500),'06 Terrain query':(2200,-650),'08 Mesh and weight table':(7150,650),'SpacingCm':(0,450),'ScaleMin':(550,450),'ScaleMax':(550,750),'ReservationTag':(550,-2500),'AssetSet':(6600,650),'HabitatTag':(-550,-1100),'ClearingTag':(0,-1800),'SlopeMinDot':(3850,450),'PatchCutoff':(5500,450),'KeepFraction':(6050,450),'PruneRadiusCm':(6600,450),'FavorClearings':(5500,750),'VariationSeed':(-550,1200)}
 for title,pos in extras.items():
  if title in nodes:nodes[title].set_node_position(*pos)
 # Real named reroutes: the hidden dependency edge is essential to compilation.
 if 'Variation seed bus' not in nodes:
  decl,ds=g.add_node_of_type(u.PCGNamedRerouteDeclarationSettings);decl.node_title='Variation seed bus';decl.set_node_position(0,1200);g.add_edge(nodes['VariationSeed'],'Out',decl,'In')
  for title in ['02 Variation','08c Restore upright rotation','08f Select survivors','09 Choose asset']:
   usage,us=g.add_node_of_type(u.PCGNamedRerouteUsageSettings);usage.node_title='Variation seed';us.set_editor_property('declaration',ds);x,y=nodes[title].get_node_position();usage.set_node_position(x-150,1050)
   assert 'InvisiblePin' in [str(p.properties.label) for p in decl.output_pins];assert 'In' in [str(p.properties.label) for p in usage.input_pins]
   g.add_edge(decl,'InvisiblePin',usage,'In');assert g.remove_edge(nodes['VariationSeed'],'Out',nodes[title],'Seed');g.add_edge(usage,'Out',nodes[title],'Seed')
 g.get_output_node().set_node_position(8800,0);g.set_editor_property('description','Reusable biome layer. Read the main point stream left to right. Closed habitat, clearing and trail queries sit above it; controls and asset profiles sit below it. Named seed reroutes share one reproducible control. Stock PCG runtime only.');A.save_loaded_asset(g,False)
 building=A.load_asset('/Game/Trail/Building/PCG_ModularBuilding')
 for n in building.nodes:
  title=str(n.node_title)
  if title.startswith('01 '):comment='Whole module counts are clamped before dependent dimensions are calculated. Actor scale stays one.'
  elif title.startswith('02 '):comment='Derived dimensions use the kit contract: 400 cm bays and 350 cm storeys. Half extents and offsets are different quantities.'
  elif title.startswith('03 '):comment='Construct local point datasets before applying the building actor transform.'
  elif title.startswith('05 '):comment='Coincident opposite interior faces cancel with hard point bounds and Binary Difference. Apply mesh pivot corrections afterwards.'
  elif title.startswith('06 '):comment='Adapt the measured pivot, axes or dimension of this specific module. Nonuniform scale must remain enabled for post height.'
  elif title.startswith('07 '):comment='Keep topology separate from the persistent facade collection. Compatible meshes share the same dimensional contract.'
  elif title.startswith('09 '):comment='Apply the building actor transform after local assembly. Rotation should move the complete result together.'
  else:continue
  bridge.comment_node(n,comment)
 A.save_loaded_asset(building,False)
 records=[]
 for folder in ['/Game/Trail/Biome','/Game/Trail/Building','/Game/Trail/Museum']:
  for path in A.list_assets(folder,recursive=True,include_folder=False):
   graph=A.load_asset(path)
   if isinstance(graph,u.PCGGraph):records.append({'path':path,'nodes':[{'title':str(n.node_title),'class':n.get_settings().get_class().get_name(),'position':list(n.get_node_position())} for n in graph.nodes]})
 (O/'graph-cleanup.json').write_text(json.dumps({'status':'PASS','graphs':records,'rule_changes':False,'named_seed_reroutes':True},indent=2))
except Exception:(O/'graph-cleanup.json').write_text(json.dumps({'status':'FAIL','error':traceback.format_exc()},indent=2));u.log_error(traceback.format_exc())
u.SystemLibrary.quit_editor()
