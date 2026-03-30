const PERCENT_FORMATTER = new Intl.NumberFormat("en", {
  style: "percent",
  maximumFractionDigits: 0,
});

export function formatPercent(value: number) {
  return PERCENT_FORMATTER.format(value);
}

