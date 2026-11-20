/**
 * FALCON EYE — ULTRA-REALISTIC 3D CINEMATIC EAGLE FLIGHT OPENING
 * 
 * Cinematic Workflow:
 * 1. Dark Cinematic Navy Sky & Volumetric Clouds
 * 2. Realistic Eagle Entrance from Top-Right Corner with Articulated Wing Kinematics
 * 3. Authentic Bald Eagle Vocalization with Synchronized Beak Articulation
 * 4. Center Hover, Natural Banking Turn & Direct Camera Eye Contact
 * 5. Extreme Macro Zoom into Eagle Eye Pupil & Hyperspace Cyber-Vortex
 * 6. Metallic "FALCON EYE" Title Reveal with Electric Cyan Light Sweep & Sub-Bass Impact
 * 7. Seamless Transition into Existing Falcon Eye Homepage & Dashboard
 */

(function () {
  'use strict';

  // State
  let scene, camera, renderer, animationFrameId;
  let eagleRoot, torso, headNeckGroup, lowerBeak, leftWing, rightWing, tailGroup;
  let leftPrimaries = [], rightPrimaries = [];
  let clouds = [], hyperspaceParticles;
  let audioContext = null;
  let sounds = {};
  let isAnimationRunning = false;
  let introTimeline = null;

  // Dynamic Asset Resolver
  function getAssetBase() {
    if (window.location.pathname.includes('/frontend/') || window.location.pathname.endsWith('/frontend')) {
      return './assets/';
    }
    return './frontend/assets/';
  }

  // Configuration
  const BASE = getAssetBase();
  const CONFIG = {
    audio: {
      eagleCall: BASE + 'audio/bald_eagle_call.mp3',
      eagleShort: BASE + 'audio/eagle_screech_short.mp3',
      wingFlap: BASE + 'audio/wing_flap.wav',
      windAmbience: BASE + 'audio/wind_ambience.wav',
      cinematicImpact: BASE + 'audio/cinematic_impact.wav'
    },
    images: {
      flight: BASE + 'images/eagle_flight.jpg',
      closeup: BASE + 'images/eagle_closeup.jpg',
      pupilVortex: BASE + 'images/eagle_pupil_vortex.jpg'
    }
  };

  /**
   * Sound Engine — Supports Web Audio API & HTML5 Audio Fallback
   */
  const SoundEngine = {
    init: function () {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          audioContext = new AudioCtx();
        }
      } catch (e) {
        console.warn('[FalconEye Intro] Web Audio Context creation failed:', e);
      }

      // Preload Audio Elements
      for (const [key, url] of Object.entries(CONFIG.audio)) {
        const audio = new Audio();
        audio.src = url;
        audio.preload = 'auto';
        sounds[key] = audio;
      }
    },

    play: function (key, volume = 1.0, loop = false) {
      if (!sounds[key]) return;
      try {
        const audio = sounds[key];
        audio.volume = Math.max(0, Math.min(1, volume));
        audio.loop = loop;
        audio.currentTime = 0;
        const playPromise = audio.play();
        if (playPromise !== undefined) {
          playPromise.catch(err => {
            console.warn(`[FalconEye Intro] Audio autoplay prevented for ${key}:`, err);
          });
        }
      } catch (e) {
        console.warn(`[FalconEye Intro] Error playing sound ${key}:`, e);
      }
    },

    stop: function (key) {
      if (sounds[key]) {
        try {
          sounds[key].pause();
          sounds[key].currentTime = 0;
        } catch (e) {}
      }
    },

    fadeOut: function (key, duration = 1.0) {
      if (!sounds[key]) return;
      const audio = sounds[key];
      const startVol = audio.volume;
      const startTime = performance.now();
      function step() {
        const elapsed = (performance.now() - startTime) / 1000;
        if (elapsed < duration) {
          audio.volume = Math.max(0, startVol * (1 - elapsed / duration));
          requestAnimationFrame(step);
        } else {
          audio.volume = 0;
          audio.pause();
        }
      }
      step();
    }
  };

  /**
   * Create Texture Canvas for Procedural Eagle Feathers
   */
  function createFeatherTexture(isWhite = false) {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');

    // Base plumage tone
    if (isWhite) {
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, 512, 512);

      // Feather striations (light silver & soft cream)
      for (let i = 0; i < 400; i++) {
        const y = Math.random() * 512;
        const len = 40 + Math.random() * 80;
        const x = Math.random() * 512;
        ctx.strokeStyle = Math.random() > 0.5 ? 'rgba(226, 232, 240, 0.45)' : 'rgba(203, 213, 225, 0.35)';
        ctx.lineWidth = 1 + Math.random() * 1.5;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + len, y + (Math.random() - 0.5) * 6);
        ctx.stroke();
      }
    } else {
      // Dark brown raptor body feathers
      const grad = ctx.createLinearGradient(0, 0, 512, 512);
      grad.addColorStop(0, '#1E140C');
      grad.addColorStop(0.5, '#2D1F13');
      grad.addColorStop(1, '#150E09');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 512, 512);

      // Individual feather quill barbs
      for (let i = 0; i < 600; i++) {
        const y = Math.random() * 512;
        const len = 30 + Math.random() * 70;
        const x = Math.random() * 512;
        ctx.strokeStyle = Math.random() > 0.4 ? 'rgba(84, 58, 38, 0.4)' : 'rgba(15, 10, 6, 0.6)';
        ctx.lineWidth = 1 + Math.random() * 1.8;
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x + len, y + (Math.random() - 0.5) * 8);
        ctx.stroke();
      }
    }

    const texture = new THREE.CanvasTexture(canvas);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    return texture;
  }

  /**
   * Build the 3D Eagle Character Model
   */
  function buildEagleModel() {
    eagleRoot = new THREE.Group();

    const brownTexture = createFeatherTexture(false);
    const whiteTexture = createFeatherTexture(true);

    // Materials
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x332215,
      map: brownTexture,
      roughness: 0.65,
      metalness: 0.05
    });

    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0xFFFFFF,
      map: whiteTexture,
      roughness: 0.55,
      metalness: 0.02
    });

    const beakMaterial = new THREE.MeshStandardMaterial({
      color: 0xF59E0B, // Golden yellow
      roughness: 0.3,
      metalness: 0.15
    });

    const eyeOuterMaterial = new THREE.MeshStandardMaterial({
      color: 0xFBBF24, // Intense amber iris
      roughness: 0.1,
      metalness: 0.3
    });

    const pupilMaterial = new THREE.MeshBasicMaterial({
      color: 0x020617 // Deep black pupil
    });

    // 1. Aerodynamic Torso
    const bodyGeo = new THREE.CylinderGeometry(0.7, 0.4, 2.6, 16, 8);
    bodyGeo.scale(1.2, 1.0, 0.8);
    bodyGeo.rotateX(Math.PI / 2);
    torso = new THREE.Mesh(bodyGeo, bodyMaterial);
    torso.position.set(0, 0, 0);
    eagleRoot.add(torso);

    // Muscular chest contour
    const chestGeo = new THREE.SphereGeometry(0.85, 16, 16);
    chestGeo.scale(1.1, 0.9, 1.3);
    const chest = new THREE.Mesh(chestGeo, bodyMaterial);
    chest.position.set(0, -0.15, 0.5);
    torso.add(chest);

    // 2. White Feathered Tail
    tailGroup = new THREE.Group();
    tailGroup.position.set(0, 0.1, -1.3);
    for (let i = -3; i <= 3; i++) {
      const featherGeo = new THREE.BoxGeometry(0.22, 0.03, 1.2);
      featherGeo.translate(0, 0, -0.6);
      const feather = new THREE.Mesh(featherGeo, headMaterial);
      feather.rotation.y = (i * 0.08);
      feather.rotation.z = (i * 0.04);
      tailGroup.add(feather);
    }
    torso.add(tailGroup);

    // 3. Articulated White Feathered Head & Neck
    headNeckGroup = new THREE.Group();
    headNeckGroup.position.set(0, 0.25, 1.2);

    // Neck
    const neckGeo = new THREE.CylinderGeometry(0.5, 0.65, 0.9, 14);
    neckGeo.rotateX(Math.PI / 3);
    const neck = new THREE.Mesh(neckGeo, headMaterial);
    neck.position.set(0, 0.25, 0.3);
    headNeckGroup.add(neck);

    // Head
    const headGeo = new THREE.SphereGeometry(0.52, 16, 16);
    headGeo.scale(1.0, 1.05, 1.25);
    const head = new THREE.Mesh(headGeo, headMaterial);
    head.position.set(0, 0.65, 0.7);
    headNeckGroup.add(head);

    // Brow ridge for fierce eagle look
    const browGeo = new THREE.BoxGeometry(0.78, 0.14, 0.38);
    const brow = new THREE.Mesh(browGeo, headMaterial);
    brow.position.set(0, 0.8, 0.85);
    headNeckGroup.add(brow);

    // Sharp Intelligent Eyes (Left & Right)
    [-0.32, 0.32].forEach((xPos, idx) => {
      const eyePivot = new THREE.Group();
      eyePivot.position.set(xPos, 0.72, 0.95);

      const sclera = new THREE.Mesh(new THREE.SphereGeometry(0.12, 12, 12), eyeOuterMaterial);
      sclera.scale.set(0.6, 1, 1);
      eyePivot.add(sclera);

      const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.06, 10, 10), pupilMaterial);
      pupil.position.set(xPos > 0 ? 0.05 : -0.05, 0.01, 0.07);
      eyePivot.add(pupil);

      // Corneal highlight reflection
      const highlight = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xFFFFFF })
      );
      highlight.position.set(xPos > 0 ? 0.06 : -0.06, 0.04, 0.09);
      eyePivot.add(highlight);

      headNeckGroup.add(eyePivot);
    });

    // 4. Hooked Beak with Articulated Lower Mandible
    // Upper Beak (Hooked)
    const upperBeakGeo = new THREE.ConeGeometry(0.2, 0.7, 10);
    upperBeakGeo.rotateX(Math.PI / 1.7);
    const upperBeak = new THREE.Mesh(upperBeakGeo, beakMaterial);
    upperBeak.position.set(0, 0.62, 1.35);
    upperBeak.scale.set(1.1, 1.3, 1.0);
    headNeckGroup.add(upperBeak);

    // Lower Mandible (Pivots open during call)
    lowerBeak = new THREE.Group();
    lowerBeak.position.set(0, 0.48, 1.15);
    const lowerBeakGeo = new THREE.ConeGeometry(0.16, 0.55, 8);
    lowerBeakGeo.rotateX(Math.PI / 1.85);
    const lowerMesh = new THREE.Mesh(lowerBeakGeo, beakMaterial);
    lowerMesh.position.set(0, 0, 0.22);
    lowerBeak.add(lowerMesh);
    headNeckGroup.add(lowerBeak);

    torso.add(headNeckGroup);

    // 5. Dual Anatomically Articulated Wings (Left & Right)
    function buildWing(isLeft) {
      const wingSide = isLeft ? 1 : -1;
      const wingRoot = new THREE.Group();
      wingRoot.position.set(wingSide * 0.65, 0.2, 0.2);

      // Inner Wing (Humerus bone & secondary flight feathers)
      const innerGeo = new THREE.BoxGeometry(1.6, 0.08, 0.9);
      innerGeo.translate(wingSide * 0.8, 0, -0.2);
      const innerMesh = new THREE.Mesh(innerGeo, bodyMaterial);
      wingRoot.add(innerMesh);

      // Outer Wing (Wrist joint & primary flight feathers)
      const outerWing = new THREE.Group();
      outerWing.position.set(wingSide * 1.6, 0, -0.2);

      const outerGeo = new THREE.BoxGeometry(1.8, 0.06, 0.8);
      outerGeo.translate(wingSide * 0.9, 0, -0.15);
      const outerMesh = new THREE.Mesh(outerGeo, bodyMaterial);
      outerWing.add(outerMesh);

      // Layered Individual Primary Feathers
      const primaryFeathers = [];
      for (let i = 0; i < 7; i++) {
        const pGeo = new THREE.BoxGeometry(0.25, 0.02, 1.4 + (i * 0.12));
        pGeo.translate(wingSide * (0.3 + i * 0.25), 0, -0.65 - (i * 0.08));
        const pMesh = new THREE.Mesh(pGeo, bodyMaterial);
        pMesh.rotation.y = wingSide * (0.12 + i * 0.04);
        outerWing.add(pMesh);
        primaryFeathers.push(pMesh);
      }

      wingRoot.add(outerWing);
      wingRoot.userData = { outerWing, primaryFeathers, side: wingSide };
      return wingRoot;
    }

    leftWing = buildWing(true);
    rightWing = buildWing(false);
    leftPrimaries = leftWing.userData.primaryFeathers;
    rightPrimaries = rightWing.userData.primaryFeathers;

    torso.add(leftWing);
    torso.add(rightWing);

    // Initial scale and orientation
    eagleRoot.scale.set(1.4, 1.4, 1.4);
    scene.add(eagleRoot);
  }

  /**
   * Build Dark Sky, Volumetric Clouds & Starfield
   */
  function buildSkyEnvironment() {
    // 1. Volumetric Drifting Clouds
    const cloudGeo = new THREE.PlaneGeometry(35, 18);
    const cloudCanvas = document.createElement('canvas');
    cloudCanvas.width = 256;
    cloudCanvas.height = 256;
    const ctx = cloudCanvas.getContext('2d');
    const grad = ctx.createRadialGradient(128, 128, 20, 128, 128, 120);
    grad.addColorStop(0, 'rgba(15, 30, 55, 0.85)');
    grad.addColorStop(0.5, 'rgba(10, 22, 42, 0.45)');
    grad.addColorStop(1, 'rgba(5, 11, 20, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 256, 256);

    const cloudTex = new THREE.CanvasTexture(cloudCanvas);
    const cloudMat = new THREE.MeshBasicMaterial({
      map: cloudTex,
      transparent: true,
      opacity: 0.6,
      depthWrite: false
    });

    for (let i = 0; i < 8; i++) {
      const cloud = new THREE.Mesh(cloudGeo, cloudMat);
      cloud.position.set(
        (Math.random() - 0.5) * 60,
        -5 + Math.random() * 20,
        -15 - Math.random() * 30
      );
      cloud.scale.set(1 + Math.random() * 0.8, 1 + Math.random() * 0.8, 1);
      scene.add(cloud);
      clouds.push(cloud);
    }

    // 2. Cosmic Depth Dust / Stars
    const starCount = 350;
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 120;
      starPos[i + 1] = (Math.random() - 0.5) * 80;
      starPos[i + 2] = -40 - Math.random() * 60;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({
      color: 0x93C5FD,
      size: 0.35,
      transparent: true,
      opacity: 0.8
    });
    const starField = new THREE.Points(starGeo, starMat);
    scene.add(starField);

    // 3. Cyber Hyperspace Vortex Particle Tunnel (For eye pupil transition)
    const tunnelCount = 1200;
    const tunnelGeo = new THREE.BufferGeometry();
    const tunnelPos = new Float32Array(tunnelCount * 3);
    const tunnelColors = new Float32Array(tunnelCount * 3);

    for (let i = 0; i < tunnelCount; i++) {
      const idx = i * 3;
      const angle = Math.random() * Math.PI * 2;
      const radius = 0.5 + Math.random() * 8.0;
      tunnelPos[idx] = Math.cos(angle) * radius;
      tunnelPos[idx + 1] = Math.sin(angle) * radius;
      tunnelPos[idx + 2] = -Math.random() * 80;

      // Electric cyan to neon blue
      tunnelColors[idx] = 0.0;
      tunnelColors[idx + 1] = 0.85 + Math.random() * 0.15;
      tunnelColors[idx + 2] = 1.0;
    }

    tunnelGeo.setAttribute('position', new THREE.BufferAttribute(tunnelPos, 3));
    tunnelGeo.setAttribute('color', new THREE.BufferAttribute(tunnelColors, 3));

    const tunnelMat = new THREE.PointsMaterial({
      size: 0.45,
      vertexColors: true,
      transparent: true,
      opacity: 0
    });

    hyperspaceParticles = new THREE.Points(tunnelGeo, tunnelMat);
    hyperspaceParticles.position.set(0, 0, 0);
    scene.add(hyperspaceParticles);
  }

  /**
   * Initialize Three.js Scene, Camera, Lights
   */
  function initThree() {
    const canvas = document.getElementById('intro-webgl-canvas');
    if (!canvas) return;

    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050B14, 0.018);

    camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(0, 0, 14);

    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      antialias: true,
      alpha: true
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;

    // Atmospheric Lighting
    const ambientLight = new THREE.AmbientLight(0x0A192F, 1.4);
    scene.add(ambientLight);

    const moonLight = new THREE.DirectionalLight(0xE0F2FE, 2.4);
    moonLight.position.set(18, 22, 16);
    scene.add(moonLight);

    const cyberRimLight = new THREE.DirectionalLight(0x00D9FF, 2.8);
    cyberRimLight.position.set(-16, -8, -12);
    scene.add(cyberRimLight);

    const warmBounceLight = new THREE.DirectionalLight(0x3B2012, 0.7);
    warmBounceLight.position.set(0, -15, 0);
    scene.add(warmBounceLight);

    buildSkyEnvironment();
    buildEagleModel();

    window.addEventListener('resize', onWindowResize);
  }

  function onWindowResize() {
    if (!camera || !renderer) return;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  /**
   * Natural Wingbeat Kinematics & Flight Kinematics
   */
  const FlightState = {
    flapSpeed: 4.8,       // Wing flaps per second
    flapAmplitude: 0.55,  // Wing flap angle
    isHovering: false,
    beakOpen: 0.0,
    bankingAngle: 0.0,
    headLookCamera: 0.0
  };

  function updateEagleKinematics(time) {
    if (!leftWing || !rightWing) return;

    // 1. Natural Sinusoidal Wingbeat
    let wingAngle = 0;
    if (!FlightState.isHovering) {
      wingAngle = Math.sin(time * FlightState.flapSpeed) * FlightState.flapAmplitude;

      // Wing flex & dihedral
      leftWing.rotation.z = wingAngle * 0.85;
      rightWing.rotation.z = -wingAngle * 0.85;

      leftWing.userData.outerWing.rotation.z = Math.sin(time * FlightState.flapSpeed - 0.4) * 0.45;
      rightWing.userData.outerWing.rotation.z = -Math.sin(time * FlightState.flapSpeed - 0.4) * 0.45;

      // Primary feather fanning
      leftPrimaries.forEach((p, idx) => {
        p.rotation.x = Math.sin(time * FlightState.flapSpeed + idx * 0.1) * 0.2;
      });
      rightPrimaries.forEach((p, idx) => {
        p.rotation.x = Math.sin(time * FlightState.flapSpeed + idx * 0.1) * 0.2;
      });

      // Torso lift & pitch with wingbeat
      torso.position.y = Math.sin(time * FlightState.flapSpeed) * 0.18;
      torso.rotation.x = Math.cos(time * FlightState.flapSpeed) * 0.05;

      // Tail pitch compensation
      tailGroup.rotation.x = -Math.sin(time * FlightState.flapSpeed) * 0.12;
    } else {
      // Hover Glide Mode — Wings spread wide in majestic dihedral
      const gentleHover = Math.sin(time * 2.2) * 0.12;
      leftWing.rotation.z = 0.22 + gentleHover;
      rightWing.rotation.z = -0.22 - gentleHover;
      leftWing.userData.outerWing.rotation.z = 0.08 + gentleHover * 0.5;
      rightWing.userData.outerWing.rotation.z = -0.08 - gentleHover * 0.5;

      torso.position.y = Math.sin(time * 1.5) * 0.08;
      tailGroup.rotation.x = 0.15 + Math.sin(time * 1.5) * 0.05;
    }

    // 2. Beak Synchronized Articulation
    if (lowerBeak) {
      lowerBeak.rotation.x = FlightState.beakOpen;
    }

    // 3. Head & Eye Tracking
    if (headNeckGroup) {
      headNeckGroup.rotation.y = FlightState.headLookCamera * 0.42;
      headNeckGroup.rotation.x = FlightState.headLookCamera * 0.15;
    }

    // 4. Clouds Drift
    clouds.forEach((cloud, i) => {
      cloud.position.x += (0.015 + (i % 3) * 0.008);
      if (cloud.position.x > 35) cloud.position.x = -35;
    });

    // 5. Hyperspace Vortex Particle Flow
    if (hyperspaceParticles && hyperspaceParticles.material.opacity > 0) {
      const positions = hyperspaceParticles.geometry.attributes.position.array;
      for (let i = 2; i < positions.length; i += 3) {
        positions[i] += 1.8;
        if (positions[i] > 10) positions[i] = -70;
      }
      hyperspaceParticles.geometry.attributes.position.needsUpdate = true;
      hyperspaceParticles.rotation.z += 0.015;
    }
  }

  function renderLoop() {
    if (!isAnimationRunning) return;
    const time = performance.now() * 0.001;

    updateEagleKinematics(time);
    renderer.render(scene, camera);
    animationFrameId = requestAnimationFrame(renderLoop);
  }

  /**
   * Main GSAP Cinematic Animation Timeline
   */
  function startCinematicTimeline() {
    introTimeline = gsap.timeline();

    // Initial Eagle Positioning: TOP-RIGHT CORNER, small & far away
    eagleRoot.position.set(22, 13, -38);
    eagleRoot.rotation.set(0.18, -0.65, 0.42); // Realistic banking into turn
    eagleRoot.scale.set(0.3, 0.3, 0.3);

    // Initial audio ambience
    SoundEngine.play('windAmbience', 0.6, true);

    // Periodically play wing flap sound during approach
    const flapInterval = setInterval(() => {
      if (!FlightState.isHovering && isAnimationRunning) {
        SoundEngine.play('wingFlap', 0.45);
      } else {
        clearInterval(flapInterval);
      }
    }, 450);

    // -------------------------------------------------------------
    // PHASE 1: Eagle Flies from TOP-RIGHT CORNER Diagonally to Center
    // -------------------------------------------------------------
    introTimeline.to(eagleRoot.position, {
      x: 0,
      y: 0.4,
      z: 0.5,
      duration: 3.8,
      ease: 'power2.out'
    }, 0);

    introTimeline.to(eagleRoot.scale, {
      x: 1.35,
      y: 1.35,
      z: 1.35,
      duration: 3.8,
      ease: 'power1.out'
    }, 0);

    // Natural banking roll into turn
    introTimeline.to(eagleRoot.rotation, {
      x: 0.05,
      y: -0.15,
      z: 0.05,
      duration: 3.8,
      ease: 'power2.out'
    }, 0);

    // -------------------------------------------------------------
    // PHASE 2: Authentic Eagle Screech Sound & Beak Synchronization
    // -------------------------------------------------------------
    introTimeline.call(() => {
      // Play real eagle call recording
      SoundEngine.play('eagleCall', 1.0);
    }, null, 2.5);

    // Synchronize beak opening with eagle call vocal harmonics
    introTimeline.to(FlightState, {
      beakOpen: 0.38, // Opens ~22 degrees
      duration: 0.28,
      ease: 'power2.out'
    }, 2.55);

    introTimeline.to(FlightState, {
      beakOpen: 0.18,
      duration: 0.32,
      yoyo: true,
      repeat: 3,
      ease: 'sine.inOut'
    }, 2.85);

    introTimeline.to(FlightState, {
      beakOpen: 0.0,
      duration: 0.45,
      ease: 'power2.in'
    }, 4.2);

    // -------------------------------------------------------------
    // PHASE 3: Center Flight, Leveling Out, and Looking at Camera
    // -------------------------------------------------------------
    introTimeline.call(() => {
      FlightState.isHovering = true; // Spreads wings into majestic hover glide
    }, null, 3.8);

    // Eagle turns head directly towards the camera, locking eyes
    introTimeline.to(FlightState, {
      headLookCamera: 1.0,
      duration: 1.2,
      ease: 'power2.out'
    }, 4.2);

    // Subtle eagle body hover
    introTimeline.to(eagleRoot.rotation, {
      y: 0.0,
      z: 0.0,
      duration: 1.5,
      ease: 'sine.inOut'
    }, 4.2);

    // -------------------------------------------------------------
    // PHASE 4: Extreme Eagle Eye Zoom Transition into Pupil Vortex
    // -------------------------------------------------------------
    // Camera zooms straight into the eagle's right eye
    introTimeline.to(camera.position, {
      x: 0.28,
      y: 0.88,
      z: 1.8,
      duration: 2.2,
      ease: 'power3.in'
    }, 5.8);

    // Hyperspace cyber-vortex particles activate as camera passes through pupil
    introTimeline.to(hyperspaceParticles.material, {
      opacity: 0.95,
      duration: 1.2,
      ease: 'power2.in'
    }, 7.0);

    // Electric cyan flash & warp
    introTimeline.to('#intro-warp-flash', {
      opacity: 0.85,
      duration: 0.45,
      ease: 'power4.in'
    }, 7.6);

    introTimeline.to('#intro-warp-flash', {
      opacity: 0.0,
      duration: 0.6,
      ease: 'power2.out'
    }, 8.05);

    // -------------------------------------------------------------
    // PHASE 5: Title Reveal with Sub-Bass Impact & Metallic Typography
    // -------------------------------------------------------------
    introTimeline.call(() => {
      SoundEngine.play('cinematicImpact', 1.0);
      document.getElementById('intro-title-overlay').classList.add('title-active');
    }, null, 8.1);

    // Animate title light sweep beam
    introTimeline.to('.title-light-sweep', {
      opacity: 1,
      duration: 0.4,
      ease: 'power2.in'
    }, 8.3);

    introTimeline.to('.title-light-sweep', {
      opacity: 0,
      duration: 0.8,
      ease: 'power2.out'
    }, 8.7);

    // -------------------------------------------------------------
    // PHASE 6: Smooth Reveal of Existing Falcon Eye Homepage
    // -------------------------------------------------------------
    introTimeline.to('#falcon-cinematic-intro', {
      opacity: 0,
      duration: 1.4,
      ease: 'power3.inOut',
      onComplete: finishIntro
    }, 11.2);
  }

  /**
   * Finalize Intro & Cleanly Reveal Existing Homepage
   */
  function finishIntro() {
    isAnimationRunning = false;
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }

    // Fade out wind ambience
    SoundEngine.fadeOut('windAmbience', 1.2);

    const introEl = document.getElementById('falcon-cinematic-intro');
    if (introEl) {
      introEl.classList.add('intro-hidden');
      setTimeout(() => {
        if (introEl.parentNode) {
          introEl.parentNode.removeChild(introEl);
        }
      }, 1400);
    }

    // Trigger Leaflet map resize once visible
    setTimeout(() => {
      if (window.commandMap) window.commandMap.invalidateSize();
      if (window.gisMap) window.gisMap.invalidateSize();
    }, 500);

    console.log('[FalconEye] Ultra-realistic cinematic 3D eagle flight intro complete.');
  }

  /**
   * Launch Experience — Triggered on "ENTER FALCON EYE" Gateway
   */
  window.launchFalconEyeExperience = function () {
    const gateway = document.getElementById('intro-gateway');
    if (gateway) {
      gateway.classList.add('gateway-dismissed');
    }

    // Unlock Web Audio context if suspended
    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume().catch(e => console.warn(e));
    }

    isAnimationRunning = true;
    renderLoop();
    startCinematicTimeline();
  };

  /**
   * Auto-Initialize on DOM Ready
   */
  document.addEventListener('DOMContentLoaded', function () {
    SoundEngine.init();
    initThree();

    // Check if browser allows autoplay without user gesture
    const enterBtn = document.getElementById('enter-falcon-btn');
    if (enterBtn) {
      enterBtn.addEventListener('click', function () {
        window.launchFalconEyeExperience();
      });
    }

    // Also support keyboard Enter or Space
    window.addEventListener('keydown', function (e) {
      if ((e.key === 'Enter' || e.key === ' ') && !isAnimationRunning) {
        const gateway = document.getElementById('intro-gateway');
        if (gateway && !gateway.classList.contains('gateway-dismissed')) {
          e.preventDefault();
          window.launchFalconEyeExperience();
        }
      }
    });
  });

})();
