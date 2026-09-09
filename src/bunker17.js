import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { VRButton } from 'three/addons/webxr/VRButton.js';
import { ARManager } from './ARManager.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x080a0b);
scene.fog = new THREE.FogExp2(0x101214, 0.012);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.95;
renderer.xr.enabled = true;
renderer.xr.setReferenceSpaceType('local-floor');
document.body.prepend(renderer.domElement);

const camera = new THREE.PerspectiveCamera(66, innerWidth / innerHeight, 0.05, 80);
const player = new THREE.Group();
player.position.set(0, 1.66, 3.9);
player.add(camera);
scene.add(player);

const room = new THREE.Group();
scene.add(room);

const assetManager = new THREE.LoadingManager();
const loader = new GLTFLoader(assetManager);
const cache = new Map();
const loadingScreen = document.getElementById('loadingScreen');
const loadingBar = document.getElementById('loadingBar');
const loadingPct = document.getElementById('loadingPct');
const loadingText = document.getElementById('loadingText');
assetManager.onProgress = (url, loaded, total) => {
  const p = total ? Math.round(loaded / total * 100) : 0;
  if (loadingBar) loadingBar.style.width = p + '%';
  if (loadingPct) loadingPct.textContent = p + '%';
  if (loadingText) loadingText.textContent = 'جاري تجهيز BUNKER 17...';
};
assetManager.onLoad = () => {
  if (loadingBar) loadingBar.style.width = '100%';
  if (loadingPct) loadingPct.textContent = '100%';
  if (loadingText) loadingText.textContent = 'BUNKER 17 جاهز';
  setTimeout(() => loadingScreen?.classList.add('done'), 260);
};
setTimeout(() => loadingScreen?.classList.add('done'), 12000);

async function loadModel(url) {
  if (!cache.has(url)) cache.set(url, loader.loadAsync(url).catch(e=>{ cache.delete(url); throw e; }));
  const gltf = await cache.get(url);
  return gltf.scene.clone(true);
}

async function place(url, position, scale = 1, rotationY = 0, parent = room) {
  try {
    const obj = await loadModel(url);
    obj.position.set(...position);
    obj.scale.setScalar(scale);
    obj.rotation.y = rotationY;
    obj.traverse(n => {
      if (n.isMesh) {
        n.castShadow = true;
        n.receiveShadow = true;
        n.frustumCulled = true;
      }
    });
    parent.add(obj);
    return obj;
  } catch (e) {
    console.warn('Model failed:', url, e);
    return null;
  }
}

async function fit(url, position, size, rotationY = 0, parent = room) {
  try {
    const obj = await loadModel(url);
    obj.rotation.y = rotationY;
    obj.updateMatrixWorld(true);
    const box = new THREE.Box3().setFromObject(obj);
    const s = box.getSize(new THREE.Vector3());
    const target = new THREE.Vector3(...size);
    const k = Math.min(target.x / Math.max(s.x, .001), target.y / Math.max(s.y, .001), target.z / Math.max(s.z, .001));
    obj.scale.setScalar(k);
    obj.updateMatrixWorld(true);
    const b2 = new THREE.Box3().setFromObject(obj);
    const c = b2.getCenter(new THREE.Vector3());
    obj.position.set(position[0] - c.x, position[1] - b2.min.y, position[2] - c.z);
    obj.traverse(n => {
      if (n.isMesh) {
        n.castShadow = true;
        n.receiveShadow = true;
      }
    });
    parent.add(obj);
    return obj;
  } catch (e) {
    console.warn('Fit failed:', url, e);
    return null;
  }
}

const Q = './assets/vendor/quaternius-scifi/Modular%20SciFi%20MegaKit%5BStandard%5D/glTF/';
const PH = './assets/vendor/polyhaven/';
const paths = {
  floor: Q + 'Platforms/Platform_DarkPlates.gltf',
  wall: Q + 'Walls/WallAstra_Straight.gltf',
  lowerWall: Q + 'Walls/BottomMetal_Straight.gltf',
  cable: Q + 'Props/Prop_Cable_3.gltf',
  access: Q + 'Props/Prop_AccessPoint.gltf',
  pipes: PH + 'modular_industrial_pipes_01/model.gltf',
  sconce: PH + 'industrial_caged_sconce/model.gltf',
  hanging: PH + 'hanging_industrial_lamp/model.gltf',
  desk: PH + 'metal_office_desk/model.gltf',
  shelves: PH + 'steel_frame_shelves_02/model.gltf',
  cabinet: PH + 'drawer_cabinet/model.gltf',
  books: PH + 'book_encyclopedia_set_01/model.gltf'
};

