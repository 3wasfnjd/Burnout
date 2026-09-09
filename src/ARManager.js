import * as THREE from 'three';

// AR placement + controller input for BUNKER 17.
const DEADZONE = 0.15;
const MOVE_SPEED = 1.5;
const ROTATE_SPEED = 1.2;

export class ARManager {
  constructor({ renderer, scene, controllers = [] }) {
    this.renderer = renderer;
    this.scene = scene;
    this.session = null;
    this.hitTestSource = null;
    this.hitTestSourceRequested = false;
    this.hasHit = false;
    this.placed = false;
    this.arPosition = new THREE.Vector3();
    this.arQuaternion = new THREE.Quaternion();
    this.previewGroup = this.buildPreviewMesh();
    this.previewGroup.visible = false;
    this.scene.add(this.previewGroup);
    this.gamepads = { left: null, right: null };
    this.controllers = { left: null, right: null };
    this._prevTrigger = { left: false, right: false };
    this._savedBackground = null;
    this._savedFog = null;
    this.onPlaced = null;
    this._camForward = new THREE.Vector3();
    this._bindControllers(controllers);
  }

  static async isSupported() {
    if (!navigator.xr) return false;
    try { return await navigator.xr.isSessionSupported('immersive-ar'); }
    catch (_) { return false; }
  }

  async requestSession(pendingSession = null) {
    this.resetPlacement();
    const session = pendingSession ? await pendingSession : await navigator.xr.requestSession('immersive-ar', {
      requiredFeatures: ['local-floor', 'hit-test'],
      optionalFeatures: ['dom-overlay', 'plane-detection', 'mesh-detection'],
      domOverlay: { root: document.body }
    });
    this.renderer.xr.setReferenceSpaceType('local-floor');
    await this.renderer.xr.setSession(session);
    this.session = session;
    session.addEventListener('end', () => this._onSessionEnd());
    this._savedBackground = this.scene.background;
    this._savedFog = this.scene.fog;
    this.scene.background = null;
    this.scene.fog = null;
    this.previewGroup.visible = true;
    return session;
  }

  _bindControllers(controllers) {
    controllers.forEach((controller) => {
      controller.addEventListener('connected', (event) => {
        const hand = event.data.handedness === 'left' ? 'left' : 'right';
        this.gamepads[hand] = event.data.gamepad || null;
        this.controllers[hand] = controller;
      });
      controller.addEventListener('disconnected', (event) => {
        const hand = event.data.handedness === 'left' ? 'left' : 'right';
        this.gamepads[hand] = null;
        this.controllers[hand] = null;
      });
    });
  }

  buildPreviewMesh() {
    const group = new THREE.Group();
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(0.45, 0.55, 32),
      new THREE.MeshBasicMaterial({ color: 0x15a249, transparent: true, opacity: 0.88, side: THREE.DoubleSide })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.02;
    group.add(ring);
    const fill = new THREE.Mesh(
      new THREE.CircleGeometry(0.45, 32),
      new THREE.MeshBasicMaterial({ color: 0x15a249, transparent: true, opacity: 0.24, side: THREE.DoubleSide })
    );
    fill.rotation.x = -Math.PI / 2;
    fill.position.y = 0.015;
    group.add(fill);
    const arrow = new THREE.Mesh(
      new THREE.ConeGeometry(0.14, 0.5, 12),
      new THREE.MeshBasicMaterial({ color: 0x159897 })
    );
    arrow.rotation.x = Math.PI / 2;
    arrow.position.set(0, 0.05, -0.55);
    group.add(arrow);
    return group;
  }

  update(frame, dt = 1 / 60) {
    if (!this.session || !frame || this.placed) return;
    try {
      const refSpace = this.renderer.xr.getReferenceSpace();
      this._ensureHitTestSource();
      this._updatePlacement(frame, refSpace, Number.isFinite(dt) ? dt : 1 / 60);
    } catch (e) {
      console.error('[ARManager] update() error:', e);
    }
  }

  _ensureHitTestSource() {
    if (this.hitTestSourceRequested || !this.session) return;
    this.hitTestSourceRequested = true;
    this.session.requestReferenceSpace('viewer').then((viewerSpace) => {
      this.session.requestHitTestSource({ space: viewerSpace }).then((source) => {
        this.hitTestSource = source;
      }).catch((e) => console.warn('[ARManager] requestHitTestSource failed:', e));
    }).catch((e) => console.warn('[ARManager] viewer reference space failed:', e));
  }

