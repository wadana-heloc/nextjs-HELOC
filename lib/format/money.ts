const AED_FORMATTER = new Intl.NumberFormat("en-AE", {
  style: "currency",
  currency: "AED",
  maximumFractionDigits: 0,
});

export function formatAed(amount: number) {
  return AED_FORMATTER.format(amount);
}

