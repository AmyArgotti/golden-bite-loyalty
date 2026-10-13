"use client";

import { useEffect, useRef, useState } from "react";

type ScanPanelProps = {
  onScan: (scanValue: string) => Promise<void>;
};

type BarcodeDetectorLike = {
  detect: (source: CanvasImageSource) => Promise<Array<{ rawValue?: string }>>;
};

type BarcodeDetectorConstructor = new (options?: { formats?: string[] }) => BarcodeDetectorLike;

export function ScanPanel({ onScan }: ScanPanelProps) {
  const [scanValue, setScanValue] = useState("");
  const [cameraMessage, setCameraMessage] = useState("Paste a scanned barcode, member ID, or QR value.");
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectorRef = useRef<BarcodeDetectorLike | null>(null);
  const scanTimerRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  async function handleManualScan() {
    if (!scanValue.trim()) {
      return;
    }
    await onScan(scanValue.trim());
  }

  function stopCamera() {
    if (scanTimerRef.current) {
      window.clearInterval(scanTimerRef.current);
      scanTimerRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  }

  async function startCameraScan() {
    try {
      const BarcodeDetectorApi = (window as Window & { BarcodeDetector?: BarcodeDetectorConstructor }).BarcodeDetector;
      if (!BarcodeDetectorApi || !navigator.mediaDevices?.getUserMedia) {
        setCameraMessage("This browser does not support live barcode detection. Use the scan value field instead.");
        return;
      }

      detectorRef.current = new BarcodeDetectorApi({
        formats: ["qr_code", "code_128", "ean_13", "ean_8", "upc_a", "upc_e"],
      });
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
      setCameraMessage("Camera active. Point it at the barcode or QR code.");

      scanTimerRef.current = window.setInterval(async () => {
        if (!videoRef.current || !detectorRef.current) {
          return;
        }
        const results = await detectorRef.current.detect(videoRef.current);
        const nextValue = results.find((result) => result.rawValue)?.rawValue;
        if (nextValue) {
          setScanValue(nextValue);
          stopCamera();
          setCameraMessage(`Detected scan value: ${nextValue}`);
          await onScan(nextValue);
        }
      }, 900);
    } catch (error) {
      stopCamera();
      setCameraMessage(`Camera scan unavailable: ${(error as Error).message}`);
    }
  }

  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Scan</div>
        <h3 style={{ marginBottom: 8 }}>Barcode and QR scan</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Paste a raw scan value or use the device camera when the browser supports live detection.
        </p>
      </div>

      <div>
        <label className="field-label" htmlFor="scan-value">
          Scan value
        </label>
        <input
          id="scan-value"
          className="field-input"
          value={scanValue}
          onChange={(event) => setScanValue(event.target.value)}
          placeholder="GB-100001 or barcode/QR value"
        />
      </div>

      <div className="button-row">
        <button className="button-primary" type="button" onClick={handleManualScan}>
          Find by scan
        </button>
        <button className="button-secondary" type="button" onClick={cameraActive ? stopCamera : startCameraScan}>
          {cameraActive ? "Stop camera" : "Use device camera"}
        </button>
      </div>

      <p className="muted" style={{ margin: 0 }}>
        {cameraMessage}
      </p>

      <video
        ref={videoRef}
        className="camera-preview"
        style={{ display: cameraActive ? "block" : "none" }}
        playsInline
        muted
      />
    </div>
  );
}
