from pathlib import Path
p=Path('src/bunker17.js')
s=p.read_text()
s=s.replace("scene.fog = new THREE.FogExp2(0x08090a, 0.035);","scene.fog = new THREE.FogExp2(0x101214, 0.012);")
s=s.replace("renderer.toneMappingExposure = 1.42;","renderer.toneMappingExposure = 1.95;")
s=s.replace("const ambient = new THREE.HemisphereLight(0x9aabb2, 0x17130f, 0.72);","const ambient = new THREE.HemisphereLight(0xd7e4ea, 0x2a2119, 1.35);")
s=s.replace("const l = new THREE.PointLight(0xffd6a3, 1.15, 10, 1.7);","const l = new THREE.PointLight(0xffd8ad, 3.2, 13, 1.55);")
s=s.replace("const emergency = new THREE.PointLight(0xff2b20, 3.5, 11, 2);","const emergency = new THREE.PointLight(0xff3a2e, 1.4, 10, 2);")
needle="scene.add(ambient);\n"
insert="scene.add(ambient);\nconst fillLight = new THREE.DirectionalLight(0xcfe7f2, 1.5);\nfillLight.position.set(2.5, 5.5, 4.5);\nscene.add(fillLight);\nconst warmFill = new THREE.DirectionalLight(0xffc58c, 0.95);\nwarmFill.position.set(-4.5, 3.5, -1.5);\nscene.add(warmFill);\n"
if "const fillLight = new THREE.DirectionalLight" not in s:
    s=s.replace(needle,insert)
s=s.replace("scene.fog=new THREE.FogExp2(0x08090a,.035);","scene.fog=new THREE.FogExp2(0x101214,.012);")
p.write_text(s)
