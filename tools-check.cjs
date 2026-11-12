const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const root = __dirname, project = path.join(root, 'Unreal/Week11PCGTrail');
for (const f of ['README.md','START-HERE.html','Student-Lab.md','SOURCES.md']) assert(fs.existsSync(path.join(root,f)),f);
const config=JSON.parse(fs.readFileSync(path.join(project,'Week11PCGTrail.uproject')));
assert.equal(config.EngineAssociation,'5.7');
assert(!config.AdditionalPluginDirectories);
assert(!config.Modules);
assert(!config.Plugins.some(p=>p.Name==='TrailBiomeAuthoring'||p.Name==='HoudiniEngine'));
for(const p of ['PCG','PythonScriptPlugin','EditorScriptingUtilities']) assert(config.Plugins.some(x=>x.Name===p&&x.Enabled),p);
const ini=fs.readFileSync(path.join(project,'Config/DefaultEngine.ini'),'utf8');
assert(!/SecurityToken\s*=[^\r\n\s]+/.test(ini),'Do not publish generated Android credentials.');
assert(ini.includes('EditorStartupMap=/Game/Trail/Museum/Maps/PCG_Museum'));
assert(ini.includes('DefaultGraphicsRHI=DefaultGraphicsRHI_DX12'));
assert(ini.includes('+D3D12TargetedShaderFormats=PCD3D_SM6'),'Nanite needs SM6 configured in the project; students must not have to enable it manually.');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'Instructor/project-manifest.json')));
assert.equal(manifest.root_maps.length,20);
for(const r of manifest.files){
 const f=path.join(project,r.file);assert(fs.existsSync(f),r.file);const bytes=fs.readFileSync(f);
 assert.equal(bytes.length,r.bytes,r.file);assert(bytes.length<95*1024*1024,r.file);
 assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),r.sha256,r.file);
}
for(const f of ['README.md','Student-Lab.md','SOURCES.md']){
 const text=fs.readFileSync(path.join(root,f),'utf8');
 for(const match of text.matchAll(/!?\[[^\]]*\]\(([^)]+)\)/g)){
  const url=match[1];if(/^(https?:|#)/.test(url))continue;
  assert(fs.existsSync(path.resolve(root,url.split('#')[0])),`${f}: ${url}`);
 }
 assert(!/Install_FabAssets|Setup_FabAssets|run Fab setup/.test(text),`Outdated setup in ${f}`);
}
console.log(`PASS: ${manifest.files.length} native packages verified; 20 maps; links, stock-plugin setup and source hashes checked.`);

// Reject retired asset-acquisition instructions anywhere in the shipped documentation.
function checkDocs(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){if(entry.name==='.git')continue;const f=path.join(dir,entry.name);if(entry.isDirectory())checkDocs(f);else if(/\.(md|html|py|ps1)$/i.test(f)){const text=fs.readFileSync(f,'utf8');assert(!/acquired separately by each student|not redistributed in the starter ZIP|Install_FabAssets|Setup_FabAssets|run Fab setup/i.test(text),`Obsolete asset setup instructions: ${f}`);}}}
checkDocs(root);
assert.equal(manifest.dependencies_bundled,true);
assert.deepEqual(manifest.missing_packages,[]);
assert(fs.existsSync(path.join(root,'Slides/Week11-PCG.pptx')),'Include the local PowerPoint review copy.');
