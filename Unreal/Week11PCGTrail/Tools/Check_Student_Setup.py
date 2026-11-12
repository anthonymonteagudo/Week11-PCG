"""Check the student scene inputs without generating or changing the scene."""
import unreal as ue,json,math
from pathlib import Path
ROOT=Path(ue.Paths.project_dir())
def run():
 levels=ue.get_editor_subsystem(ue.LevelEditorSubsystem)
 world=ue.get_editor_subsystem(ue.UnrealEditorSubsystem).get_editor_world()
 assert world.get_name() in ['Trail_Student','Biome_OpenDesert','Biome_JuniperScrub','Biome_RockyWash','Biome_Forest','Biome_Snow'] or world.get_name().startswith('Variation_'),'Open the student map or a supplied biome example first.'
 actors=ue.get_editor_subsystem(ue.EditorActorSubsystem).get_all_level_actors();named={a.get_actor_label():a for a in actors}
 terrain=named.get('Trail_Terrain');assert terrain and terrain.actor_has_tag('TrailTerrain'),'Terrain actor/tag is missing.'
 assert terrain.static_mesh_component.get_editor_property('static_mesh'),'Terrain mesh is missing.'
 assert terrain.static_mesh_component.get_collision_enabled()!=ue.CollisionEnabled.NO_COLLISION,'Terrain collision is disabled.'
 sets={};parameters={};H=ue.PCGGraphParametersHelpers
 for name in ['Trees','Rocks','Scrub']:
  a=named.get('PCG_'+name);assert a,'Missing PCG_'+name
  c=a.get_component_by_class(ue.PCGComponent);assert c
  interface=c.get_editor_property('graph_instance');assert isinstance(interface,ue.PCGGraphInstance)
  preset=interface.get_editor_property('graph');assert isinstance(preset,ue.PCGGraphInstance),'The actor must reference a supplied graph-instance preset.'
  parent=preset.get_editor_property('graph');assert isinstance(parent,ue.PCGGraph) and parent.get_path_name().split('.')[0]=='/Game/Trail/Biome/PCG_BiomeScatter','All layers must share PCG_BiomeScatter.'
  spacing=H.get_double_parameter(interface,'SpacingCm');low=H.get_double_parameter(interface,'ScaleMin');high=H.get_double_parameter(interface,'ScaleMax')
  assert 300<=spacing<=2400,'Candidate spacing must stay between 300 and 2400 cm.'
  assert .2<=low<=high<=1.2,'Uniform scale must satisfy 0.2 <= minimum <= maximum <= 1.2.'
  natural={k:H.get_double_parameter(interface,k) for k in ['PatchCutoff','KeepFraction','SlopeMinDot','PruneRadiusCm']}
  assert all(0<=natural[k]<=1 for k in ['PatchCutoff','KeepFraction','SlopeMinDot']),'Patch cutoff, survival and flatness must be in 0–1.'
  assert 0<=natural['PruneRadiusCm']<=500,'Pruning neighborhood must be in 0–500 cm.'
  natural['FavorClearings']=H.get_bool_parameter(interface,'FavorClearings')
  region_inputs={}
  for key in ['HabitatTag','ClearingTag']:
   input_tag=str(H.get_name_parameter(interface,key));matches=[a for a in actors if a.actor_has_tag(input_tag)];assert len(matches)>=2,'Expected multiple closed spline inputs for '+key+': '+input_tag
   for region_actor in matches:
    curve=region_actor.get_component_by_class(ue.SplineComponent);assert curve and curve.is_closed_loop() and curve.get_number_of_spline_points()>=3,'Every habitat/clearing input must be a closed spline.'
   region_inputs[key]={'tag':input_tag,'actors':[a.get_actor_label() for a in matches]}
  table=H.get_object_parameter(interface,'AssetSet');assert isinstance(table,ue.DataTable),'Choose a mesh and weight DataTable.'
  rows=json.loads(ue.DataTableFunctionLibrary.export_data_table_to_json_string(table));assert rows,'The asset table is empty.'
  assert all('Mesh' in r and 'Weight' in r for r in rows),'Choose a supplied biome table with Mesh and Weight columns.'
  positive=[r for r in rows if float(r.get('Weight',-1))>0]
  assert positive and all(float(r.get('Weight',-1))>=0 for r in rows),'Weights must be nonnegative, with at least one positive entry.'
  meshes=[ue.load_asset(r['Mesh']) for r in positive];assert all(isinstance(m,ue.StaticMesh) for m in meshes),'Missing bundled meshes: re-extract the complete student ZIP or restore the repository checkout.'
  tag=str(H.get_name_parameter(interface,'ReservationTag'));reservation=named.get(tag)
  assert reservation and reservation.actor_has_tag(tag),'Missing reservation/tag for '+name
  s=reservation.get_component_by_class(ue.SplineComponent);assert s and s.is_closed_loop(),'Reservation must be closed.'
  assert tag in ['Reserve_Trees','Reserve_Rocks','Reserve_Scrub'],'Choose a supplied prepared reservation.'
  radius=max(math.hypot(abs(m.get_bounds().origin.x)+m.get_bounds().box_extent.x,abs(m.get_bounds().origin.y)+m.get_bounds().box_extent.y) for m in meshes)
  width={'Reserve_Trees':850,'Reserve_Rocks':600,'Reserve_Scrub':500}[tag]
  assert radius*high+275<=width,'Chosen asset set and maximum scale exceed this reservation margin. Choose a compatible preset before generating.'
  sets[name]=[m.get_path_name() for m in meshes]
  parameters[name]={'instance':preset.get_path_name(),'spacing_cm':spacing,'scale_min':low,'scale_max':high,'variation_seed':H.get_int32_parameter(interface,'VariationSeed'),'asset_table':table.get_path_name(),'reservation_tag':tag,'natural_controls':natural,'region_inputs':region_inputs}
 for stem in ['Dirt','Grass_Mix','Rocks']:
  for suffix in ['ALB','NRM','RMA']:assert ue.load_asset('/Game/Northwood/Textures/Landscape/TX_'+stem+'_01a_'+suffix),'Missing bundled surface textures: restore the complete student project.'
 report={'status':'READY','map':world.get_name(),'parent_graph':'/Game/Trail/Biome/PCG_BiomeScatter','asset_sets':sets,'parameters':parameters,'note':'Inputs checked. Generate and inspect final placement after changes.'}
 (ROOT/'StudentSetupCheck.json').write_text(json.dumps(report,indent=2));ue.log('TRAIL_STUDENT_SETUP_READY')
 return report
if __name__=='__main__':run()
