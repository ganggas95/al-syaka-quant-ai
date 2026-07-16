"use client";

import { MarketStatusBar } from "@/components/charts/market-status-bar";
import { MarketStructureChart } from "@/components/charts/market-structure-chart";
import { ScoreBreakdown } from "@/components/charts/score-breakdown";
import { SignalCandlestick } from "@/components/charts/signal-candlestick";
import { AiMarketThesis } from "@/components/signal/ai-market-thesis";
import { ConsensusMultitf } from "@/components/signal/consensus-multitf";
import {
    EmptyState,
    ErrorState,
    InitialLoadingState,
    RefreshIndicator,
} from "@/components/signal/loading-states";
import { ProbabilityVisualization } from "@/components/signal/probability-visualization";
import { RiskSummary } from "@/components/signal/risk-summary";
import { SessionInfo } from "@/components/signal/session-info";
import { ShapExplainability } from "@/components/signal/shap-explainability";
import { SignalHistory } from "@/components/signal/signal-history";
import { SignalTimeline } from "@/components/signal/signal-timeline";
import { useAutoSignal } from "@/hooks/use-auto-signal";
import {
    Activity,
    BrainCircuit,
    Shield,
    Target,
    TrendingUp,
} from "lucide-react";
import { useState } from "react";

const SYMBOLS = ["XAUUSD", "EURUSD", "BTCUSD", "US30"];
const TIMEFRAMES = ["H1", "H4", "D1"];

