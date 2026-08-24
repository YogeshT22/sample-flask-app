# -----------------------------------------------------------------
# Flask Application 3.0
# Purpose: Demonstrate a CI/CD deployed app with:
#          - Premium dark glassmorphism UI
#          - Prometheus metrics instrumentation (/metrics)
#          - Environment-aware pod info
# -----------------------------------------------------------------

import os
import socket
# pyrefly: ignore [missing-import]
from flask import Flask, jsonify
# pyrefly: ignore [missing-import]
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# --- Configuration ---
APP_VERSION = os.environ.get('APP_VERSION', 'v1.0 - Default')

# --- Prometheus Metrics ---
# Auto-instruments all routes: request count, latency histogram, in-flight gauge.
# Exposes the /metrics endpoint (text/plain, Prometheus format).
metrics = PrometheusMetrics(app, excluded_paths=['/metrics'])
metrics.info('flask_app_info', 'Application version info', version=APP_VERSION)


@app.route('/')
def home():
    """Main endpoint — premium dark glassmorphism UI."""
    pod_hostname = socket.gethostname()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask App — CI/CD Pipeline</title>
    <meta name="description" content="Flask application deployed via Jenkins DevSecOps CI/CD pipeline on Kubernetes.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            background: #070c18;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        /* Dot-grid background */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image: radial-gradient(rgba(99,102,241,0.12) 1px, transparent 1px);
            background-size: 36px 36px;
            pointer-events: none;
            z-index: 0;
        }}

        /* Ambient glow orbs */
        .orb {{
            position: fixed;
            border-radius: 50%;
            filter: blur(100px);
            pointer-events: none;
            z-index: 0;
        }}
        .orb-1 {{
            width: 640px; height: 640px;
            background: rgba(99,102,241,0.16);
            top: -280px; left: -280px;
            animation: drift 14s ease-in-out infinite;
        }}
        .orb-2 {{
            width: 500px; height: 500px;
            background: rgba(6,182,212,0.10);
            bottom: -200px; right: -200px;
            animation: drift 18s ease-in-out infinite reverse;
        }}
        .orb-3 {{
            width: 340px; height: 340px;
            background: rgba(139,92,246,0.13);
            top: 40%; right: 8%;
            animation: drift 11s ease-in-out infinite 4s;
        }}

        @keyframes drift {{
            0%, 100% {{ transform: translate(0, 0); }}
            33%       {{ transform: translate(20px, -20px); }}
            66%       {{ transform: translate(-15px, 15px); }}
        }}

        /* Entrance animation */
        .container {{
            position: relative;
            z-index: 10;
            width: 100%;
            max-width: 680px;
            padding: 20px;
            animation: rise 0.75s cubic-bezier(0.16, 1, 0.3, 1) both;
        }}

        @keyframes rise {{
            from {{ opacity: 0; transform: translateY(28px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Glass card */
        .card {{
            background: rgba(255,255,255,0.032);
            backdrop-filter: blur(28px);
            -webkit-backdrop-filter: blur(28px);
            border: 1px solid rgba(255,255,255,0.065);
            border-radius: 28px;
            padding: 48px;
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.04) inset,
                0 40px 90px rgba(0,0,0,0.6);
        }}

        /* Status pill */
        .status {{
            display: inline-flex;
            align-items: center;
            gap: 9px;
            background: rgba(34,197,94,0.07);
            border: 1px solid rgba(34,197,94,0.22);
            color: #4ade80;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            padding: 6px 16px;
            border-radius: 100px;
            margin-bottom: 32px;
        }}

        .pulse {{
            width: 7px; height: 7px;
            background: #4ade80;
            border-radius: 50%;
            animation: blink 2s ease-in-out infinite;
            flex-shrink: 0;
        }}

        @keyframes blink {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(74,222,128,0.5); opacity: 1; }}
            50%       {{ box-shadow: 0 0 0 5px rgba(74,222,128,0);  opacity: 0.7; }}
        }}

        /* App icon */
        .app-icon {{
            width: 62px; height: 62px;
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            margin-bottom: 24px;
            box-shadow: 0 8px 30px rgba(99,102,241,0.4);
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.15;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #f1f5f9 0%, #8896b0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .lead {{
            font-size: 14px;
            color: #415572;
            line-height: 1.7;
            margin-bottom: 36px;
            max-width: 510px;
        }}

        /* Info grid */
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 32px;
        }}

        .cell {{
            background: rgba(255,255,255,0.022);
            border: 1px solid rgba(255,255,255,0.052);
            border-radius: 14px;
            padding: 14px 18px;
            transition: background 0.2s, border-color 0.2s, transform 0.2s;
            cursor: default;
        }}

        .cell:hover {{
            background: rgba(255,255,255,0.048);
            border-color: rgba(99,102,241,0.3);
            transform: translateY(-2px);
        }}

        .cell-label {{
            font-size: 10px;
            font-weight: 600;
            color: #2e4360;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}

        .cell-value {{
            font-size: 13px;
            font-weight: 500;
            color: #7b90a8;
        }}

        .cell-value.purple {{ color: #818cf8; }}
        .cell-value.green  {{ color: #34d399; font-size: 12px; }}

        /* Divider */
        .divider {{ border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 28px 0; }}

        /* Action buttons */
        .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 28px; }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 10px 20px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            box-shadow: 0 4px 16px rgba(99,102,241,0.35);
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(99,102,241,0.5);
        }}

        .btn-ghost {{
            background: rgba(255,255,255,0.04);
            color: #566a82;
            border: 1px solid rgba(255,255,255,0.06);
        }}
        .btn-ghost:hover {{
            background: rgba(255,255,255,0.08);
            color: #8896b0;
            border-color: rgba(255,255,255,0.12);
        }}

        /* Pipeline trail */
        .pipeline-label {{
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.9px;
            color: #213040;
            margin-bottom: 10px;
        }}

        .pipeline {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 5px;
        }}

        .step {{
            font-size: 11px;
            font-weight: 500;
            padding: 4px 11px;
            border-radius: 7px;
            background: rgba(34,197,94,0.07);
            color: #4ade80;
            border: 1px solid rgba(34,197,94,0.18);
            transition: background 0.2s;
        }}
        .step:hover {{ background: rgba(34,197,94,0.13); }}

        .arrow {{ color: #1a3040; font-size: 14px; user-select: none; }}
    </style>
</head>
<body>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>

    <div class="container">
        <div class="card">

            <div class="status">
                <span class="pulse"></span>
                Deployed &amp; Running
            </div>

            <div class="app-icon">🚀</div>

            <h1>Flask Application</h1>
            <p class="lead">
                Continuously delivered through a Jenkins DevSecOps pipeline —
                vulnerability&#8209;scanned, cosign&#8209;signed, and orchestrated on Kubernetes.
            </p>

            <div class="grid">
                <div class="cell">
                    <div class="cell-label">Version</div>
                    <div class="cell-value purple">{APP_VERSION}</div>
                </div>
                <div class="cell">
                    <div class="cell-label">Pod</div>
                    <div class="cell-value green">{pod_hostname}</div>
                </div>
                <div class="cell">
                    <div class="cell-label">Orchestration</div>
                    <div class="cell-value">Kubernetes (k3d)</div>
                </div>
                <div class="cell">
                    <div class="cell-label">WSGI Server</div>
                    <div class="cell-value">Gunicorn &middot; 2 workers</div>
                </div>
            </div>

            <hr class="divider">

            <div class="actions">
                <a href="/health"  class="btn btn-primary" id="health-btn">&#9829;&nbsp; Health</a>
                <a href="/metrics" class="btn btn-ghost"   id="metrics-btn">&#128202;&nbsp; Metrics</a>
            </div>

            <div class="pipeline-label">CI/CD Pipeline</div>
            <div class="pipeline">
                <span class="step">Git Push</span>
                <span class="arrow">›</span>
                <span class="step">Secret Scan</span>
                <span class="arrow">›</span>
                <span class="step">Build &amp; Push</span>
                <span class="arrow">›</span>
                <span class="step">Trivy Scan</span>
                <span class="arrow">›</span>
                <span class="step">SBOM</span>
                <span class="arrow">›</span>
                <span class="step">Cosign Sign</span>
                <span class="arrow">›</span>
                <span class="step">K8s Deploy</span>
                <span class="arrow">›</span>
                <span class="step">k6 Test</span>
            </div>

        </div>
    </div>
</body>
</html>"""
    return html


@app.route('/health')
def health_check():
    """Health check endpoint used by Kubernetes readiness and liveness probes."""
    return jsonify(
        status="ok",
        version=APP_VERSION,
        pod=socket.gethostname(),
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
