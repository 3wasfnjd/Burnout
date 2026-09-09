from pathlib import Path
import re

p=Path('src/main.js')
s=p.read_text()

old="import{VRButton}from'three/addons/webxr/VRButton.js';import{ARButton}from'three/addons/webxr/ARButton.js';"
new="import{VRButton}from'three/addons/webxr/VRButton.js';import{ARManager}from'./ARManager.js';"
if old not in s: raise SystemExit('XR imports not found')
s=s.replace(old,new,1)

pat=re.compile(r"const desktopBg=scene\.background,desktopFog=scene\.fog;.*?scene\.add\(new THREE\.HemisphereLight",re.S)
repl="""const desktopBg=scene.background,desktopFog=scene.fog;let xrKind='flat';const xrRig=new THREE.Group(),xrCamera=new THREE.PerspectiveCamera(70,innerWidth/innerHeight,.05,90);xrRig.add(xrCamera);xrRig.position.set(0,0,2.35);scene.add(xrRig);const xrWrap=document.createElement('div');xrWrap.id='xrWrap';Object.assign(xrWrap.style,{position:'fixed',left:'50%',bottom:'14px',transform:'translateX(-50%)',display:'flex',gap:'10px',zIndex:'40'});document.body.appendChild(xrWrap);const vrBtn=VRButton.createButton(renderer,{optionalFeatures:['local-floor','bounded-floor','hand-tracking','dom-overlay'],domOverlay:{root:document.body}});vrBtn.style.position='static';vrBtn.style.margin='0';vrBtn.style.width='132px';vrBtn.style.height='42px';vrBtn.style.borderRadius='10px';xrWrap.appendChild(vrBtn);const arBtn=document.createElement('button');arBtn.textContent='ENTER AR';Object.assign(arBtn.style,{position:'static',margin:'0',width:'132px',height:'42px',borderRadius:'10px',border:'1px solid #ffffff88',background:'#101315cc',color:'#fff',fontWeight:'800'});xrWrap.appendChild(arBtn);
const rayGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,-4)]),rayMat=new THREE.LineBasicMaterial({color:0x8fe8ff}),xrControllers=[];for(let i=0;i<2;i++){const c=renderer.xr.getController(i);xrControllers.push(c);const line=new THREE.Line(rayGeo,rayMat);c.add(line);c.addEventListener('selectstart',()=>xrSelect(c));c.addEventListener('squeezestart',()=>{if(xrKind==='vr'&&vrPuzzle)closeVrPuzzle()});xrRig.add(c)}
let arScale=.32,arPlaced=false,arYaw=0;const arManager=new ARManager({renderer,scene,controllers:xrControllers});arManager.onPlaced=({position,quaternion,angle})=>{if(!root)return;arYaw=angle;arPlaced=true;root.position.copy(position);root.quaternion.copy(quaternion);root.scale.setScalar(arScale);root.visible=true;resetArPlayer();player.visible=true};arBtn.onclick=async()=>{try{startBgm();arBtn.disabled=true;await arManager.requestSession()}catch(e){console.error('AR session failed',e);arBtn.disabled=false}};ARManager.isSupported().then(ok=>{if(!ok){arBtn.disabled=true;arBtn.textContent='AR غير مدعوم'}});
renderer.xr.addEventListener('sessionstart',()=>{startBgm();const ses=renderer.xr.getSession();xrKind=ses&&ses.environmentBlendMode==='opaque'?'vr':'ar';document.body.classList.add('xr-active');try{puzzles.close?.()}catch(e){};const ub=document.getElementById('use');if(ub)ub.style.display=xrKind==='ar'?'':'none';if(xrKind==='ar'){scene.background=null;scene.fog=null;arPlaced=false;player.visible=false;if(root){root.visible=false;root.scale.setScalar(arScale)}}else{player.visible=false;if(root){root.visible=true;root.scale.setScalar(1);root.position.set(0,0,0);root.quaternion.identity()}xrRig.position.set(0,0,2.35);xrRig.rotation.set(0,0,0)}});renderer.xr.addEventListener('sessionend',()=>{xrKind='flat';arPlaced=false;document.body.classList.remove('xr-active');const ub=document.getElementById('use');if(ub)ub.style.display='';scene.background=desktopBg;scene.fog=desktopFog;player.visible=true;player.scale.setScalar(1);player.rotation.y=0;closeVrPuzzle();arBtn.disabled=false;if(root){root.visible=true;root.scale.setScalar(1);root.position.set(0,0,0);root.quaternion.identity()}});scene.add(new THREE.HemisphereLight"""
s,n=pat.subn(repl,s,count=1)
if n!=1: raise SystemExit('old XR/AR block not found')

old="let xrSelectBusy=false;function xrSelect(controller){if(xrSelectBusy)return;xrSelectBusy=true;setTimeout(()=>xrSelectBusy=false,140);if(xrKind==='ar'){if(!arPlaced)confirmArPlacement();return}if(xrKind!=='vr')return;"
new="let xrSelectBusy=false;function xrSelect(controller){if(xrSelectBusy)return;xrSelectBusy=true;setTimeout(()=>xrSelectBusy=false,140);if(xrKind==='ar')return;if(xrKind!=='vr')return;"
if old not in s: raise SystemExit('xrSelect AR branch not found')
s=s.replace(old,new,1)

# Replace the AR movement branch so post-placement input comes from ARManager.
pat=re.compile(r"if\(xrKind==='ar'\)\{if\(!arPlaced\)return;const \[ax0,ay0\]=stickAxes\(left\?\.gamepad\|\|right\?\.gamepad\);.*?moveArPlayer\(dx,dz,dt\);return\}",re.S)
repl="""if(xrKind==='ar'){if(!arPlaced||!arManager.isPlaced())return;const input=arManager.getMoveInput();let ax=THREE.MathUtils.clamp(input.x+jx,-1,1),ay=THREE.MathUtils.clamp(input.z+jy,-1,1);if(Math.abs(ax)<.08&&Math.abs(ay)<.08)return;xrCamera.getWorldDirection(arLocalForward);arLocalForward.y=0;if(arLocalForward.lengthSq()<.0001)return;arLocalForward.normalize().applyAxisAngle(arPlayerAxis,-arYaw);arLocalRight.set(arLocalForward.z,0,-arLocalForward.x);const speed=2.35,dx=(arLocalRight.x*ax+arLocalForward.x*-ay)*speed*dt,dz=(arLocalRight.z*ax+arLocalForward.z*-ay)*speed*dt;moveArPlayer(dx,dz,dt);return}"""
s,n=pat.subn(repl,s,count=1)
if n!=1: raise SystemExit('AR movement branch not found')

# Remove the legacy hit-test function; ARManager owns it now.
s,n=re.subn(r"\nfunction updateArHit\(frame\)\{.*?\}\nfunction animate", "\nfunction animate", s, count=1, flags=re.S)
if n!=1: raise SystemExit('legacy updateArHit not found')

old="if(renderer.xr.isPresenting){updateArHit(frame);if(!modal.classList.contains('show'))xrMove(dt);"
new="if(renderer.xr.isPresenting){if(xrKind==='ar')arManager.update(frame,dt);if(!modal.classList.contains('show'))xrMove(dt);"
if old not in s: raise SystemExit('animate XR block not found')
s=s.replace(old,new,1)

p.write_text(s)
