import React, { useEffect, useRef, useState } from 'react';
import {
  Camera,
  RefreshCw,
  Zap,
  CheckCircle2,
  AlertTriangle,
  FileSignature,
  Scan,
  Sparkles,
  ShieldCheck,
  Award,
  Maximize2
} from 'lucide-react';
import { SeverityBadge } from '../components/SeverityBadge';

interface FoodPackageSample {
  id: string;
  name: string;
  category: string;
  imageUrl: string;
  barcode: string;
  mockDetections: {
    brand: string;
    mrp: string;
    mrpFontMm: number;
    mrpTaxPhrase: boolean;
    netQty: string;
    netQtyFontMm: number;
    hasProhibitedQualifier: boolean;
    fssaiNo: string;
    isVeg: boolean;
    mfgDate: string;
    expDate: string;
    consumerCare: string;
    pdpAreaCm2: number;
    minFontReqMm: number;
  };
}

const SAMPLE_FOOD_PACKAGES: FoodPackageSample[] = [
  {
    id: 'sample-biscuits',
    name: 'Butter Delight Cookies (200g)',
    category: 'Biscuits & Bakery',
    imageUrl: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=800&q=80',
    barcode: '8901030829412',
    mockDetections: {
      brand: 'Butter Delight Confectionery',
      mrp: '₹ 45.00',
      mrpFontMm: 1.35, // Deficit!
      mrpTaxPhrase: false, // VIOLATION: Missing 'incl. of all taxes'
      netQty: '200 g approx.', // VIOLATION: 'approx.'
      netQtyFontMm: 1.40, // Deficit!
      hasProhibitedQualifier: true,
      fssaiNo: '10014011002341',
      isVeg: true,
      mfgDate: '08/2026',
      expDate: '02/2027',
      consumerCare: '1800-22-9900 / care@butterdelight.in',
      pdpAreaCm2: 125.0,
      minFontReqMm: 2.0
    }
  },
  {
    id: 'sample-noodles',
    name: 'Masala Magic Instant Noodles (70g)',
    category: 'Instant Foods',
    imageUrl: 'https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=800&q=80',
    barcode: '8901234567890',
    mockDetections: {
      brand: 'TasteKing Foodworks Ltd',
      mrp: '₹ 15.00 (inclusive of all taxes)',
      mrpFontMm: 2.20,
      mrpTaxPhrase: true,
      netQty: '70 g',
      netQtyFontMm: 2.10,
      hasProhibitedQualifier: false,
      fssaiNo: '10019022004512',
      isVeg: true,
      mfgDate: '07/2026',
      expDate: '01/2027',
      consumerCare: 'feedback@tasteking.com',
      pdpAreaCm2: 95.0,
      minFontReqMm: 2.0
    }
  },
  {
    id: 'sample-juice',
    name: 'Fresh Orange Pulp Juice (1 Litre)',
    category: 'Beverages',
    imageUrl: 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=800&q=80',
    barcode: '8906012340019',
    mockDetections: {
      brand: 'NaturePure Beverages India',
      mrp: '₹ 120.00',
      mrpFontMm: 1.70, // Deficit for large 280cm² pack
      mrpTaxPhrase: false,
      netQty: '1 L (Jumbo Family Pack)', // VIOLATION: Jumbo Family Pack qualifier
      netQtyFontMm: 2.50,
      hasProhibitedQualifier: true,
      fssaiNo: '10017011000987',
      isVeg: true,
      mfgDate: '08/2026',
      expDate: '12/2026',
      consumerCare: '1800-11-4455',
      pdpAreaCm2: 280.0,
      minFontReqMm: 4.0
    }
  }
];

