'use client';

import React, { Suspense, useState, useRef, useMemo, useCallback } from 'react';
import { Canvas, useThree, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage, Grid, GizmoHelper, GizmoViewport, Html } from '@react-three/drei';
import * as THREE from 'three';
import { Box, Eye, Crosshair, Scissors, RotateCcw, Download, Maximize2, Loader2 } from 'lucide-react';

// ────────── 3D Model with clipping support ──────────
function Model({ url, clippingPlane, wireframe }: { url: string; clippingPlane: THREE.Plane | null; wireframe: boolean }) {
  const { scene } = useGLTF(url);
  
  React.useEffect(() => {
    scene.traverse((child: any) => {
      if (child.isMesh) {
        child.material = child.material.clone();
        child.material.wireframe = wireframe;
        if (clippingPlane) {
          child.material.clippingPlanes = [clippingPlane];
          child.material.clipShadows = true;
        } else {
          child.material.clippingPlanes = [];
        }
        child.material.needsUpdate = true;
      }
    });
  }, [scene, clippingPlane, wireframe]);

  return <primitive object={scene} />;
}

// ────────── Wireframe Ghost (Loading placeholder) ──────────
function WireframeGhost() {
  const meshRef = useRef<THREE.Mesh>(null);
  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5;
    }
  });
  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[40, 20, 40]} />
      <meshBasicMaterial wireframe color="#3B82F6" transparent opacity={0.3} />
    </mesh>
  );
}

// ────────── Clipping Plane Visualizer ──────────
function ClipPlaneHelper({ plane, visible }: { plane: THREE.Plane; visible: boolean }) {
  const helperRef = useRef<THREE.PlaneHelper>(null);
  if (!visible) return null;
  return <primitive object={new THREE.PlaneHelper(plane, 120, 0xef4444)} />;
}

// ────────── Camera Controller for View Presets ──────────
function CameraController({ preset }: { preset: string | null }) {
  const { camera } = useThree();
  React.useEffect(() => {
    if (!preset) return;
    const positions: Record<string, [number, number, number]> = {
      front: [0, 0, 150],
      top: [0, 150, 0.01],
      right: [150, 0, 0],
      iso: [100, 80, 100],
    };
    const pos = positions[preset] || positions.iso;
    camera.position.set(...pos);
    camera.lookAt(0, 0, 0);
    camera.updateProjectionMatrix();
  }, [preset, camera]);
  return null;
}

// ────────── View Preset Toolbar ──────────
const VIEW_PRESETS = [
  { key: 'front', label: 'Front', icon: '⬜' },
  { key: 'top', label: 'Top', icon: '⬛' },
  { key: 'right', label: 'Right', icon: '◻️' },
  { key: 'iso', label: 'Iso', icon: '◇' },
];