export default function SignalsPage() {
  // ── State ──────────────────────────────────────────────────────────────
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("H1");
  const [includeAI, setIncludeAI] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<
    string | undefined
  >();

  // ── Auto signal hook ───────────────────────────────────────────────────
  const {
    result,
    candleData,
    signalHistory,
    loading,
    isRefreshing,
    error,
    retry,
  } = useAutoSignal(symbol, timeframe, includeAI);

  // ── Loading state (first load) ─────────────────────────────────────────
  if (loading && !result) {
    return <InitialLoadingState />;
  }

  // ── Error state (no cached data) ───────────────────────────────────────
  if (error && !result) {
    return (
      <div className="space-y-6 pb-10">
        <HeaderControls
          symbol={symbol}
          timeframe={timeframe}
          includeAI={includeAI}
          onSymbolChange={setSymbol}
          onTimeframeChange={setTimeframe}
          onIncludeAIChange={setIncludeAI}
        />
        <ErrorState message={error} onRetry={retry} />
      </div>
    );
  }

  // ── Empty state (no result yet) ────────────────────────────────────────
  if (!result) {
    return (
      <div className="space-y-6 pb-10">
        <HeaderControls
          symbol={symbol}
          timeframe={timeframe}
          includeAI={includeAI}
          onSymbolChange={setSymbol}
          onTimeframeChange={setTimeframe}
          onIncludeAIChange={setIncludeAI}
        />
        <EmptyState />
      </div>
    );
  }

  // ── Main dashboard ─────────────────────────────────────────────────────
  return (
    <div className="space-y-6 pb-10">
      {/* ── Header Controls ─────────────────────────────────────────── */}
      <HeaderControls
        symbol={symbol}
        timeframe={timeframe}
        includeAI={includeAI}
        onSymbolChange={setSymbol}
        onTimeframeChange={setTimeframe}
        onIncludeAIChange={setIncludeAI}
        isRefreshing={isRefreshing}
      />

      {/* ── Signal Status Banner ────────────────────────────────────── */}
      <SignalBanner result={result} />

      {/* ── Parameters Row (Entry, SL, TP, RR) ──────────────────────── */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <ParamCard
          icon={<Target className="h-3 w-3" />}
          label="Entry"
          value={result.entry_price?.toFixed(5)}
        />
        <ParamCard
          icon={<Shield className="h-3 w-3 text-red-500" />}
          label="Stop Loss"
          value={result.stop_loss?.toFixed(5)}
          valueClassName="text-red-500"
        />
        <ParamCard
          icon={<TrendingUp className="h-3 w-3 text-green-500" />}
          label="Take Profit"
          value={result.take_profit?.toFixed(5)}
          valueClassName="text-green-500"
        />
        <ParamCard
          icon={<Activity className="h-3 w-3" />}
          label="Risk/Reward"
          value={
            result.risk_reward != null
              ? `1:${result.risk_reward.toFixed(1)}`
              : "—"
          }
        />
      </div>

      {/* ── AI Market Thesis ────────────────────────────────────────── */}
      <AiMarketThesis
        reasons={result.reasons}
        explanationReason={result.explanation_reason}
        marketRegime={result.market_regime}
        regimeReason={result.regime_reason}
        macroBias={result.macro_bias}
        macroReason={result.macro_reason}
      />

      {/* ── Row: Consensus MTF + Probability + Composite Score ──────── */}
      <div className="grid gap-6 lg:grid-cols-3">
        <ConsensusMultitf
          h1Signal={result.h1_signal}
          h4Signal={result.h4_signal}
          d1Signal={result.d1_signal}
        />
        <ProbabilityVisualization
          confidence={result.confidence}
          confidenceLabel={result.confidence_label}
          decisionConfidence={result.decision_confidence}
        />
        <ScoreBreakdown
          compositeScore={result.composite_score || 0}
          breakdown={
            result.confidence_breakdown || {
              market_structure: 0,
              momentum: 0,
              trend: 0,
              volatility: 0,
              ai_prediction: 0,
            }
          }
        />
      </div>

      {/* ── Row: Price Chart (full width) ───────────────────────────── */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="mb-4 text-sm font-medium text-muted-foreground">
          Price Chart ({symbol} &middot; {timeframe})
        </h3>
        <SignalCandlestick
          data={candleData}
          entryPrice={result.entry_price}
          stopLoss={result.stop_loss}
          takeProfit={result.take_profit}
          signal={result.signal}
          height={480}
        />
      </div>

      {/* ── Row: Market Structure + SHAP + Risk Summary ─────────────── */}
      <div className="grid gap-6 lg:grid-cols-3">
        <MarketStructureChart
          data={result.market_structure || defaultMarketStructure}
        />
        <ShapExplainability
          featureContributions={result.feature_contributions}
          shapSummary={result.shap_summary}
          shapReasons={result.shap_reasons}
        />
        <RiskSummary
          entryPrice={result.entry_price}
          stopLoss={result.stop_loss}
          takeProfit={result.take_profit}
          riskReward={result.risk_reward}
          riskLevel={result.risk_level}
          lotSize={result.lot_size}
          positionMultiplier={result.position_multiplier}
          tradeQuality={result.trade_quality}
        />
      </div>

      {/* ── Row: Signal History + Timeline ──────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SignalHistory
          entries={signalHistory}
          currentId={selectedHistoryId || result.signal_id}
          onSelect={setSelectedHistoryId}
        />
        <SignalTimeline
          entries={signalHistory}
          currentId={selectedHistoryId || result.signal_id}
          onSelect={setSelectedHistoryId}
        />
      </div>

      {/* ── Footer: Market Status Bar + Session Info ────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">
        <MarketStatusBar
          regime={result.market_regime}
          volatility={result.market_structure?.trend ? undefined : undefined}
          volume={undefined}
          liquidity={undefined}
          newsImpact={undefined}
          risk={result.risk_level}
          session={undefined}
        />
        <SessionInfo session={undefined} macroEvents={result.macro_events} />
      </div>
    </div>
  );
}

// ─── Header Controls Sub-component ──────────────────────────────────────────

interface HeaderControlsProps {
  symbol: string;
  timeframe: string;
  includeAI: boolean;
  onSymbolChange: (s: string) => void;
  onTimeframeChange: (t: string) => void;
  onIncludeAIChange: (v: boolean) => void;
  isRefreshing?: boolean;
}

function HeaderControls({
  symbol,
  timeframe,
  includeAI,
  onSymbolChange,
  onTimeframeChange,
  onIncludeAIChange,
  isRefreshing,
}: HeaderControlsProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-white/5 pb-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Live Signal Workspace
          </h1>
          <p className="text-sm text-muted-foreground">
            AI + Statistics + Market Structure &middot; Multi-Timeframe
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isRefreshing && <RefreshIndicator />}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4 rounded-xl border bg-card/50 p-4">
        {/* Symbol */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Symbol
          </label>
          <select
            value={symbol}
            onChange={(e) => onSymbolChange(e.target.value)}
            className="rounded-lg border bg-background px-3 py-2 text-sm font-bold"
          >
            {SYMBOLS.map((sym) => (
              <option key={sym} value={sym}>
                {sym}
              </option>
            ))}
          </select>
        </div>

        {/* Timeframe */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Timeframe
          </label>
          <div className="flex gap-1">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => onTimeframeChange(tf)}
                className={`rounded-lg px-4 py-2 text-xs font-bold transition-all ${
                  timeframe === tf
                    ? "bg-green-500 text-black"
                    : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* AI toggle */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[10px] uppercase tracking-wider text-muted-foreground">
            Features
          </label>
          <label className="flex h-9 cursor-pointer items-center gap-2 rounded-lg border bg-background px-3 text-xs font-bold transition-colors hover:bg-secondary/50">
            <input
              type="checkbox"
              checked={includeAI}
              onChange={(e) => onIncludeAIChange(e.target.checked)}
              className="accent-green-500"
            />
            <BrainCircuit className="h-4 w-4 text-blue-500" /> AI + SHAP
          </label>
        </div>

        {/* Spacer */}
        <div className="flex flex-1 items-end justify-end gap-2">
          {/* ExportSignal will be connected when result is available */}
          <span className="text-[10px] text-muted-foreground">
            Auto-generating on change...
          </span>
        </div>
      </div>
    </div>
  );
}

// ─── Signal Banner Sub-component ────────────────────────────────────────────

function SignalBanner({ result }: { result: any }) {
  const isBuy = result.signal === "BUY" || result.signal === "BULLISH";
  const isSell = result.signal === "SELL" || result.signal === "BEARISH";
  const signalColor = isBuy
    ? "text-green-500"
    : isSell
      ? "text-red-500"
      : "text-amber-500";
  const borderColor = isBuy
    ? "border-green-500/20"
    : isSell
      ? "border-red-500/20"
      : "border-amber-500/20";

  return (
    <div
      className={`flex flex-wrap items-center justify-between rounded-xl border ${borderColor} bg-card p-6`}
    >
      <div className="flex items-center gap-6">
        <span className={`text-5xl font-black ${signalColor}`}>
          {result.signal}
        </span>
        <div className="space-y-2">
          <div className="flex gap-2">
            <span className="rounded-full bg-secondary px-3 py-1 text-[10px] font-bold text-muted-foreground">
              {result.confidence?.toFixed(0)}% Confidence
            </span>
            {result.composite_score != null && (
              <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[10px] font-bold text-blue-500">
                {result.composite_score.toFixed(1)}% Composite
              </span>
            )}
          </div>
          <div className="flex gap-2">
            {result.risk_level && (
              <span className="rounded-full bg-green-500/10 px-3 py-1 text-[10px] font-bold text-green-500">
                {result.risk_level} Risk
              </span>
            )}
            {result.trade_quality && (
              <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[10px] font-bold text-blue-500">
                {result.trade_quality}
              </span>
            )}
          </div>
          <p className="text-[10px] text-muted-foreground uppercase tracking-widest">
            {result.symbol} &middot; {result.timeframe || ""} &middot; ID:{" "}
            {result.signal_id}
          </p>
        </div>
      </div>

      {/* Multi-TF quick view */}
      <div className="flex items-center gap-4">
        {[
          { tf: "H1", signal: result.h1_signal },
          { tf: "H4", signal: result.h4_signal },
          { tf: "D1", signal: result.d1_signal },
        ].map(({ tf, signal: sig }) => {
          const col =
            sig === "BUY" || sig === "BULLISH"
              ? "text-green-500"
              : sig === "SELL" || sig === "BEARISH"
                ? "text-red-500"
                : "text-muted-foreground";
          return (
            <div
              key={tf}
              className="flex flex-col items-center rounded-lg border bg-card p-2 w-16"
            >
              <span className="text-[9px] text-muted-foreground uppercase">
                {tf}
              </span>
              <span className={`text-[10px] font-bold uppercase ${col}`}>
                {sig || "—"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Param Card Sub-component ───────────────────────────────────────────────

function ParamCard({
  icon,
  label,
  value,
  valueClassName = "text-foreground",
}: {
  icon: React.ReactNode;
  label: string;
  value?: string | number;
  valueClassName?: string;
}) {
  return (
    <div className="rounded-xl border bg-card p-4">
      <div className="flex items-center gap-2 text-[10px] uppercase text-muted-foreground">
        {icon}
        {label}
      </div>
      <p className={`mt-1 font-mono text-lg font-bold ${valueClassName}`}>
        {value ?? "—"}
      </p>
    </div>
  );
}

// ─── Helper ─────────────────────────────────────────────────────────────────

const defaultMarketStructure = {
  trend: "NEUTRAL",
  swing_highs: 0,
  swing_lows: 0,
  break_of_structure: 0,
  change_of_character: 0,
  fair_value_gaps: 0,
  liquidity_sweeps: 0,
};
