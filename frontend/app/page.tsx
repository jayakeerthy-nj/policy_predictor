"use client";

import { type CSSProperties, useMemo, useState } from "react";

type DomainImpact = {
  domain: string;
  impact_percent: number;
  direction: "increase" | "decrease" | "neutral";
  confidence: number;
  feature_importance: Record<string, number>;
};

type PredictionResponse = {
  prediction_id: string;
  country: string;
  impacts: DomainImpact[];
};

type ScenarioPoint = {
  domain: string;
  baseline: number;
  shock: number;
  policy_adjusted: number;
};

type ScenarioResponse = {
  scenario_id: string;
  country: string;
  scenarios: ScenarioPoint[];
  explanation: string;
};

type GraphResponse = {
  nodes: string[];
  edges: Array<{ source: string; target: string; weight: number }>;
  ripple_effects: Record<string, number>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

/* ── Light Theme Styling ── */
const COLORS = {
  bg: "#f7f8fa",
  card: "white",
  cardBorder: "#e0e0e0",
  green: "#2e7d32",
  red: "#c62828",
  orange: "#f57c00",
  blue: "#1976d2",
  text: "#000000",
  textMuted: "#444444",
  textLight: "#666666",
  surface: "#f0f0f0",
};

const cardStyle: CSSProperties = {
  border: `1px solid ${COLORS.cardBorder}`,
  borderRadius: "10px",
  padding: "1.5rem",
  background: COLORS.card,
  boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
};

/* ── SVG Bar Chart for Domain Impacts ── */
function ImpactChart({ impacts }: { impacts: DomainImpact[] }) {
  const W = 400, barH = 14, gap = 16, padL = 90, padR = 60;
  const H = impacts.length * (barH + gap) + 10;
  const maxAbs = Math.max(10, ...impacts.map((i) => Math.abs(i.impact_percent)));

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ overflow: "visible", marginTop: "1rem" }}>
      {impacts.map((imp, idx) => {
        const y = idx * (barH + gap) + 5;
        const val = imp.impact_percent;
        const barW = (Math.abs(val) / maxAbs) * (W - padL - padR);
        const col = val > 0 ? COLORS.green : val < 0 ? COLORS.red : COLORS.textLight;
        return (
          <g key={imp.domain}>
            <text x={padL - 8} y={y + barH / 2 + 4} textAnchor="end" fill={COLORS.text} fontSize="12" fontWeight="bold" style={{ textTransform: "capitalize" }}>
              {imp.domain}
            </text>
            <rect x={padL} y={y} width={W - padL - padR} height={barH} rx="4" fill={COLORS.surface} />
            <rect x={padL} y={y} width={barW} height={barH} rx="4" fill={col}>
              <animate attributeName="width" from="0" to={barW} dur="0.5s" fill="freeze" />
            </rect>
            <text x={padL + barW + 8} y={y + barH / 2 + 4} fill={COLORS.textMuted} fontSize="11">
              {val.toFixed(2)}%
            </text>
          </g>
        );
      })}
    </svg>
  );
}

