from pathlib import Path

path = Path('src/bunker17.js')
s = path.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Expected block not found: {label}')
    s = s.replace(old, new, 1)

rep(
    "camera.position.set(0, .28, 3.15);",
    "camera.position.set(0, .48, 2.2);",
    "third-person camera",
)

rep(
'''function syncAvatar(moving,dt){
  if(!avatarModel)return;
  avatar.position.set(player.position.x,0,player.position.z);
  avatar.rotation.y=yaw+Math.PI;
  avatarMixer?.update(dt);
  if(moving===avatarMoving)return;
  avatarMoving=moving;
  if(moving&&avatarRun){avatarIdle?.fadeOut(.18);avatarRun.reset().fadeIn(.18).play();}
  else if(avatarIdle){avatarRun?.fadeOut(.18);avatarIdle.reset().fadeIn(.18).play();}
}''',
'''function setAvatarMotion(moving){
  if(!avatarModel||moving===avatarMoving)return;
  avatarMoving=moving;
  if(moving&&avatarRun){avatarIdle?.fadeOut(.18);avatarRun.reset().fadeIn(.18).play();}
  else if(avatarIdle){avatarRun?.fadeOut(.18);avatarIdle.reset().fadeIn(.18).play();}
}
function syncFlatAvatar(moving,dt){
  if(!avatarModel)return;
  avatar.position.set(player.position.x,0,player.position.z);
  avatar.rotation.y=yaw+Math.PI;
  avatarMixer?.update(dt);
  setAvatarMotion(moving);
}''',
    "avatar motion helpers",
)

rep(
'''arManager.onPlaced=({position,quaternion})=>{room.position.copy(position);room.quaternion.copy(quaternion);room.scale.setScalar(.22);room.visible=true;};''',
'''const arAvatarPos=new THREE.Vector3(0,0,3.0),arRoomQuat=new THREE.Quaternion(),arInvRoomQuat=new THREE.Quaternion(),arLocalMove=new THREE.Vector3();
function resetArAvatar(){arAvatarPos.set(0,0,3.0);avatar.position.copy(arAvatarPos);avatar.rotation.y=Math.PI;setAvatarMotion(false);}
arManager.onPlaced=({position,quaternion})=>{room.position.copy(position);room.quaternion.copy(quaternion);room.scale.setScalar(.22);room.visible=true;resetArAvatar();avatar.visible=true;};''',
    "AR placement/avatar",
)

rep(
'''renderer.xr.addEventListener('sessionstart',()=>{startBgm();const s=renderer.xr.getSession();xrMode=s?.environmentBlendMode==='opaque'?'vr':'ar';avatar.visible=xrMode!=='vr';if(xrMode==='ar'){scene.background=null;scene.fog=null;room.visible=false;}else{room.visible=true;room.position.set(0,0,0);room.quaternion.identity();room.scale.setScalar(1);player.position.set(0,1.66,3.9);}});''',
'''renderer.xr.addEventListener('sessionstart',()=>{startBgm();const s=renderer.xr.getSession();xrMode=s?.environmentBlendMode==='opaque'?'vr':'ar';if(xrMode==='ar'){avatar.visible=false;scene.background=null;scene.fog=null;room.visible=false;}else{avatar.visible=false;room.visible=true;room.position.set(0,0,0);room.quaternion.identity();room.scale.setScalar(1);player.position.set(0,1.66,3.9);}});''',
    "XR session start",
)

rep(
'''function adjustAR(dt){
  if(!arManager.isPlaced())return;
  const {x,z}=arManager.getMoveInput();const rot=arManager.getRotateInput();
  const xrCam=renderer.xr.getCamera(camera);xrCam.getWorldDirection(xrForward);xrForward.y=0;if(xrForward.lengthSq()>.001)xrForward.normalize();else xrForward.set(0,0,-1);
  xrRight.crossVectors(xrForward,xrUp).normalize();
  room.position.addScaledVector(xrRight,x*.55*dt).addScaledVector(xrForward,-z*.55*dt);
  if(rot!==0)room.rotateY(-rot*1.25*dt);
}''',
'''function adjustAR(dt){
  if(!arManager.isPlaced())return;
  const {x,z}=arManager.getMoveInput();const rot=arManager.getRotateInput();
  const xrCam=renderer.xr.getCamera(camera);xrCam.getWorldDirection(xrForward);xrForward.y=0;if(xrForward.lengthSq()<.001)xrForward.set(0,0,-1);else xrForward.normalize();
  room.getWorldQuaternion(arRoomQuat);arInvRoomQuat.copy(arRoomQuat).invert();xrForward.applyQuaternion(arInvRoomQuat);xrForward.y=0;if(xrForward.lengthSq()<.001)xrForward.set(0,0,-1);else xrForward.normalize();
  xrRight.set(xrForward.z,0,-xrForward.x);arLocalMove.set(0,0,0).addScaledVector(xrRight,x).addScaledVector(xrForward,-z);if(arLocalMove.lengthSq()>1)arLocalMove.normalize();
  const moving=arLocalMove.lengthSq()>.0001;
  if(moving){arAvatarPos.addScaledVector(arLocalMove,2.2*dt);arAvatarPos.x=THREE.MathUtils.clamp(arAvatarPos.x,-4.65,4.65);arAvatarPos.z=THREE.MathUtils.clamp(arAvatarPos.z,-4.35,4.35);avatar.position.copy(arAvatarPos);avatar.rotation.y=Math.atan2(arLocalMove.x,arLocalMove.z);}else if(Math.abs(rot)>.15){avatar.rotation.y-=rot*1.7*dt;}
  avatarMixer?.update(dt);setAvatarMotion(moving);
}''',
    "AR character movement",
)

rep(
    "syncAvatar(v.lengthSq()>.00001,dt);",
    "syncFlatAvatar(v.lengthSq()>.00001,dt);",
    "flat avatar sync",
)

path.write_text(s, encoding='utf-8')
print('Fixed BUNKER 17 third-person camera and AR character movement.')
