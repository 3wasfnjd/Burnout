from pathlib import Path

path = Path('src/bunker17.js')
s = path.read_text(encoding='utf-8')

old = """  for(let x=-4.5;x<=4.5;x+=1.8)for(let z=-4.2;z<=4.2;z+=1.8){
    const floorObj=await fit(paths.floor,[x,0,z],[1.72,.12,1.72]);
    if(floorObj&&crackedFloorTexture){
      floorObj.traverse(n=>{if(!n.isMesh)return; n.material=new THREE.MeshStandardMaterial({map:crackedFloorTexture,roughness:.96,metalness:.02}); n.receiveShadow=true;});
    }
  }"""

new = """  const floorXs=[-4.5,-2.7,-0.9,0.9,2.7,4.5];
  const floorZs=[-4.2,-2.4,-0.6,1.2,3.0];
  for(let zi=0;zi<floorZs.length;zi++)for(let xi=0;xi<floorXs.length;xi++){
    const floorObj=await fit(paths.floor,[floorXs[xi],0,floorZs[zi]],[1.72,.12,1.72]);
    if(floorObj&&crackedFloorTexture){
      const tileTex=crackedFloorTexture.clone();
      tileTex.wrapS=THREE.RepeatWrapping;
      tileTex.wrapT=THREE.RepeatWrapping;
      tileTex.repeat.set(1/floorXs.length,1/floorZs.length);
      tileTex.offset.set(xi/floorXs.length,1-(zi+1)/floorZs.length);
      tileTex.needsUpdate=true;
      floorObj.traverse(n=>{
        if(!n.isMesh)return;
        n.material=new THREE.MeshStandardMaterial({map:tileTex,roughness:.96,metalness:.02});
        n.receiveShadow=true;
      });
    }
  }"""

if old not in s:
    raise SystemExit('Expected cracked floor block not found')

s=s.replace(old,new,1)
path.write_text(s,encoding='utf-8')
print('Applied cracked asphalt as one continuous texture across BUNKER 17 floor tiles.')
