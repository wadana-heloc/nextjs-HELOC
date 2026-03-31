"use client";

import { useMemo, useState } from "react";
import type { Community, PropertyType } from "@/lib/api/estimate";
import { estimatePropertyValue } from "@/lib/api/estimate";
import { formatAed } from "@/lib/format/money";
import { FieldLabel } from "@/components/ui/FieldLabel";
import { HelpText } from "@/components/ui/HelpText";

const COMMUNITIES: Community[] = [
  "Dubai Marina",
  "Downtown Dubai",
  "JVC",
  "Business Bay",
  "Palm Jumeirah",
  "Dubai Hills",
  "JBR",
  "Arabian Ranches",
  "DAMAC Hills",
  "MBR City",
];

const PROPERTY_TYPES: PropertyType[] = ["Apartment", "Villa", "Townhouse"];

const MAX_EQUITY_PERCENT = 0.6;

export function EquityCalculator() {
  const [community, setCommunity] = useState<Community>("Dubai Marina");
  const [propertyType, setPropertyType] = useState<PropertyType>("Apartment");
  const [floorLevel, setFloorLevel] = useState<string>("");
  const [sizeSqft, setSizeSqft] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [valueAed, setValueAed] = useState<number | null>(null);

  const parsedFloorLevel = useMemo(() => {
    const normalized = floorLevel.replace(/,/g, "").trim();
    const n = normalized === "" ? NaN : Number(normalized);
    return Number.isFinite(n) ? n : NaN;
  }, [floorLevel]);

  const parsedSize = useMemo(() => {
    // Allow users to paste values like "1,250" by stripping commas.
    const normalized = sizeSqft.replace(/,/g, "").trim();
    const n = normalized === "" ? NaN : Number(normalized);
    return Number.isFinite(n) ? n : NaN;
  }, [sizeSqft]);

  const floorTrimmed = floorLevel.trim();
  const floorValid =
    floorTrimmed === "" || (Number.isFinite(parsedFloorLevel) && parsedFloorLevel >= 0);

  const canSubmit =
    !isSubmitting && Number.isFinite(parsedSize) && parsedSize > 0 && floorValid;

  const maxEquityAed =
    valueAed === null ? null : Math.floor(valueAed * MAX_EQUITY_PERCENT);

  const sizeTrimmed = sizeSqft.trim();
  const sizeHelp =
    sizeTrimmed === ""
      ? "We use this to estimate value per sqft."
      : !Number.isFinite(parsedSize) || parsedSize <= 0
        ? "Please enter a positive number for size."
        : "Looks good. Ready to estimate.";

  async function onEstimate() {
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await estimatePropertyValue({
        community,
        propertyType,
        sizeSqft: parsedSize,
        floorLevel: floorTrimmed === "" ? undefined : parsedFloorLevel,
      });
      setValueAed(res.valueAed);
    } catch (e) {
      setValueAed(null);
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Equity Calculator
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Get an estimate of your property value and how much equity you could
            access.
          </p>
        </header>

        <div className="space-y-5">
          <div>
            <FieldLabel htmlFor="community">Community</FieldLabel>
            <select
              id="community"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={community}
              onChange={(e) => setCommunity(e.target.value as Community)}
            >
              {COMMUNITIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div>
            <FieldLabel htmlFor="propertyType">Property type</FieldLabel>
            <select
              id="propertyType"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={propertyType}
              onChange={(e) => setPropertyType(e.target.value as PropertyType)}
            >
              {PROPERTY_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <FieldLabel htmlFor="floorLevel">Floor level</FieldLabel>
            <input
              id="floorLevel"
              inputMode="numeric"
              type="number"
              min={0}
              step={1}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={floorLevel}
              onChange={(e) => setFloorLevel(e.target.value)}
              placeholder="Optional"
            />
            <HelpText>
              {floorTrimmed === ""
                ? "Optional; enter the level if known."
                : !floorValid
                ? "Please enter a non-negative number for floor level."
                : "Looks good."
              }
            </HelpText>
          </div>

          <div>
            <FieldLabel htmlFor="sizeSqft">Size (sqft)</FieldLabel>
            <input
              id="sizeSqft"
              inputMode="numeric"
              type="number"
              min={0}
              step={1}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={sizeSqft}
              onChange={(e) => setSizeSqft(e.target.value)}
              placeholder="e.g., 1250 (no commas)"
            />
            <HelpText>{sizeHelp}</HelpText>
          </div>

          <button
            type="button"
            className="mt-2 w-full rounded-lg bg-slate-900 py-2.5 text-white font-medium hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-slate-900"
            disabled={!canSubmit}
            onClick={onEstimate}
          >
            {isSubmitting ? "Estimating..." : "Estimate My Equity"}
          </button>

          {error ? (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
              {error}
            </div>
          ) : null}

          {valueAed !== null && maxEquityAed !== null ? (
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-700">
                Your property is worth approximately{" "}
                <span className="font-semibold text-slate-900">
                  {formatAed(valueAed)}
                </span>
                .
              </p>
              <p className="mt-2 text-sm text-slate-700">
                You could access up to{" "}
                <span className="font-semibold text-slate-900">
                  {formatAed(maxEquityAed)}
                </span>{" "}
                in equity.
              </p>
              <p className="mt-3 text-xs text-slate-600">
                Estimates shown are not a guarantee.
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