const emergency = new THREE.PointLight(0xff3a2e, 1.4, 10, 2);
emergency.position.set(0, 3.55, 0.5);
room.add(emergency);
const ambient = new THREE.HemisphereLight(0xd7e4ea, 0x2a2119, 1.35);
scene.add(ambient);
const fillLight = new THREE.DirectionalLight(0xcfe7f2, 1.5);
fillLight.position.set(2.5, 5.5, 4.5);
scene.add(fillLight);
const warmFill = new THREE.DirectionalLight(0xffc58c, 0.95);
warmFill.position.set(-4.5, 3.5, -1.5);
scene.add(warmFill);
const mainLights = [];
for (const p of [[-3.8,3.25,0],[0,3.25,0],[3.8,3.25,0]]) {
  const l = new THREE.PointLight(0xffd8ad, 3.2, 13, 1.55);
  l.position.set(...p); l.castShadow = true; l.shadow.mapSize.set(512,512); room.add(l); mainLights.push(l);
}
const consoleGlow = new THREE.PointLight(0x54d7bf, 0.25, 4, 2);
consoleGlow.position.set(0, 1.5, -4.3); room.add(consoleGlow);
const doorLight = new THREE.PointLight(0xff281f, 2.2, 3.6, 2);
doorLight.position.set(0,2.6,-5.1); room.add(doorLight);

async function buildRoom() {
  // Imported architectural meshes only; no visible Three.js primitive shell.
  for (let x=-4.5; x<=4.5; x+=1.8) for (let z=-4.2; z<=4.2; z+=1.8) await fit(paths.floor,[x,0,z],[1.72,.12,1.72]);
  for (let x=-4.5; x<=4.5; x+=1.8) {
    await fit(paths.wall,[x,.02,-5.0],[1.76,3.75,.34]);
    await fit(paths.lowerWall,[x,.02,-4.72],[1.76,.38,.28]);
    await fit(paths.wall,[x,.02,5.0],[1.76,3.75,.34],Math.PI);
  }
  for (let z=-3.9; z<=3.9; z+=1.8) {
    await fit(paths.wall,[-5.4,.02,z],[1.76,3.75,.34],Math.PI/2);
    await fit(paths.wall,[5.4,.02,z],[1.76,3.75,.34],-Math.PI/2);
  }
  for (let x=-3.6;x<=3.6;x+=3.6) await fit(paths.hanging,[x,3.15,0],[1.1,.7,1.1]);
  await fit(paths.sconce,[-4.92,2.0,-2.4],[.65,.85,.55],Math.PI/2);
  await fit(paths.sconce,[4.92,2.0,-2.4],[.65,.85,.55],-Math.PI/2);
  await fit(paths.pipes,[-4.55,.25,-.5],[1.15,3.1,3.5],Math.PI/2);
  await fit(paths.desk,[-1.1,.05,1.25],[2.5,1.3,1.5],Math.PI);
  await fit(paths.shelves,[4.15,.05,1.55],[1.7,3.1,1.05],-Math.PI/2);
  await fit(paths.cabinet,[3.8,.04,-3.15],[1.55,2.4,.9],-Math.PI/2);
  await fit(paths.books,[4.12,1.3,1.15],[1.1,.65,.75],-Math.PI/2);
  await fit(paths.access,[1.2,1.15,-4.72],[1.25,1.0,.42],0);
  await fit(paths.access,[-1.2,1.15,-4.72],[1.25,1.0,.42],0);
  await fit(paths.cable,[-2.1,.05,2.9],[2.4,.35,1.6],0);
  await fit(paths.cable,[2.3,.05,2.65],[2.2,.35,1.4],Math.PI/2);
}

const stageNames = ['الطاقة','الضغط','الأدلة','لوحة التحكم','باب الخروج'];
let stage = 0;
let completed = [false,false,false,false,false];
const stations = [
  { name:'لوحة الطاقة', pos:new THREE.Vector3(-3.9,1.5,-2.2), stage:0 },
  { name:'شبكة الضغط', pos:new THREE.Vector3(-4.25,1.55,.1), stage:1 },
  { name:'الأدلة', pos:new THREE.Vector3(3.9,1.35,1.5), stage:2 },
  { name:'لوحة التحكم', pos:new THREE.Vector3(0,1.45,-4.55), stage:3 },
  { name:'باب الملجأ', pos:new THREE.Vector3(0,1.55,-4.9), stage:4 }
];