  _updatePlacement(frame, refSpace, dt) {
    this._updateHitTestPose(frame, refSpace, dt);
    this.previewGroup.position.copy(this.arPosition);
    this.previewGroup.quaternion.copy(this.arQuaternion);
    this.previewGroup.visible = this.hasHit;
    if (this.hasHit && this._triggerPressedEdge()) this.confirmPlacement();
  }

  _updateHitTestPose(frame, refSpace, dt) {
    if (this.hitTestSource) {
      const results = frame.getHitTestResults(this.hitTestSource);
      if (results.length > 0) {
        const pose = results[0].getPose(refSpace);
        if (pose) {
          if (!this.hasHit) {
            const xrCam = this.renderer.xr.getCamera();
            this._camForward.set(0, 0, -1).transformDirection(xrCam.matrixWorld);
            const yaw = Math.atan2(this._camForward.x, this._camForward.z);
            this.arQuaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
          }
          this.arPosition.set(pose.transform.position.x, pose.transform.position.y, pose.transform.position.z);
          this.hasHit = true;
        }
      }
    }
    if (this.hasHit) this._applyThumbstickAdjustment(Math.min(dt, 1 / 30));
  }

  _applyThumbstickAdjustment(dt) {
    const axesR = this.gamepads.right ? this.gamepads.right.axes : [];
    const axesL = this.gamepads.left ? this.gamepads.left.axes : [];
    const moveX = this._axis(axesR, 2);
    const moveY = this._axis(axesR, 3);
    const rotX = this._axis(axesL, 2);
    if (moveX !== 0 || moveY !== 0) {
      const xrCam = this.renderer.xr.getCamera();
      const forward = this._camForward.set(0, 0, -1).transformDirection(xrCam.matrixWorld);
      forward.y = 0;
      forward.normalize();
      const right = new THREE.Vector3().crossVectors(forward, new THREE.Vector3(0, 1, 0));
      this.arPosition.addScaledVector(right, moveX * MOVE_SPEED * dt).addScaledVector(forward, -moveY * MOVE_SPEED * dt);
    }
    if (rotX !== 0) {
      const deltaYaw = -rotX * ROTATE_SPEED * dt;
      this.arQuaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), deltaYaw));
    }
  }

  _axis(axes, index) {
    let v = axes && axes.length > index ? axes[index] : 0;
    if ((!v || Math.abs(v) <= DEADZONE) && axes && axes.length > 1 && index >= 2) v = axes[index - 2] || 0;
    return Math.abs(v) > DEADZONE ? v : 0;
  }

  _triggerPressedEdge() {
    const r = !!this.gamepads.right?.buttons?.[0]?.pressed;
    const l = !!this.gamepads.left?.buttons?.[0]?.pressed;
    const edge = (r && !this._prevTrigger.right) || (l && !this._prevTrigger.left);
    this._prevTrigger.right = r;
    this._prevTrigger.left = l;
    return edge;
  }

  confirmPlacement() {
    if (!this.hasHit || this.placed) return false;
    this.placed = true;
    this.previewGroup.visible = false;
    if (this.onPlaced) this.onPlaced(this.getPlacement());
    return true;
  }

  resetPlacement() {
    this.hasHit = false;
    this.placed = false;
    this.hitTestSource = null;
    this.hitTestSourceRequested = false;
    this._prevTrigger.left = false;
    this._prevTrigger.right = false;
    this.previewGroup.visible = false;
  }

  isPlaced() { return this.placed; }

  getPlacement() {
    const yaw = new THREE.Euler().setFromQuaternion(this.arQuaternion, 'YXZ').y;
    return { position: this.arPosition.clone(), quaternion: this.arQuaternion.clone(), angle: yaw };
  }

  // Left stick moves the placed miniature; right stick rotates it.
  getMoveInput() {
    const axesL = this.gamepads.left ? this.gamepads.left.axes : [];
    return { x: this._axis(axesL, 2), z: this._axis(axesL, 3) };
  }

  getRotateInput() {
    const axesR = this.gamepads.right ? this.gamepads.right.axes : [];
    return this._axis(axesR, 2);
  }

  _onSessionEnd() {
    this.session = null;
    this.hitTestSource = null;
    this.hitTestSourceRequested = false;
    this.hasHit = false;
    this.placed = false;
    if (this._savedBackground !== null) this.scene.background = this._savedBackground;
    this.scene.fog = this._savedFog;
    this.previewGroup.visible = false;
  }
}
