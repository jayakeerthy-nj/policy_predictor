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

const cardStyle: CSSProperties = {
  border: "1px solid #d9d9d9",
  borderRadius: "10px",
  padding: "1rem",
  background: "white",
};

function ImpactBar({ value }: { value: number }) {
  const abs = Math.min(100, Math.abs(value));
  const color = value > 0 ? "#2e7d32" : value < 0 ? "#c62828" : "#616161";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
      <div style={{ width: "180px", background: "#f0f0f0", borderRadius: "6px", height: "10px" }}>
        <div
          style={{
            width: `${abs}%`,
            height: "100%",
            borderRadius: "6px",
            background: color,
          }}
        />
      </div>
      <span style={{ fontSize: "0.9rem", minWidth: "64px" }}>{value.toFixed(2)}%</span>
    </div>
  );
}

export default function HomePage() {
  const [policyText, setPolicyText] = useState(
    "Increase import tariffs on fuel by 10% to reduce trade deficit."
  );
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
          body: JSON.stringify({
            policy_text: policyText,
            context_overrides: {},
            country: "India",
          }),
        }),
        fetch(`${API_BASE}/scenario/simulate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            policy_text: policyText,
            shock_factor: shockFactor,
            country: "India",
          }),
        }),
        fetch(`${API_BASE}/graph/dependencies`),
      ]);

      if (!predictionResp.ok || !scenarioResp.ok || !graphResp.ok) {
        throw new Error("One or more backend requests failed.");
      }

      const predictionData = (await predictionResp.json()) as PredictionResponse;
      const scenarioData = (await scenarioResp.json()) as ScenarioResponse;
      const graphData = (await graphResp.json()) as GraphResponse;

      setPrediction(predictionData);
      setScenario(scenarioData);
      setGraph(graphData);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unexpected error";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        fontFamily: "Arial, sans-serif",
        padding: "1.5rem",
        background: "#f7f8fa",
        minHeight: "100vh",
      }}
    >
      <h1 style={{ marginTop: 0 }}>Polaris Dashboard</h1>
      <p style={{ marginTop: "0.25rem", color: "#444" }}>
        India-specific policy impact intelligence across markets, inflation, healthcare, trade, and commodities.
      </p>

      <section style={{ ...cardStyle, marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Policy Input</h2>
        <p style={{ marginTop: 0, color: "#444" }}>
          Scope: <strong>India</strong> (all predictions and scenarios are computed for India).
        </p>
        <textarea
          value={policyText}
          onChange={(e) => setPolicyText(e.target.value)}
          rows={4}
          style={{ width: "100%", marginBottom: "0.75rem", padding: "0.6rem" }}
        />
        <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
          <label>
            Shock factor:
            <input
              type="number"
              min={0}
              max={1}
              step={0.05}
              value={shockFactor}
              onChange={(e) => setShockFactor(Number(e.target.value))}
              style={{ marginLeft: "0.5rem", width: "90px" }}
            />
          </label>
          <button
            onClick={runAnalysis}
            disabled={loading || !policyText.trim()}
            style={{ padding: "0.5rem 1rem", cursor: "pointer" }}
          >
            {loading ? "Running..." : "Run Analysis"}
          </button>
          <code>{API_BASE}</code>
        </div>
        {error ? <p style={{ color: "#b00020", marginBottom: 0 }}>Error: {error}</p> : null}
      </section>

      <section
        style={{
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
        }}
      >
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Impact Comparison</h2>
          {!prediction ? (
            <p style={{ color: "#666" }}>Run analysis to view domain impact predictions.</p>
          ) : (
            <div style={{ display: "grid", gap: "0.6rem" }}>
              <p style={{ margin: 0, color: "#444" }}>
                Predicted impact on: <strong>{prediction.country}</strong>
              </p>
              {prediction.impacts.map((impact) => (
                <div key={impact.domain}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <strong style={{ textTransform: "capitalize" }}>{impact.domain}</strong>
                    <span>Confidence: {(impact.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <ImpactBar value={impact.impact_percent} />
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Scenario Visualization</h2>
          {!scenario ? (
            <p style={{ color: "#666" }}>Run analysis to generate baseline, shock, and policy-adjusted scenarios.</p>
          ) : (
            <>
              <p style={{ marginTop: 0, color: "#444" }}>
                Scenario context: <strong>{scenario.country}</strong>
              </p>
              <div style={{ display: "grid", gap: "0.8rem" }}>
                {scenario.scenarios.map((item) => (
                  <div key={item.domain} style={{ borderBottom: "1px solid #eee", paddingBottom: "0.5rem" }}>
                    <strong style={{ textTransform: "capitalize" }}>{item.domain}</strong>
                    <div style={{ fontSize: "0.9rem" }}>
                      Baseline: {item.baseline.toFixed(2)}% | Shock: {item.shock.toFixed(2)}% | Policy-adjusted:{" "}
                      {item.policy_adjusted.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
              <p style={{ marginTop: "0.75rem", color: "#333", whiteSpace: "pre-wrap" }}>
                {scenario.explanation}
              </p>
            </>
          )}
        </div>

        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, fontSize: "1.1rem" }}>Dependency Graph & Ripple Effects</h2>
          {!graph ? (
            <p style={{ color: "#666" }}>Run analysis to see interdependency ripple signals.</p>
          ) : (
            <>
              <p style={{ marginTop: 0 }}>
                <strong>Edges:</strong> {graph.edges.length} | <strong>Nodes:</strong> {graph.nodes.length}
              </p>
              <div style={{ fontSize: "0.92rem", marginBottom: "0.6rem" }}>
                {graph.edges.map((edge, idx) => (
                  <div key={`${edge.source}-${edge.target}-${idx}`}>
                    {edge.source} → {edge.target} (w={edge.weight})
                  </div>
                ))}
              </div>
              <h3 style={{ fontSize: "1rem", marginBottom: "0.4rem" }}>Top Ripple Magnitudes</h3>
              <ul style={{ marginTop: 0 }}>
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
    </main>
  );
}