const hint = document.getElementById('hint');
const roomSub = document.getElementById('roomSub');
if (roomSub) roomSub.textContent = 'BUNKER 17 — CONTROL ROOM';
const prev = document.getElementById('prev'), next = document.getElementById('next');
if (prev) prev.style.display='none'; if (next) next.style.display='none';
const useBtn = document.getElementById('use');
const modal = document.getElementById('modal');
const pTitle = document.getElementById('pTitle');
const pDesc = document.getElementById('pDesc');
const game = document.getElementById('game');
const status = document.getElementById('status');
document.getElementById('close')?.addEventListener('click',()=>modal?.classList.remove('show'));

function setStage(n){ stage=n; if(hint) hint.textContent=`النظام ${n+1}/5 — ${stageNames[n]}`; }
function solve(n){ completed[n]=true; if(n===0){ emergency.intensity=.45; ambient.intensity=1.05; mainLights.forEach(l=>l.intensity=5.2); }
  if(n===1){ consoleGlow.intensity=.8; }
  if(n===3){ doorLight.color.set(0xffb12f); doorLight.intensity=3; }
  if(n===4){ doorLight.color.set(0x55ff9a); doorLight.intensity=4.5; }
  if(n<4) setStage(n+1); else if(hint) hint.textContent='تم فتح BUNKER 17 — الحرية أمامك';
}

function nearestStation(){
  let best=null,dist=999;
  for(const s of stations){ const d=player.position.distanceTo(s.pos); if(d<dist){dist=d;best=s;} }
  return dist<2.6 ? best : null;
}

function openPuzzle(s){
  if(s.stage>stage){ pTitle.textContent=s.name; pDesc.textContent='هذا النظام ما زال مقفلاً. أكمل النظام السابق أولاً.'; game.innerHTML=''; status.textContent=''; modal.classList.add('show'); return; }
  pTitle.textContent=s.name; status.textContent=''; modal.classList.add('show');
  if(s.stage===0) powerPuzzle();
  if(s.stage===1) pressurePuzzle();
  if(s.stage===2) cluePuzzle();
  if(s.stage===3) consolePuzzle();
  if(s.stage===4) doorPuzzle();
}

function finishPuzzle(n, message){
  status.textContent=message;
  if(!completed[n]) solve(n);
}

function powerPuzzle(){
  pDesc.textContent='أعد الطاقة عبر شبكة التوزيع. كل زر يدير قطعة سلك 90°. يجب إنشاء مسار متصل من المولد إلى وحدة التحكم.';
  const target=[1,2,0,3,1,0,2,1,3], rot=[0,0,0,0,0,0,0,0,0];
  game.innerHTML='<div class="b17-grid power-grid"></div><div class="b17-meter">GENERATOR ▸ ▢ ▢ ▢ ▸ CONTROL</div>';
  const wrap=game.firstChild;
  rot.forEach((_,i)=>{const b=document.createElement('button');b.className='b17-tile';b.innerHTML='<span>└</span>';b.onclick=()=>{rot[i]=(rot[i]+1)%4;b.querySelector('span').style.transform=`rotate(${rot[i]*90}deg)`;const ok=rot.every((v,j)=>v===target[j]);status.textContent=`استقرار الشبكة ${rot.filter((v,j)=>v===target[j]).length}/9`;if(ok){wrap.classList.add('powered');finishPuzzle(0,'POWER BUS ONLINE — عادت الإضاءة الرئيسية');}};wrap.appendChild(b);});
}

function pressurePuzzle(){
  pDesc.textContent='وازن ضغط خطوط التبريد. تدوير أي صمام يؤثر في أكثر من خط؛ اجعل العدادات الثلاثة داخل المجال الأخضر 45–55 PSI.';
  let v=[0,0,0]; const pressure=()=>[28+v[0]*9+v[2]*4,31+v[1]*8-v[0]*3,26+v[2]*10+v[1]*3];
  game.innerHTML='<div class="b17-gauges"></div><div class="b17-valves"></div>';const gauges=game.firstChild,wrap=game.lastChild;
  const render=()=>{const ps=pressure();gauges.innerHTML=ps.map((x,i)=>`<div class="b17-gauge ${x>=45&&x<=55?'ok':''}"><b>${Math.round(x)}</b><small>PSI ${i+1}</small></div>`).join('');status.textContent=`PRESSURE ${ps.map(x=>Math.round(x)).join(' / ')} PSI`;if(ps.every(x=>x>=45&&x<=55))finishPuzzle(1,'PRESSURE STABLE — خطوط التبريد مستقرة');};
  for(let i=0;i<3;i++){const b=document.createElement('button');b.className='b17-valve';b.innerHTML=`<span class="wheel">✣</span><b>V${i+1}</b>`;b.onclick=()=>{v[i]=(v[i]+1)%4;b.querySelector('.wheel').style.transform=`rotate(${v[i]*90}deg)`;render();};wrap.appendChild(b);}render();
}