/* ── Final Verdict Section ── */
function VerdictSection({ impacts, explanation }: { impacts: DomainImpact[]; explanation: string }) {
  const positives = impacts.filter((i) => i.impact_percent > 1);
  const negatives = impacts.filter((i) => i.impact_percent < -1);
  const neutral = impacts.filter((i) => Math.abs(i.impact_percent) <= 1);

  const overallScore = impacts.reduce((sum, i) => sum + i.impact_percent, 0) / (impacts.length || 1);
  const verdict = overallScore > 2 ? "Mostly Beneficial" : overallScore < -2 ? "Mostly Harmful" : "Mixed Impact";
  const verdictColor = overallScore > 2 ? COLORS.green : overallScore < -2 ? COLORS.red : COLORS.orange;

  return (
    <div style={{ ...cardStyle, marginTop: "1.5rem" }}>
      <h2 style={{ marginTop: 0, fontSize: "1.25rem", color: COLORS.text, borderBottom: `1px solid ${COLORS.surface}`, paddingBottom: "0.75rem", marginBottom: "1rem" }}>
        Final Verdict: <span style={{ color: verdictColor }}>{verdict}</span>
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem", marginBottom: "1.5rem" }}>
        {/* Benefits */}
        <div>
          <h3 style={{ margin: "0 0 0.75rem", fontSize: "1.05rem", color: COLORS.green }}>Benefits</h3>
          {positives.length === 0 ? (
            <p style={{ color: COLORS.textLight, fontSize: "0.95rem", margin: 0 }}>No significant positive impacts predicted.</p>
          ) : (
            <ul style={{ margin: 0, paddingLeft: "1.2rem", color: COLORS.textMuted }}>
              {positives.map((i) => (
                <li key={i.domain} style={{ marginBottom: "0.4rem", fontSize: "0.95rem" }}>
                  <strong style={{ textTransform: "capitalize", color: COLORS.text }}>{i.domain}</strong> could see an improvement of <strong>{i.impact_percent.toFixed(1)}%</strong>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Disadvantages */}
        <div>
          <h3 style={{ margin: "0 0 0.75rem", fontSize: "1.05rem", color: COLORS.red }}>Disadvantages / Risks</h3>
          {negatives.length === 0 ? (
            <p style={{ color: COLORS.textLight, fontSize: "0.95rem", margin: 0 }}>No significant negative impacts predicted.</p>
          ) : (
            <ul style={{ margin: 0, paddingLeft: "1.2rem", color: COLORS.textMuted }}>
              {negatives.map((i) => (
                <li key={i.domain} style={{ marginBottom: "0.4rem", fontSize: "0.95rem" }}>
                  <strong style={{ textTransform: "capitalize", color: COLORS.text }}>{i.domain}</strong> could face a decline of <strong>{i.impact_percent.toFixed(1)}%</strong>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {neutral.length > 0 && (
        <p style={{ color: COLORS.textLight, fontSize: "0.9rem", margin: "0 0 1.5rem 0" }}>
          Minimal impact expected on: {neutral.map((i) => i.domain).join(", ")}.
        </p>
      )}

      {/* AI Explanation */}
      <div style={{ background: "#fafafa", border: `1px solid ${COLORS.surface}`, borderRadius: "8px", padding: "1.25rem" }}>
        <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", color: COLORS.text }}>AI Analysis Summary</h3>
        <p style={{ color: COLORS.textMuted, fontSize: "0.95rem", lineHeight: 1.6, margin: 0, whiteSpace: "pre-wrap" }}>
          {explanation}
        </p>
      </div>
    </div>
  );
}

/* ── Main Page ── */
export default function HomePage() {
  const [policyText, setPolicyText] = useState("Increase import tariffs on fuel by 10% to reduce trade deficit.");
  const [shockFactor, setShockFactor] = useState(0.2);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [scenario, setScenario] = useState<ScenarioResponse | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);

  const topRipple = useMemo(() => {
    if (!graph) return [];
    return Object.entries(graph.ripple_effects)
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .slice(0, 5);
  }, [graph]);

  async function runAnalysis() {
    setLoading(true);
    setError("");
    try {
      const [predictionResp, scenarioResp, graphResp] = await Promise.all([
        fetch(`${API_BASE}/prediction/impact`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ policy_text: policyText, context_overrides: {}, country: "India" }),
        }),
        fetch(`${API_BASE}/scenario/simulate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ policy_text: policyText, shock_factor: shockFactor, country: "India" }),
        }),
        fetch(`${API_BASE}/graph/dependencies`),
      ]);

      if (!predictionResp.ok || !scenarioResp.ok || !graphResp.ok) throw new Error("One or more backend requests failed.");

      setPrediction((await predictionResp.json()) as PredictionResponse);
      setScenario((await scenarioResp.json()) as ScenarioResponse);
      setGraph((await graphResp.json()) as GraphResponse);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ fontFamily: "Arial, sans-serif", padding: "1.5rem", background: COLORS.bg, minHeight: "100vh", color: COLORS.text }}>
      <h1 style={{ marginTop: 0, fontSize: "2rem", fontWeight: "bold" }}>Polaris Dashboard</h1>
      <p style={{ marginTop: "0.25rem", color: COLORS.textMuted }}>
        India-specific policy impact intelligence across markets, inflation, healthcare, trade, and commodities.
      </p>

      {/* Input Card */}
      <section style={{ ...cardStyle, marginBottom: "1.5rem" }}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Policy Input</h2>
        <p style={{ marginTop: 0, color: COLORS.textMuted, fontSize: "0.95rem" }}>
          Scope: <strong>India</strong> (all predictions and scenarios are computed for India).
        </p>
        <textarea
          value={policyText}
          onChange={(e) => setPolicyText(e.target.value)}
          rows={4}
          style={{ width: "100%", marginBottom: "0.75rem", padding: "0.6rem", border: "1px solid #ccc", borderRadius: "4px", fontSize: "1rem", fontFamily: "monospace", resize: "vertical" }}
        />
        <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
          <label style={{ fontSize: "0.95rem" }}>
            Shock factor:
            <input type="number" min={0} max={1} step={0.05} value={shockFactor} onChange={(e) => setShockFactor(Number(e.target.value))}
              style={{ marginLeft: "0.5rem", width: "90px", padding: "0.25rem 0.5rem", border: "1px solid #ccc", borderRadius: "4px" }}
            />
          </label>
          <button onClick={runAnalysis} disabled={loading || !policyText.trim()}
            style={{ padding: "0.5rem 1rem", cursor: loading ? "not-allowed" : "pointer", background: "#efefef", border: "1px solid #ccc", borderRadius: "4px", fontSize: "0.95rem" }}>
            {loading ? "Running..." : "Run Analysis"}
          </button>
          <code style={{ fontSize: "0.9rem", color: COLORS.textLight }}>{API_BASE}</code>
        </div>
        {error && <p style={{ color: COLORS.red, marginBottom: 0, marginTop: "0.5rem" }}>Error: {error}</p>}
      </section>

      {/* Results Grid */}
      <section style={{ display: "grid", gap: "1.5rem", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))" }}>
        
        {/* Impact Comparison */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Impact Comparison</h2>
          {!prediction ? (
            <p style={{ color: COLORS.textLight }}>Run analysis to view domain impact predictions.</p>
          ) : (
            <>
              <p style={{ margin: "0 0 1rem 0", color: COLORS.textMuted, fontSize: "0.95rem" }}>
                Predicted impact on: <strong>{prediction.country}</strong>
              </p>
              
              {/* List View with Confidence */}
              <div style={{ display: "grid", gap: "0.75rem", marginBottom: "1rem" }}>
                {prediction.impacts.map((imp) => (
                  <div key={imp.domain} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ textTransform: "capitalize", fontSize: "0.95rem" }}>{imp.domain}</strong>
                    <span style={{ fontSize: "0.9rem", color: COLORS.textMuted }}>Confidence: {(imp.confidence * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>

              {/* Graphical View */}
              <div style={{ borderTop: `1px solid ${COLORS.surface}`, paddingTop: "0.5rem" }}>
                <ImpactChart impacts={prediction.impacts} />
              </div>
            </>
          )}
        </div>

        {/* Scenario Visualization */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Scenario Visualization</h2>
          {!scenario ? (
            <p style={{ color: COLORS.textLight }}>Run analysis to generate baseline, shock, and policy-adjusted scenarios.</p>
          ) : (
            <>
              <p style={{ margin: "0 0 1rem 0", color: COLORS.textMuted, fontSize: "0.95rem" }}>
                Scenario context: <strong>{scenario.country}</strong>
              </p>
              <div style={{ display: "grid", gap: "1rem" }}>
                {scenario.scenarios.map((item) => (
                  <div key={item.domain} style={{ borderBottom: `1px solid ${COLORS.surface}`, paddingBottom: "0.75rem" }}>
                    <strong style={{ textTransform: "capitalize", display: "block", marginBottom: "0.25rem" }}>{item.domain}</strong>
                    <div style={{ fontSize: "0.9rem", color: COLORS.textMuted, lineHeight: 1.4 }}>
                      Baseline: {item.baseline.toFixed(2)}% | Shock: {item.shock.toFixed(2)}% | Policy-adjusted: {item.policy_adjusted.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Dependency Graph & Ripple Effects */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Dependency Graph & Ripple Effects</h2>
          {!graph ? (
            <p style={{ color: COLORS.textLight }}>Run analysis to see interdependency ripple signals.</p>
          ) : (
            <>
              <p style={{ margin: "0 0 1rem 0", fontSize: "0.95rem" }}>
                <strong>Edges:</strong> {graph.edges.length} | <strong>Nodes:</strong> {graph.nodes.length}
              </p>
              <div style={{ fontSize: "0.9rem", marginBottom: "1rem", color: COLORS.textMuted, lineHeight: 1.5 }}>
                {graph.edges.map((edge, idx) => (
                  <div key={`${edge.source}-${edge.target}-${idx}`}>
                    {edge.source} → {edge.target} (w={edge.weight})
                  </div>
                ))}
              </div>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.5rem" }}>Top Ripple Magnitudes</h3>
              <ul style={{ margin: "0 0 0 1.2rem", padding: 0, color: COLORS.textMuted, fontSize: "0.95rem", lineHeight: 1.5 }}>
                {topRipple.map(([node, value]) => (
                  <li key={node}>
                    {node}: {value.toFixed(4)}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      </section>

      {/* Final Verdict Section */}
      {prediction && scenario && (
        <VerdictSection impacts={prediction.impacts} explanation={scenario.explanation} />
      )}
      
    </main>
  );
}
