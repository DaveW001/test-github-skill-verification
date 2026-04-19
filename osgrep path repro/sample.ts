export function refreshAuthToken(token: string): string {
  return `${token}-refreshed`;
}

export function readFeatureFlag(flagName: string): boolean {
  return flagName === "osgrep_canary";
}

export function staleIndexSymbol(): string {
  return "stale-index-check";
}