function cluePuzzle(){
  pDesc.textContent='استخرج الأدلة بالترتيب المنطقي من سجل الملجأ. الرموز وحدها لا تكفي؛ الرقم الموجود مع كل دليل هو ترتيب الإدخال.';
  const clues=[['كتاب العمليات','△','2'],['خزانة الطوارئ','○','4'],['مذكرة المكتب','III','1'],['لوحة التحذير','✕','3']];let found=new Map();
  game.innerHTML='<div class="b17-clues"></div><div class="b17-evidence">الأدلة المكتشفة: —</div>';const wrap=game.firstChild,out=game.lastChild;
  clues.forEach(([name,sym,n])=>{const b=document.createElement('button');b.className='b17-clue';b.textContent=name;b.onclick=()=>{found.set(n,sym);b.classList.add('found');b.textContent=`${name}  [${n}] ${sym}`;out.textContent='الأدلة: '+[...found.entries()].sort().map(([k,x])=>`${k}:${x}`).join('   ');if(found.size===4)finishPuzzle(2,'تم جمع الأدلة — رتّب الرموز حسب الأرقام 1 ← 4');};wrap.appendChild(b);});
}

function consolePuzzle(){
  pDesc.textContent='أدخل الرموز حسب أرقام الأدلة، وليس حسب مكان العثور عليها.';
  const answer=['III','△','✕','○'], symbols=['△','○','III','✕'];let entry=[];
  game.innerHTML='<div class="b17-symbols"></div><div class="b17-entry">— — — —</div>';const wrap=game.firstChild,out=game.lastChild;
  symbols.forEach(sym=>{const b=document.createElement('button');b.textContent=sym;b.onclick=()=>{if(entry.length<4)entry.push(sym);out.textContent=entry.join('  ');if(entry.length===4){if(entry.every((x,i)=>x===answer[i]))finishPuzzle(3,'SECURITY CORE ACCEPTED — DOOR CODE 7314');else{status.textContent='ACCESS DENIED — أعد قراءة أرقام الأدلة';entry=[];setTimeout(()=>out.textContent='— — — —',450);}}};wrap.appendChild(b);});
}

function doorPuzzle(){
  pDesc.textContent='أدخل رمز الأمان الذي ظهر على وحدة التحكم، ثم فعّل قفل الباب الميكانيكي.';
  let code='';game.innerHTML='<div class="b17-keypad"></div><div class="b17-code">____</div>';const pad=game.firstChild,out=game.lastChild;
  [...'1234567890'].forEach(n=>{const b=document.createElement('button');b.textContent=n;b.onclick=()=>{if(code.length<4)code+=n;out.textContent=code.padEnd(4,'_');if(code.length===4){if(code==='7314'){status.textContent='CODE ACCEPTED — القفل الميكانيكي جاهز';pad.querySelectorAll('button').forEach(x=>x.disabled=true);const open=document.createElement('button');open.className='b17-open';open.textContent='تدوير مقبض الباب';let turns=0;open.onclick=()=>{turns++;open.style.transform=`rotate(${turns*45}deg)`;status.textContent=`تحرير الأقفال ${turns}/4`;if(turns>=4){finishPuzzle(4,'BUNKER 17 OPEN — تم تحرير الباب');modal.classList.remove('show');}};game.appendChild(open);}else{status.textContent='رمز غير صحيح';code='';setTimeout(()=>out.textContent='____',350);}}};pad.appendChild(b);});
}

useBtn?.addEventListener('click',()=>{ const s=nearestStation(); if(s)openPuzzle(s); else if(hint)hint.textContent='اقترب من إحدى محطات النظام'; });

