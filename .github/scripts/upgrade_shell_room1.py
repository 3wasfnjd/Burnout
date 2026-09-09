from pathlib import Path
p=Path('src/main.js')
s=p.read_text()
old="function shell(i){const a=rooms[i][2],wide=i===8?18.5:(i===5?17.8:17),depth=i===9?9.6:8.9;box(wide,.65,depth,M.rock,0,-.48,.05);box(wide,5.9,.8,M.rock,0,2.3,-4.05);box(.9,5.9,depth,M.rock,-wide/2+.25,2.3,.05);box(wide-1.3,.28,depth-1.35,M.floor,.2,-.08,.05);for(let x=-wide/2+.8;x<wide/2-.8;x+=1.25)for(let z=-2.75;z<3;z+=1.18)box(1.16,.025,1.08,Math.random()>.45?M.floor:mat(0x6a5c4d,.98),x,.08,z);for(let x=-wide/2+.4;x<wide/2-.4;x+=.58)rock(x,-.02,3.38,.28+Math.random()*.2);for(let x=-6.2;x<=2.7;x+=2.25)qfit('Walls/WallAstra_Straight.gltf',x,.12,-3.42,2.15,4.45,.42);qfit('Walls/TopCables_Straight_Hanging.gltf',-1.7,4.1,-3.12,2.2,.65,.5);lamp(-4.7,3.8,-2.2,a,5,5);lamp(2.1,3.8,-2.2,a,5,5)}"
new="""function shell(i){const a=rooms[i][2],wide=i===8?18.5:(i===5?17.8:17),depth=i===9?9.6:8.9;if(i===0){
// Room 1: engineered bunker shell. Rock is kept outside; the playable interior is modular metal.
box(wide,.55,depth,M.rock,0,-.55,.05);box(wide,5.9,.72,M.rock,0,2.3,-4.18);box(.82,5.9,depth,M.rock,-wide/2+.18,2.3,.05);
// continuous dark structural slab below modular deck
box(wide-1.15,.18,depth-1.05,M.dark,.15,-.02,.08);
// real Quaternius modular floor plates instead of procedural square tiles
for(let x=-6.5;x<=6.5;x+=2.15)for(let z=-2.55;z<=2.55;z+=1.7)qfit('Platforms/Platform_DarkPlates.gltf',x,.075,z,2.05,.13,1.58,0,false);
// wall system: Astra panels plus metal base rails and upper cable raceway
for(let x=-6.35;x<=3.0;x+=2.2){qfit('Walls/WallAstra_Straight.gltf',x,.12,-3.47,2.16,4.42,.38);qfit('Walls/BottomMetal_Straight.gltf',x,.10,-3.20,2.16,.38,.30)}
qfit('Walls/TopCables_Straight_Hanging.gltf',-4.25,4.02,-3.14,2.15,.62,.48);qfit('Walls/TopCables_Straight_Hanging.gltf',-1.95,4.02,-3.14,2.15,.62,.48);qfit('Walls/TopCables_Straight_Hanging.gltf',.35,4.02,-3.14,2.15,.62,.48);
// exposed rock only at the cutaway/front edge, not as an interior finish
for(let x=-wide/2+.45;x<wide/2-.45;x+=.68)rock(x,-.10,3.62,.25+Math.random()*.14);
lamp(-4.7,3.72,-2.35,a,4.2,5);lamp(1.7,3.72,-2.35,a,4.2,5);return}
box(wide,.65,depth,M.rock,0,-.48,.05);box(wide,5.9,.8,M.rock,0,2.3,-4.05);box(.9,5.9,depth,M.rock,-wide/2+.25,2.3,.05);box(wide-1.3,.28,depth-1.35,M.floor,.2,-.08,.05);for(let x=-wide/2+.8;x<wide/2-.8;x+=1.25)for(let z=-2.75;z<3;z+=1.18)box(1.16,.025,1.08,Math.random()>.45?M.floor:mat(0x6a5c4d,.98),x,.08,z);for(let x=-wide/2+.4;x<wide/2-.4;x+=.58)rock(x,-.02,3.38,.28+Math.random()*.2);for(let x=-6.2;x<=2.7;x+=2.25)qfit('Walls/WallAstra_Straight.gltf',x,.12,-3.42,2.15,4.45,.42);qfit('Walls/TopCables_Straight_Hanging.gltf',-1.7,4.1,-3.12,2.2,.65,.5);lamp(-4.7,3.8,-2.2,a,5,5);lamp(2.1,3.8,-2.2,a,5,5)}"""
if old not in s: raise SystemExit('shell block not found')
s=s.replace(old,new)
old2="function door(type=0){const x=5.6;if(type===2){box(3.4,4.4,.45,M.metal,x,2.2,-3.0);const ring=new THREE.Mesh(new THREE.TorusGeometry(1.05,.16,12,28),M.dark);ring.position.set(x,2.1,-2.7);add(ring);box(2.1,2.1,.22,M.dark,x,2.1,-2.68)}else{qfit('Platforms/Door_Frame_A.gltf',x,.1,-3.05,3.2,4.4,.75);qfit('Platforms/Door_DarkMetal.gltf',x,.2,-2.75,2.35,3.35,.3);if(type===1){box(.22,3.1,.22,M.yellow,4.05,1.7,-2.68);box(.22,3.1,.22,M.yellow,7.1,1.7,-2.68)}}qfit('Props/Prop_AccessPoint.gltf',4.15,.48,-2.55,.8,1.05,.35);lamp(x,4.05,-2.35,rooms[roomIndex][2],9,7)}"
new2="""function door(type=0){const x=5.6;if(roomIndex===0&&type===0){
// Room 1 uses a heavier square blast-door assembly, integrated into the wall.
qfit('Platforms/Door_Frame_SquareTall.gltf',x,.08,-3.16,3.45,4.58,.82);qfit('Platforms/Door_Metal.gltf',x,.18,-2.78,2.62,3.52,.34);
qfit('Walls/BottomMetal_Straight.gltf',3.78,.10,-3.18,1.18,.38,.30);qfit('Walls/BottomMetal_Straight.gltf',7.40,.10,-3.18,1.18,.38,.30);
qfit('Props/Prop_AccessPoint.gltf',3.78,.58,-2.58,.76,1.08,.34);lamp(x,4.13,-2.38,rooms[roomIndex][2],6.5,5.5);return}
if(type===2){box(3.4,4.4,.45,M.metal,x,2.2,-3.0);const ring=new THREE.Mesh(new THREE.TorusGeometry(1.05,.16,12,28),M.dark);ring.position.set(x,2.1,-2.7);add(ring);box(2.1,2.1,.22,M.dark,x,2.1,-2.68)}else{qfit('Platforms/Door_Frame_A.gltf',x,.1,-3.05,3.2,4.4,.75);qfit('Platforms/Door_DarkMetal.gltf',x,.2,-2.75,2.35,3.35,.3);if(type===1){box(.22,3.1,.22,M.yellow,4.05,1.7,-2.68);box(.22,3.1,.22,M.yellow,7.1,1.7,-2.68)}}qfit('Props/Prop_AccessPoint.gltf',4.15,.48,-2.55,.8,1.05,.35);lamp(x,4.05,-2.35,rooms[roomIndex][2],9,7)}"""
if old2 not in s: raise SystemExit('door block not found')
s=s.replace(old2,new2)
p.write_text(s)
