export type Community =
  | "Dubai Marina"
  | "Downtown Dubai"
  | "JVC"
  | "Business Bay"
  | "Palm Jumeirah"
  | "Dubai Hills"
  | "JBR"
  | "Arabian Ranches"
  | "DAMAC Hills"
  | "MBR City";

export type PropertyType = "Apartment" | "Villa" | "Townhouse";

export type EstimateRequest = {
  community: Community;
  propertyType: PropertyType;
  sizeSqft: number;
  floorLevel?: number;
};

export type EstimateResponse = {
  valueAed: number;
};

const USE_FAKE =
  (process.env.NEXT_PUBLIC_USE_FAKE_ESTIMATE ?? "true") === "true";

function fakeEstimateValueAed(req: EstimateRequest): number {
  const basePerSqft =
    req.propertyType === "Villa" ? 2200 : req.propertyType === "Townhouse" ? 1700 : 1400;

  const communityMultiplier =
    req.community === "Palm Jumeirah"
      ? 2.2
      : req.community === "Downtown Dubai"
        ? 1.8
        : req.community === "Dubai Marina"
          ? 1.6
          : req.community === "JBR"
            ? 1.55
            : req.community === "Dubai Hills"
              ? 1.45
              : req.community === "Business Bay"
                ? 1.35
                : req.community === "Arabian Ranches"
                  ? 1.3
                  : req.community === "DAMAC Hills"
                    ? 1.15
                    : req.community === "MBR City"
                      ? 1.25
                      : 1.0;

  const floorFactor =
    req.floorLevel && req.floorLevel > 0
      ? 1 + Math.min(req.floorLevel, 30) * 0.002
      : 1;

  const raw = req.sizeSqft * basePerSqft * communityMultiplier * floorFactor;
  return Math.max(250_000, Math.round(raw / 10_000) * 10_000);
}

export async function estimatePropertyValue(
  req: EstimateRequest,
): Promise<EstimateResponse> {
  if (USE_FAKE) {
    return { valueAed: fakeEstimateValueAed(req) };
  }

  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!baseUrl) {
    throw new Error(
      "Missing NEXT_PUBLIC_API_BASE_URL (needed when NEXT_PUBLIC_USE_FAKE_ESTIMATE=false).",
    );
  }

  const res = await fetch(`${baseUrl}/estimate`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    // body: JSON.stringify(req),
    //added from bilal data
    //
    body: JSON.stringify({
      community: req.community,
      property_type: req.propertyType,
      size_sqft: req.sizeSqft,
    }),
    //
  });
  //

  if (!res.ok) {
    throw new Error(`Estimate request failed (${res.status}).`);
  }

  // const data = (await res.json()) as Partial<EstimateResponse>;
  //
  const data = await res.json();

  return { valueAed: data.estimated_value_aed };
  //

  if (typeof data.valueAed !== "number" || !Number.isFinite(data.valueAed)) {
    throw new Error("Estimate response missing numeric valueAed.");
  }

  return { valueAed: data.valueAed };
}