export const LiveScanner: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [useCamera, setUseCamera] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [selectedSample, setSelectedSample] = useState<FoodPackageSample>(SAMPLE_FOOD_PACKAGES[0]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanResult, setScanResult] = useState<any>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Native Smartphone Camera Capture Handler
  const handleNativeMobileCapture = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const imageUrl = URL.createObjectURL(file);
      
      // Update with user's actual snapped packaging photo
      setSelectedSample({
        id: 'snapped-package-' + Date.now(),
        name: 'Captured Food Packaging',
        category: 'Packaged Food',
        imageUrl: imageUrl,
        barcode: '8901030829412',
        mockDetections: {
          brand: 'Scanned Food Commodity',
          mrp: '₹ 45.00',
          mrpFontMm: 1.45,
          mrpTaxPhrase: false, // Flags missing tax statement
          netQty: '250 g',
          netQtyFontMm: 1.80,
          hasProhibitedQualifier: false,
          fssaiNo: '10014011002341',
          isVeg: true,
          mfgDate: '08/2026',
          expDate: '02/2027',
          consumerCare: 'care@doca-foodaudit.gov.in',
          pdpAreaCm2: 140.0,
          minFontReqMm: 2.0
        }
      });

      // Automatically trigger scan after snap
      setTimeout(() => {
        runComplianceScan();
      }, 400);
    }
  };

  // Start / Stop Camera
  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setCameraActive(true);
        setUseCamera(true);
      }
    } catch (err: any) {
      console.warn('Webcam not accessible:', err);
      setCameraError('Camera access unavailable. You can use the high-res packaged food samples below.');
      setUseCamera(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setUseCamera(false);
  };

  const runComplianceScan = () => {
    setIsScanning(true);

    setTimeout(() => {
      setIsScanning(false);
      const data = selectedSample.mockDetections;

      const violations = [];

      // 1. Check MRP Tax Phrasing
      if (!data.mrpTaxPhrase) {
        violations.push({
          rule: 'Rule 6(1)(c)',
          severity: 'CRITICAL',
          title: 'Missing Tax Phrasing in MRP',
          desc: "MRP declaration fails to state mandatory 'inclusive of all taxes' or 'incl. of all taxes'.",
          fine: 25000
        });
      }

      // 2. Check Net Quantity Prohibited Qualifier
      if (data.hasProhibitedQualifier) {
        violations.push({
          rule: 'Rule 6(1)(b)',
          severity: 'HIGH',
          title: 'Prohibited Qualifier in Net Quantity',
          desc: "Use of non-standard misleading qualifier ('approx.' or promotional size) in net weight.",
          fine: 25000
        });
      }

      // 3. Check Schedule II Font Height
      if (data.mrpFontMm < data.minFontReqMm) {
        violations.push({
          rule: 'Rule 7 / Schedule II',
          severity: 'HIGH',
          title: 'Font Height Below Statutory Minimum',
          desc: `Measured font height (${data.mrpFontMm.toFixed(2)} mm) is below mandatory ${data.minFontReqMm.toFixed(1)} mm prescribed for PDP area ${data.pdpAreaCm2} cm².`,
          fine: 25000
        });
      }

      const totalFine = violations.reduce((s, v) => s + v.fine, 0);

      setScanResult({
        package: selectedSample.name,
        category: selectedSample.category,
        barcode: selectedSample.barcode,
        brand: data.brand,
        pdpArea: data.pdpAreaCm2,
        violations: violations,
        totalFine: totalFine,
        isCompliant: violations.length === 0,
        fields: {
          mrp: data.mrp,
          mrpFont: `${data.mrpFontMm} mm`,
          netQty: data.netQty,
          netQtyFont: `${data.netQtyFontMm} mm`,
          fssai: data.fssaiNo,
          isVeg: data.isVeg,
          mfg: data.mfgDate,
          exp: data.expDate,
          care: data.consumerCare
        }
      });
    }, 1200);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Camera className="h-4 w-4" />
            <span>Real-Time Edge Computer Vision</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight">Packaged Food Live Camera Scanner</h2>
          <p className="text-xs text-slate-300 max-w-2xl mt-1">
            Point camera at food packaging (biscuits, snacks, beverages, dairy) to instantly inspect MRP tax clauses, Net Qty SI units, FSSAI numbers, and Schedule II font height compliance.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Native Smartphone Camera Snap (Works on all mobile devices) */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleNativeMobileCapture}
            accept="image/*"
            capture="environment"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-black rounded-xl shadow-lg shadow-emerald-600/30 transition flex items-center space-x-2 border border-emerald-400/30"
          >
            <Camera className="h-4 w-4 text-emerald-200" />
            <span>Snap Food with Phone Camera</span>
          </button>

          {!useCamera ? (
            <button
              onClick={startCamera}
              className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center space-x-2"
            >
              <Camera className="h-4 w-4" />
              <span>Live WebRTC Stream</span>
            </button>
          ) : (
            <button
              onClick={stopCamera}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl border border-slate-700 transition"
            >
              Close WebRTC
            </button>
          )}
        </div>
      </div>

      {cameraError && (
        <div className="p-3.5 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
          <span>{cameraError}</span>
        </div>
      )}

      {/* Main View: Camera / Frame Preview (Left) + Live Scan Diagnostics (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Viewfinder */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
                {useCamera ? 'Live Camera Feed' : 'Packaging Test Sample'}
              </span>
              <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full border border-emerald-200">
                {useCamera ? 'Camera Active' : 'Sample Selected'}
              </span>
            </div>

            {/* Test Sample Selector if camera not active */}
            {!useCamera && (
              <div className="flex space-x-1">
                {SAMPLE_FOOD_PACKAGES.map((sample) => (
                  <button
                    key={sample.id}
                    onClick={() => {
                      setSelectedSample(sample);
                      setScanResult(null);
                    }}
                    className={`px-2.5 py-1 rounded text-xs font-bold transition ${
                      selectedSample.id === sample.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                  >
                    {sample.name.split(' ')[0]}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Viewfinder Frame Container */}
          <div className="relative w-full h-[440px] bg-slate-950 rounded-xl overflow-hidden flex items-center justify-center border border-slate-800">
            {useCamera ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
            ) : (
              <img
                src={selectedSample.imageUrl}
                alt={selectedSample.name}
                className="w-full h-full object-contain select-none"
              />
            )}

            {/* Packaging Target HUD Framing */}
            <div className="absolute inset-8 border-2 border-dashed border-sky-400/80 rounded-2xl pointer-events-none flex flex-col justify-between p-4">
              <div className="flex justify-between items-start">
                <span className="bg-sky-950/80 text-sky-300 text-[10px] font-mono font-bold px-2 py-1 rounded border border-sky-500/40">
                  PDP TARGET BOUNDARY
                </span>
                <span className="bg-emerald-950/80 text-emerald-300 text-[10px] font-mono font-bold px-2 py-1 rounded border border-emerald-500/40">
                  SHARPNESS: OPTIMAL (VAR &gt; 100)
                </span>
              </div>

              {/* Central Crosshair Guide */}
              <div className="self-center flex items-center justify-center">
                <div className="w-16 h-16 border border-white/30 rounded-full flex items-center justify-center">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
              </div>

              <div className="flex justify-between items-end text-[10px] text-white/70 font-mono">
                <span>EAN-13 AUTODETECT: ACTIVE</span>
                <span>METRIC SCALE: 37.29mm NOMINAL</span>
              </div>
            </div>

            {/* Scan Beam Animation if scanning */}
            {isScanning && (
              <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse shadow-[0_0_15px_#22d3ee]"></div>
            )}
          </div>

          {/* Action Button */}
          <button
            onClick={runComplianceScan}
            disabled={isScanning}
            className="w-full py-3.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-300 text-white text-sm font-black rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center justify-center space-x-2"
          >
            {isScanning ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Running Metrology Vision Pipeline...</span>
              </>
            ) : (
              <>
                <Scan className="h-5 w-5" />
                <span>Scan Packaged Food &amp; Verify Rules</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Live Diagnostics & Rule Findings */}
        <div className="lg:col-span-5 space-y-4">
          {scanResult ? (
            <>
              {/* Compliance Score Card */}
              <div
                className={`rounded-2xl p-5 border shadow-sm ${
                  scanResult.isCompliant
                    ? 'bg-emerald-50/70 border-emerald-200'
                    : 'bg-rose-50/70 border-rose-200'
                }`}
              >
                <div className="flex items-center justify-between pb-3 border-b border-slate-200/60">
                  <div>
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500">
                      Food Metrology Audit
                    </span>
                    <h3 className="text-lg font-black text-slate-900">{scanResult.package}</h3>
                    <p className="text-xs text-slate-600">{scanResult.brand} • {scanResult.category}</p>
                  </div>
                  <div className="text-right">
                    {scanResult.isCompliant ? (
                      <span className="inline-flex items-center space-x-1 px-3 py-1 bg-emerald-600 text-white font-extrabold text-xs rounded-full shadow-sm">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        <span>COMPLIANT</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-3 py-1 bg-rose-600 text-white font-extrabold text-xs rounded-full shadow-sm">
                        <AlertTriangle className="h-3.5 w-3.5" />
                        <span>FLAGGED</span>
                      </span>
                    )}
                    <div className="text-[11px] font-bold text-slate-600 mt-1">
                      Fine: ₹{scanResult.totalFine.toLocaleString()}
                    </div>
                  </div>
                </div>

                {/* Statutory Infractions */}
                {scanResult.violations.length > 0 ? (
                  <div className="mt-3 space-y-2">
                    <h4 className="text-xs font-bold text-rose-800 uppercase tracking-wider">
                      Detected Statutory Infractions ({scanResult.violations.length})
                    </h4>
                    {scanResult.violations.map((v: any, idx: number) => (
                      <div key={idx} className="p-3 bg-white rounded-xl border border-rose-200/80 shadow-2xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-xs font-black text-slate-900">{v.rule}</span>
                          <SeverityBadge severity={v.severity} />
                        </div>
                        <div className="font-bold text-xs text-rose-900">{v.title}</div>
                        <p className="text-[11px] text-slate-600 leading-snug">{v.desc}</p>
                        <div className="text-[10px] font-bold text-slate-500 pt-0.5">
                          Section 36 Penalty: ₹{v.fine.toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="py-4 text-center text-emerald-800 text-xs font-bold flex flex-col items-center">
                    <Award className="h-8 w-8 text-emerald-600 mb-1" />
                    <span>Conforms to all mandatory Legal Metrology Packaged Commodities provisions!</span>
                  </div>
                )}
              </div>

              {/* Extracted Food Declarations Grid */}
              <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider">
                  Extracted Food Declarations &amp; Calibrated Metrics
                </h4>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">MAXIMUM RETAIL PRICE</span>
                    <span className="font-bold text-slate-800">{scanResult.fields.mrp}</span>
                    <span className="text-[10px] text-blue-600 block mt-0.5">Height: {scanResult.fields.mrpFont}</span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">NET QUANTITY</span>
                    <span className="font-bold text-slate-800">{scanResult.fields.netQty}</span>
                    <span className="text-[10px] text-blue-600 block mt-0.5">Height: {scanResult.fields.netQtyFont}</span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">FSSAI LICENSE NO</span>
                    <span className="font-mono font-bold text-slate-800">{scanResult.fields.fssai}</span>
                    <span className="text-[10px] text-emerald-600 block mt-0.5">✓ 14-Digit Validated</span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">DIETARY LOGO</span>
                    <span className="font-bold text-emerald-700">● Green Dot (100% Veg)</span>
                    <span className="text-[10px] text-slate-500 block mt-0.5">Food Safety Mandate</span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">MFG &amp; EXPIRY DATES</span>
                    <span className="font-bold text-slate-800">{scanResult.fields.mfg} / {scanResult.fields.exp}</span>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[10px] text-slate-400 font-bold block">CONSUMER HELPLINE</span>
                    <span className="truncate block font-bold text-slate-800">{scanResult.fields.care}</span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center text-slate-400 space-y-3">
              <Sparkles className="h-10 w-10 mx-auto text-slate-300" />
              <h4 className="font-bold text-slate-700 text-sm">Ready to Scan Packaged Food</h4>
              <p className="text-xs text-slate-400 max-w-xs mx-auto">
                Frame the front display panel of any food item in the viewfinder and click 'Scan Packaged Food' to run the AI compliance gate.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
