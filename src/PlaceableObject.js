import * as THREE from 'three';

/**
 * PlaceableObject
 * ----------------
 * Wraps an Object3D root so every mode (desktop / VR / AR) applies
 * position, rotation and scale through ONE code path instead of
 * scattering `root.scale.setScalar(...)` calls across main.js.
 *
 * This mirrors the pattern used in هجولة عتابة to fix the
 * scale-consistency / ground-alignment bugs that show up when scale
 * and transform resets are duplicated in multiple event handlers.
 */
export class PlaceableObject {
  /**
   * @param {THREE.Object3D} object3D - the root/group being placed
   * @param {Object} [opts]
   * @param {number} [opts.desktopScale=1] - scale used outside AR
   * @param {number} [opts.arScale=0.32]   - scale used while placed in AR
   */
  constructor(object3D, { desktopScale = 1, arScale = 0.32 } = {}) {
    this.object3D = object3D;
    this.desktopScale = desktopScale;
    this.arScale = arScale;
    this.mode = 'desktop'; // 'desktop' | 'vr' | 'ar-pending' | 'ar-placed'
  }

  /** Swap the wrapped root (e.g. when main.js rebuilds a room). */
  setObject(object3D) {
    this.object3D = object3D;
    this._applyCurrentMode();
  }

  toDesktop() {
    this.mode = 'desktop';
    this._applyCurrentMode();
  }

  toVR() {
    this.mode = 'vr';
    this._applyCurrentMode();
  }

  /** Entered an AR session but the user hasn't tapped/confirmed a spot yet. */
  toARPending() {
    this.mode = 'ar-pending';
    if (!this.object3D) return;
    this.object3D.visible = false;
    this.object3D.scale.setScalar(this.arScale);
  }

  /** Apply a confirmed AR placement (position + rotation from ARManager). */
  placeInAR({ position, quaternion }) {
    if (!this.object3D) return;
    this.mode = 'ar-placed';
    this.object3D.position.copy(position);
    this.object3D.quaternion.copy(quaternion);
    this.object3D.scale.setScalar(this.arScale);
    this.object3D.visible = true;
  }

  /** Re-sync world position/rotation from a live XR anchor (drift correction). */
  syncFromAnchor(position, quaternion) {
    if (!this.object3D || this.mode !== 'ar-placed') return;
    this.object3D.position.copy(position);
    this.object3D.quaternion.copy(quaternion);
  }

  isPlacedInAR() {
    return this.mode === 'ar-placed';
  }

  /** Room was rebuilt while already placed in AR - keep the existing
   *  world position/rotation, just re-apply scale/visibility to the new root. */
  reapplyARPlacement() {
    if (!this.object3D) return;
    this.mode = 'ar-placed';
    this.object3D.scale.setScalar(this.arScale);
    this.object3D.visible = true;
  }

  _applyCurrentMode() {
    if (!this.object3D) return;
    if (this.mode === 'desktop' || this.mode === 'vr') {
      this.object3D.visible = true;
      this.object3D.scale.setScalar(this.desktopScale);
      this.object3D.position.set(0, 0, 0);
      this.object3D.quaternion.identity();
    } else if (this.mode === 'ar-pending') {
      this.object3D.visible = false;
      this.object3D.scale.setScalar(this.arScale);
    }
    // 'ar-placed' is left alone here; it's driven by placeInAR()/syncFromAnchor().
  }
}