const keys={}; addEventListener('keydown',e=>keys[e.code]=true); addEventListener('keyup',e=>keys[e.code]=false);
let yaw=0, pitch=-.05, dragging=false, lx=0,ly=0;
renderer.domElement.addEventListener('pointerdown',e=>{dragging=true;lx=e.clientX;ly=e.clientY;});
addEventListener('pointerup',()=>dragging=false);
addEventListener('pointermove',e=>{if(!dragging||renderer.xr.isPresenting)return;const dx=e.clientX-lx,dy=e.clientY-ly;lx=e.clientX;ly=e.clientY;yaw-=dx*.004;pitch=Math.max(-1.05,Math.min(.85,pitch-dy*.003));});

const joy=document.getElementById('joy'),knob=document.getElementById('knob');let joyId=null,jx=0,jy=0;
joy?.addEventListener('pointerdown',e=>{joyId=e.pointerId;joy.setPointerCapture(e.pointerId);});
joy?.addEventListener('pointermove',e=>{if(e.pointerId!==joyId)return;const r=joy.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;let dx=e.clientX-cx,dy=e.clientY-cy;const m=Math.hypot(dx,dy),max=r.width*.32;if(m>max){dx*=max/m;dy*=max/m;}jx=dx/max;jy=dy/max;if(knob)knob.style.transform=`translate(${dx}px,${dy}px)`;});
const joyEnd=e=>{if(e.pointerId!==joyId)return;joyId=null;jx=jy=0;if(knob)knob.style.transform='translate(0,0)';}; joy?.addEventListener('pointerup',joyEnd); joy?.addEventListener('pointercancel',joyEnd);

const vrBtn=VRButton.createButton(renderer,{optionalFeatures:['local-floor','bounded-floor','hand-tracking','dom-overlay'],domOverlay:{root:document.body}});
Object.assign(vrBtn.style,{position:'fixed',left:'12px',bottom:'12px',zIndex:'50'});document.body.appendChild(vrBtn);
const arBtn=document.createElement('button');arBtn.textContent='ENTER AR';arBtn.className='b17-ar';document.body.appendChild(arBtn);
const controllers=[renderer.xr.getController(0),renderer.xr.getController(1)];controllers.forEach(c=>scene.add(c));
const arManager=new ARManager({renderer,scene,controllers}); let xrMode='flat';
arManager.onPlaced=({position,quaternion})=>{room.position.copy(position);room.quaternion.copy(quaternion);room.scale.setScalar(.22);room.visible=true;};
arBtn.onclick=async()=>{try{await arManager.requestSession();}catch(e){console.error(e)}};
renderer.xr.addEventListener('sessionstart',()=>{const s=renderer.xr.getSession();xrMode=s?.environmentBlendMode==='opaque'?'vr':'ar';if(xrMode==='ar'){scene.background=null;scene.fog=null;room.visible=false;}else{room.visible=true;room.position.set(0,0,0);room.quaternion.identity();room.scale.setScalar(1);player.position.set(0,1.66,3.9);}});
renderer.xr.addEventListener('sessionend',()=>{xrMode='flat';scene.background=new THREE.Color(0x080a0b);scene.fog=new THREE.FogExp2(0x101214,.012);room.visible=true;room.position.set(0,0,0);room.quaternion.identity();room.scale.setScalar(1);});

controllers.forEach(c=>c.addEventListener('selectstart',()=>{if(xrMode==='vr'){const p=new THREE.Vector3();c.getWorldPosition(p);let best=null,d=999;for(const s of stations){const dd=p.distanceTo(s.pos);if(dd<d){d=dd;best=s;}}if(best&&d<3.0)openPuzzle(best);}}));

const clock=new THREE.Clock();
function tick(){
  const dt=Math.min(clock.getDelta(),.04);
  if(xrMode==='flat'){
    player.rotation.y=yaw;camera.rotation.x=pitch;
    const f=(keys.KeyW?1:0)-(keys.KeyS?1:0)-jy;
    const r=(keys.KeyD?1:0)-(keys.KeyA?1:0)+jx;
    const v=new THREE.Vector3(r,0,-f); if(v.lengthSq()>1)v.normalize(); v.applyAxisAngle(new THREE.Vector3(0,1,0),yaw).multiplyScalar(2.5*dt);
    player.position.add(v); player.position.x=THREE.MathUtils.clamp(player.position.x,-4.65,4.65);player.position.z=THREE.MathUtils.clamp(player.position.z,-4.35,4.35);
    const s=nearestStation(); if(s&&hint)hint.textContent=`${s.name} — اضغط تفاعل`; else if(hint)hint.textContent=`النظام ${stage+1}/5 — ${stageNames[stage]}`;
  }
  renderer.render(scene,camera);
}
renderer.setAnimationLoop(tick);

addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
setStage(0);
buildRoom();
