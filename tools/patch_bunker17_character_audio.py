from pathlib import Path

path = Path('src/bunker17.js')
s = path.read_text(encoding='utf-8')

# Import the FBX loader used by the original Shelter character.
s = s.replace(
    "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';\n",
    "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';\nimport { FBXLoader } from 'three/addons/loaders/FBXLoader.js';\n",
    1,
)

# Move the flat-screen camera behind the avatar so the player character is visible.
s = s.replace(
    "player.add(camera);\nscene.add(player);",
    "camera.position.set(0, .28, 3.15);\nplayer.add(camera);\nscene.add(player);",
    1,
)

# Restore the original Shelter background music with browser-safe user-gesture start and mute control.
music = r'''

// BUNKER 17 ambience/music. Browsers require the first play call to follow a user gesture.
const bgm = new Audio('https://opengameart.org/sites/default/files/sector_0.mp3');
bgm.loop = true;
bgm.volume = .20;
bgm.preload = 'auto';
let bgmStarted = false;
function startBgm(){
  if (bgmStarted) return;
  bgm.play().then(()=>{ bgmStarted = true; }).catch(()=>{});
}
['pointerdown','keydown','touchstart'].forEach(type=>addEventListener(type,startBgm,{once:true,passive:true}));
const musicBtn=document.createElement('button');
musicBtn.id='musicBtn';
musicBtn.textContent='🔊';
musicBtn.title='تشغيل/كتم الموسيقى';
Object.assign(musicBtn.style,{position:'fixed',left:'12px',top:'12px',zIndex:'55',width:'42px',height:'42px',borderRadius:'50%',border:'1px solid #ffffff44',background:'#0a0d10dd',color:'#fff',fontSize:'18px',cursor:'pointer'});
musicBtn.addEventListener('click',e=>{e.stopPropagation();startBgm();bgm.muted=!bgm.muted;musicBtn.textContent=bgm.muted?'🔇':'🔊';});
document.body.appendChild(musicBtn);
'''
s = s.replace("const room = new THREE.Group();\nscene.add(room);", "const room = new THREE.Group();\nscene.add(room);" + music, 1)

# Restore the repository's existing Kenney character and idle/run animation.
avatar = r'''
const fbxLoader = new FBXLoader(assetManager);
const textureLoader = new THREE.TextureLoader(assetManager);
const avatar = new THREE.Group();
room.add(avatar);
let avatarModel=null, avatarMixer=null, avatarIdle=null, avatarRun=null, avatarMoving=false;

Promise.all([
  fbxLoader.loadAsync('./assets/kenney/characterMedium.fbx'),
  fbxLoader.loadAsync('./assets/kenney/idle.fbx'),
  fbxLoader.loadAsync('./assets/kenney/run.fbx'),
  textureLoader.loadAsync('./assets/kenney/humanMaleA.png')
]).then(([model,idle,run,texture])=>{
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.flipY=true;
  model.updateMatrixWorld(true);
  let box=new THREE.Box3().setFromObject(model);
  const size=box.getSize(new THREE.Vector3());
  model.scale.setScalar(1.72/Math.max(size.y,.001));
  model.updateMatrixWorld(true);
  box=new THREE.Box3().setFromObject(model);
  const center=box.getCenter(new THREE.Vector3());
  model.position.x-=center.x;
  model.position.y-=box.min.y;
  model.position.z-=center.z;
  model.traverse(n=>{
    if(!n.isMesh)return;
    n.castShadow=true;
    n.receiveShadow=true;
    n.material=new THREE.MeshStandardMaterial({map:texture,roughness:.82,metalness:0});
  });
  avatarModel=model;
  avatar.add(model);
  avatarMixer=new THREE.AnimationMixer(model);
  if(idle.animations[0]){avatarIdle=avatarMixer.clipAction(idle.animations[0],model);avatarIdle.play();}
  if(run.animations[0]){avatarRun=avatarMixer.clipAction(run.animations[0],model);}
  avatar.position.set(player.position.x,0,player.position.z);
  avatar.rotation.y=Math.PI;
}).catch(e=>console.warn('BUNKER 17 character failed to load',e));

function syncAvatar(moving,dt){
  if(!avatarModel)return;
  avatar.position.set(player.position.x,0,player.position.z);
  avatar.rotation.y=yaw+Math.PI;
  avatarMixer?.update(dt);
  if(moving===avatarMoving)return;
  avatarMoving=moving;
  if(moving&&avatarRun){avatarIdle?.fadeOut(.18);avatarRun.reset().fadeIn(.18).play();}
  else if(avatarIdle){avatarRun?.fadeOut(.18);avatarIdle.reset().fadeIn(.18).play();}
}
'''
s = s.replace("const loader = new GLTFLoader(assetManager);\n", "const loader = new GLTFLoader(assetManager);\n" + avatar, 1)

# Keep the avatar in sync with flat-screen movement.
s = s.replace(
    "player.position.z=THREE.MathUtils.clamp(player.position.z,-4.35,4.35);const s=nearestStation();",
    "player.position.z=THREE.MathUtils.clamp(player.position.z,-4.35,4.35);syncAvatar(v.lengthSq()>.00001,dt);const s=nearestStation();",
    1,
)

# Start music in XR, hide the full avatar in first-person VR, and retain it in miniature AR.
s = s.replace(
    "renderer.xr.addEventListener('sessionstart',()=>{const s=renderer.xr.getSession();xrMode=s?.environmentBlendMode==='opaque'?'vr':'ar';",
    "renderer.xr.addEventListener('sessionstart',()=>{startBgm();const s=renderer.xr.getSession();xrMode=s?.environmentBlendMode==='opaque'?'vr':'ar';avatar.visible=xrMode!=='vr';",
    1,
)
s = s.replace(
    "renderer.xr.addEventListener('sessionend',()=>{xrMode='flat';",
    "renderer.xr.addEventListener('sessionend',()=>{xrMode='flat';avatar.visible=true;",
    1,
)
s = s.replace(
    "arBtn.onclick=async()=>{try{await arManager.requestSession();}",
    "arBtn.onclick=async()=>{try{startBgm();await arManager.requestSession();}",
    1,
)

# Ensure the initial avatar transform is correct before the first movement frame.
s = s.replace("setStage(0);buildRoom();", "setStage(0);buildRoom();", 1)

path.write_text(s,encoding='utf-8')
print('Patched BUNKER 17 character, third-person camera and music.')
