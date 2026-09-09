from pathlib import Path

path = Path('src/bunker17.js')
s = path.read_text(encoding='utf-8')

needle = "async function buildRoom(){\n  for(let x=-4.5;x<=4.5;x+=1.8)for(let z=-4.2;z<=4.2;z+=1.8)await fit(paths.floor,[x,0,z],[1.72,.12,1.72]);"
replacement = "async function buildRoom(){\n  const crackedFloorTexture = await new Promise((resolve,reject)=>{\n    textureLoader.load('./assets/textures/cracked_asphalt_floor.jpg', tex=>{\n      tex.colorSpace=THREE.SRGBColorSpace;\n      tex.wrapS=THREE.ClampToEdgeWrapping; tex.wrapT=THREE.ClampToEdgeWrapping;\n      tex.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy?.()||4);\n      resolve(tex);\n    },undefined,reject);\n  }).catch(()=>null);\n  for(let x=-4.5;x<=4.5;x+=1.8)for(let z=-4.2;z<=4.2;z+=1.8){\n    const floorObj=await fit(paths.floor,[x,0,z],[1.72,.12,1.72]);\n    if(floorObj&&crackedFloorTexture){\n      floorObj.traverse(n=>{if(!n.isMesh)return; n.material=new THREE.MeshStandardMaterial({map:crackedFloorTexture,roughness:.96,metalness:.02}); n.receiveShadow=true;});\n    }\n  }"

if needle not in s:
    raise SystemExit('Floor loop pattern not found; no changes made.')

s = s.replace(needle, replacement, 1)
path.write_text(s,encoding='utf-8')
print('Applied cracked asphalt texture to Bunker 17 floor tiles.')
