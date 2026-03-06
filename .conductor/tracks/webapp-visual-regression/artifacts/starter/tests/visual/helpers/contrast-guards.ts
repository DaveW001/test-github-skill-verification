import { Page } from "@playwright/test";

export type ContrastFinding = {
  severity: "warn" | "info";
  selector: string;
  message: string;
};

type ContrastTarget = {
  selector: string;
  minRatio: number;
  label: string;
};

type RGB = { r: number; g: number; b: number };

function parseRgb(input: string): RGB | null {
  const match = input.match(/rgba?\(([^)]+)\)/i);
  if (!match) {
    return null;
  }
  const parts = match[1].split(",").map((p) => Number.parseFloat(p.trim()));
  if (parts.length < 3 || parts.slice(0, 3).some((n) => Number.isNaN(n))) {
    return null;
  }
  return { r: parts[0], g: parts[1], b: parts[2] };
}

function luminance({ r, g, b }: RGB): number {
  const toLinear = (v: number) => {
    const n = v / 255;
    return n <= 0.03928 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
}

function ratio(fg: RGB, bg: RGB): number {
  const l1 = luminance(fg);
  const l2 = luminance(bg);
  const light = Math.max(l1, l2);
  const dark = Math.min(l1, l2);
  return (light + 0.05) / (dark + 0.05);
}

export async function runContrastGuards(page: Page, targets: ContrastTarget[]): Promise<ContrastFinding[]> {
  const findings: ContrastFinding[] = [];

  for (const target of targets) {
    const node = page.locator(target.selector).first();
    if ((await node.count()) === 0) {
      findings.push({
        severity: "info",
        selector: target.selector,
        message: `Contrast check skipped for ${target.label}: selector not found`,
      });
      continue;
    }

    const result = await node.evaluate((el) => {
      const style = window.getComputedStyle(el);
      const color = style.color;

      let bg = style.backgroundColor;
      let current: Element | null = el;
      while (current && bg && /rgba?\([^)]*,\s*0\s*\)/.test(bg)) {
        current = current.parentElement;
        if (current) {
          bg = window.getComputedStyle(current).backgroundColor;
        }
      }

      return { fg: color, bg: bg || "rgb(255,255,255)" };
    });

    const fg = parseRgb(result.fg);
    const bg = parseRgb(result.bg);
    if (!fg || !bg) {
      findings.push({
        severity: "info",
        selector: target.selector,
        message: `Contrast check skipped for ${target.label}: unsupported color format fg='${result.fg}' bg='${result.bg}'`,
      });
      continue;
    }

    const cr = ratio(fg, bg);
    if (cr < target.minRatio) {
      findings.push({
        severity: "warn",
        selector: target.selector,
        message: `Low contrast for ${target.label}: ratio=${cr.toFixed(2)} minimum=${target.minRatio.toFixed(2)}`,
      });
    }
  }

  return findings;
}