// ────────── Parametric Input Slider ──────────
const ParamSlider = ({ label, value, min, max, unit, onChange }: {
  label: string; value: number; min: number; max: number; unit: string;
  onChange: (v: number) => void;
}) => (
  <div style={{ marginBottom: '12px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
      <span style={{ fontSize: '11px', fontWeight: '600', color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</span>
      <span style={{ fontSize: '12px', fontWeight: '700', color: '#0F172A', fontFamily: 'Space Grotesk, monospace' }}>{value}{unit}</span>
    </div>
    <input type="range" min={min} max={max} value={value} onChange={e => onChange(Number(e.target.value))}
      style={{ width: '100%', accentColor: '#2563EB', height: '4px', cursor: 'pointer' }} />
  </div>
);

// ────────── Export Button ──────────
const ExportButton = ({ url, format, size }: { url: string; format: string; size: string }) => (
  <a href={url} target="_blank" rel="noopener noreferrer"
    style={{
      display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px',
      border: '1px solid #E2E8F0', borderRadius: '8px', fontSize: '12px', fontWeight: '600',
      color: '#334155', textDecoration: 'none', background: '#FAFAFA',
      transition: 'all 0.15s ease',
    }}
    onMouseEnter={e => { e.currentTarget.style.borderColor = '#2563EB'; e.currentTarget.style.color = '#2563EB'; }}
    onMouseLeave={e => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.color = '#334155'; }}
  >
    <Download style={{ width: '14px', height: '14px' }} />
    <span>{format}</span>
    <span style={{ fontSize: '10px', color: '#94A3B8', fontWeight: '500' }}>{size}</span>
  </a>
);

// ────────── Main Component ──────────
interface ThreeViewerProps {
  modelUrl: string | null;
  isGenerating?: boolean;
  generationStatus?: string;
  cadData?: any;
}

export default function ThreeViewer({ modelUrl, isGenerating = false, generationStatus = '', cadData }: ThreeViewerProps) {
  const [activePreset, setActivePreset] = useState<string>('iso');
  const [showSection, setShowSection] = useState(false);
  const [clipOffset, setClipOffset] = useState(0);
  const [showWireframe, setShowWireframe] = useState(false);

  // Parametric inputs (cosmetic — would trigger backend re-gen in production)
  const [params, setParams] = useState({
    span: cadData?.parameters?.span_mm || 450,
    wallThickness: cadData?.parameters?.wall_thickness_mm || 3,
    motorSpacing: cadData?.parameters?.motor_spacing_mm || 200,
    armAngle: cadData?.parameters?.arm_angle_deg || 45,
  });

  const clippingPlane = useMemo(() => {
    if (!showSection) return null;
    return new THREE.Plane(new THREE.Vector3(0, -1, 0), clipOffset);
  }, [showSection, clipOffset]);

  const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';
  const baseUrl = API.replace('/api/v1', '');

  return (
    <div style={{ display: 'flex', gap: '0', borderRadius: '12px', overflow: 'hidden', border: '1px solid #E2E8F0', background: '#fff' }}>

      {/* ── 3D Viewport (70%) ── */}
      <div style={{ flex: '7', position: 'relative', background: '#0F172A', minHeight: '500px' }}>

        {/* View Presets Toolbar */}
        <div style={{
          position: 'absolute', top: '12px', left: '12px', zIndex: 20,
          display: 'flex', gap: '4px', background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(8px)',
          borderRadius: '8px', padding: '4px', border: '1px solid rgba(255,255,255,0.08)',
        }}>
          {VIEW_PRESETS.map(p => (
            <button key={p.key} onClick={() => setActivePreset(p.key)}
              style={{
                padding: '6px 10px', border: 'none', borderRadius: '6px', cursor: 'pointer',
                fontSize: '11px', fontWeight: '600', letterSpacing: '0.03em',
                background: activePreset === p.key ? 'rgba(37,99,235,0.9)' : 'transparent',
                color: activePreset === p.key ? 'white' : 'rgba(255,255,255,0.5)',
                transition: 'all 0.15s ease',
              }}>
              {p.label}
            </button>
          ))}
        </div>

        {/* Tool buttons (top-right) */}
        <div style={{
          position: 'absolute', top: '12px', right: '12px', zIndex: 20,
          display: 'flex', gap: '4px', background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(8px)',
          borderRadius: '8px', padding: '4px', border: '1px solid rgba(255,255,255,0.08)',
        }}>
          <button onClick={() => setShowSection(!showSection)}
            title="Section/Clipping Plane"
            style={{
              padding: '6px 8px', border: 'none', borderRadius: '6px', cursor: 'pointer',
              background: showSection ? 'rgba(239,68,68,0.8)' : 'transparent',
              color: showSection ? 'white' : 'rgba(255,255,255,0.5)',
              display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', fontWeight: '600',
            }}>
            <Scissors style={{ width: '14px', height: '14px' }} />
            Section
          </button>
          <button onClick={() => setShowWireframe(!showWireframe)}
            title="Wireframe View"
            style={{
              padding: '6px 8px', border: 'none', borderRadius: '6px', cursor: 'pointer',
              background: showWireframe ? 'rgba(139,92,246,0.8)' : 'transparent',
              color: showWireframe ? 'white' : 'rgba(255,255,255,0.5)',
              display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', fontWeight: '600',
            }}>
            <Box style={{ width: '14px', height: '14px' }} />
            Wire
          </button>
          <button onClick={() => setActivePreset('iso')}
            title="Reset View"
            style={{
              padding: '6px 8px', border: 'none', borderRadius: '6px', cursor: 'pointer',
              background: 'transparent', color: 'rgba(255,255,255,0.5)',
              display: 'flex', alignItems: 'center', fontSize: '11px', fontWeight: '600',
            }}>
            <RotateCcw style={{ width: '14px', height: '14px' }} />
          </button>
        </div>

        {/* Section plane slider */}
        {showSection && (
          <div style={{
            position: 'absolute', bottom: '16px', left: '50%', transform: 'translateX(-50%)',
            zIndex: 20, background: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(8px)',
            borderRadius: '10px', padding: '8px 16px', border: '1px solid rgba(255,255,255,0.1)',
            display: 'flex', alignItems: 'center', gap: '12px', minWidth: '280px',
          }}>
            <span style={{ fontSize: '11px', color: '#EF4444', fontWeight: '600' }}>CLIP</span>
            <input type="range" min={-60} max={60} value={clipOffset}
              onChange={e => setClipOffset(Number(e.target.value))}
              style={{ flex: 1, accentColor: '#EF4444' }} />
            <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', fontFamily: 'monospace' }}>{clipOffset}mm</span>
          </div>
        )}

        {/* Status badge */}
        <div style={{
          position: 'absolute', bottom: '16px', left: '12px', zIndex: 20,
          background: 'rgba(15,23,42,0.85)', backdropFilter: 'blur(8px)',
          borderRadius: '6px', padding: '4px 10px', border: '1px solid rgba(255,255,255,0.06)',
          fontSize: '10px', fontWeight: '600', letterSpacing: '0.05em', textTransform: 'uppercase',
          color: isGenerating ? '#60A5FA' : modelUrl ? '#34D399' : '#94A3B8',
          display: 'flex', alignItems: 'center', gap: '6px',
        }}>
          {isGenerating && <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#3B82F6', animation: 'pulse 1.5s infinite' }} />}
          {isGenerating ? (generationStatus || 'Generating CAD...') : modelUrl ? 'Model Loaded' : 'Awaiting Generation'}
        </div>

        {/* Three.js Canvas */}
        <Canvas
          shadows
          camera={{ position: [100, 80, 100], fov: 50 }}
          gl={{ localClippingEnabled: true }}
          style={{ background: '#0F172A' }}
        >
          <CameraController preset={activePreset} />
          <ambientLight intensity={0.4} />
          <directionalLight position={[10, 10, 5]} intensity={0.8} castShadow />

          <Suspense fallback={
            <Html center>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <WireframeGhost />
              </div>
            </Html>
          }>
            {modelUrl ? (
              <Stage environment="city" intensity={0.3} adjustCamera={false}>
                <Model url={modelUrl} clippingPlane={clippingPlane} wireframe={showWireframe} />
              </Stage>
            ) : isGenerating ? (
              <WireframeGhost />
            ) : null}
          </Suspense>

          {clippingPlane && <ClipPlaneHelper plane={clippingPlane} visible={showSection} />}

          <Grid infiniteGrid fadeDistance={200} fadeStrength={2} cellColor="#1E293B" sectionColor="#334155" />
          <OrbitControls makeDefault enableZoom enablePan />
          <GizmoHelper alignment="bottom-right" margin={[64, 64]}>
            <GizmoViewport labelColor="white" axisHeadScale={0.8} />
          </GizmoHelper>
        </Canvas>
      </div>

      {/* ── Right Spec Panel (30%) ── */}
      <div style={{
        flex: '3', background: '#FAFBFC', borderLeft: '1px solid #E2E8F0',
        padding: '20px', overflowY: 'auto', maxHeight: '500px',
        display: 'flex', flexDirection: 'column', gap: '20px',
      }}>
        {/* Title */}
        <div>
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0F172A', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Crosshair style={{ width: '16px', height: '16px', color: '#2563EB' }} />
            Parametric Editor
          </h3>
          <p style={{ fontSize: '11px', color: '#94A3B8', margin: 0 }}>Adjust dimensions to regenerate</p>
        </div>

        {/* Parametric Sliders */}
        <div style={{ borderBottom: '1px solid #E2E8F0', paddingBottom: '16px' }}>
          <ParamSlider label="Motor Span" value={params.span} min={200} max={800} unit="mm"
            onChange={v => setParams(p => ({ ...p, span: v }))} />
          <ParamSlider label="Wall Thickness" value={params.wallThickness} min={1} max={8} unit="mm"
            onChange={v => setParams(p => ({ ...p, wallThickness: v }))} />
          <ParamSlider label="Motor Spacing" value={params.motorSpacing} min={100} max={400} unit="mm"
            onChange={v => setParams(p => ({ ...p, motorSpacing: v }))} />
          <ParamSlider label="Arm Angle" value={params.armAngle} min={15} max={90} unit="°"
            onChange={v => setParams(p => ({ ...p, armAngle: v }))} />
          <button style={{
            width: '100%', padding: '8px', border: '1px solid #BFDBFE', borderRadius: '8px',
            background: '#EFF6FF', color: '#2563EB', fontSize: '12px', fontWeight: '700',
            cursor: 'pointer', marginTop: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
          }}>
            <RotateCcw style={{ width: '13px', height: '13px' }} />
            Regenerate Model
          </button>
        </div>

        {/* Spec Card */}
        <div>
          <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Model Specs</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { label: 'Type', value: cadData?.parameters?.type || 'Quadcopter Frame' },
              { label: 'Span', value: `${params.span}mm`, color: '#2563EB' },
              { label: 'Wall', value: `${params.wallThickness}mm` },
              { label: 'Motors', value: cadData?.parameters?.motor_count ?? '4' },
              { label: 'Material', value: cadData?.parameters?.material || 'CFRP' },
              { label: 'Mass Est.', value: cadData?.parameters?.mass_kg ? `${cadData.parameters.mass_kg}kg` : '~1.2kg', color: '#059669' },
            ].map(spec => (
              <div key={spec.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid #F1F5F9' }}>
                <span style={{ fontSize: '12px', color: '#64748B' }}>{spec.label}</span>
                <span style={{ fontSize: '13px', fontWeight: '700', color: spec.color || '#0F172A', fontFamily: 'Space Grotesk, monospace' }}>{spec.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Export Files */}
        {cadData && (
          <div>
            <h4 style={{ fontSize: '11px', fontWeight: '700', color: '#94A3B8', margin: '0 0 10px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Export Files</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {cadData.gltf_url && <ExportButton url={`${baseUrl}${cadData.gltf_url}`} format="GLTF" size="~2MB" />}
              {cadData.step_url && <ExportButton url={`${baseUrl}${cadData.step_url}`} format="STEP" size="~5MB" />}
              {cadData.stl_url && <ExportButton url={`${baseUrl}${cadData.stl_url}`} format="STL" size="~8MB" />}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
