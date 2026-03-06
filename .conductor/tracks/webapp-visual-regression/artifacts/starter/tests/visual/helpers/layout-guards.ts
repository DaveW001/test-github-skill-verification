import { Page } from "@playwright/test";

export type GuardSeverity = "blocker" | "warn" | "info";

export type GuardFinding = {
  kind: "sticky-overlap" | "off-page" | "spacing-outlier";
  severity: GuardSeverity;
  selector: string;
  message: string;
};

type LayoutGuardOptions = {
  stickySelector: string;
  criticalSelectors: string[];
  offPageSelectors: string[];
  spacingGroupSelectors: string[];
};

export async function runLayoutGuards(page: Page, options: LayoutGuardOptions): Promise<GuardFinding[]> {
  return page.evaluate((opts) => {
    type Finding = GuardFinding;

    const findings: Finding[] = [];
    const vw = window.innerWidth;
    const vh = window.innerHeight;

    const visibleRect = (el: Element) => {
      const rect = el.getBoundingClientRect();
      if (rect.width < 2 || rect.height < 2) {
        return null;
      }
      const style = window.getComputedStyle(el);
      if (style.visibility === "hidden" || style.display === "none" || Number(style.opacity) === 0) {
        return null;
      }
      return rect;
    };

    const median = (values: number[]) => {
      if (!values.length) {
        return 0;
      }
      const sorted = [...values].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    };

    const stickyRoot = document.querySelector(opts.stickySelector);
    let stickyBottom = 0;
    if (stickyRoot) {
      const stickyRect = visibleRect(stickyRoot);
      if (stickyRect && stickyRect.top <= 1) {
        stickyBottom = Math.max(stickyBottom, stickyRect.bottom);
      }
    }

    if (stickyBottom > 0) {
      for (const selector of opts.criticalSelectors) {
        const el = document.querySelector(selector);
        if (!el) {
          continue;
        }
        const rect = visibleRect(el);
        if (!rect) {
          continue;
        }
        if (rect.bottom > 0 && rect.top < vh && rect.top + 2 < stickyBottom) {
          findings.push({
            kind: "sticky-overlap",
            severity: "blocker",
            selector,
            message: `Potential sticky overlap: ${selector} top=${Math.round(rect.top)} under sticky bottom=${Math.round(stickyBottom)}`,
          });
        }
      }
    }

    for (const selector of opts.offPageSelectors) {
      const nodes = Array.from(document.querySelectorAll(selector)).slice(0, 30);
      for (const node of nodes) {
        const rect = visibleRect(node);
        if (!rect) {
          continue;
        }
        if (rect.bottom < 0 || rect.top > vh) {
          continue;
        }
        const leftOverflow = rect.left < -4;
        const rightOverflow = rect.right > vw + 4;
        if (leftOverflow || rightOverflow) {
          findings.push({
            kind: "off-page",
            severity: "warn",
            selector,
            message: `Element escapes viewport: ${selector} rect=(${Math.round(rect.left)},${Math.round(rect.top)},${Math.round(rect.right)},${Math.round(rect.bottom)}) viewport=${vw}x${vh}`,
          });
          break;
        }
      }
    }

    for (const selector of opts.spacingGroupSelectors) {
      const nodes = Array.from(document.querySelectorAll(selector));
      if (nodes.length < 4) {
        continue;
      }
      const items = nodes
        .map((node) => {
          const rect = visibleRect(node);
          if (!rect) {
            return null;
          }
          return {
            top: rect.top,
            bottom: rect.bottom,
            left: rect.left,
          };
        })
        .filter((item): item is { top: number; bottom: number; left: number } => !!item)
        .sort((a, b) => a.top - b.top);

      if (items.length < 4) {
        continue;
      }

      const columnSeed = items[0].left;
      const columnItems = items.filter((item) => Math.abs(item.left - columnSeed) <= 24);
      if (columnItems.length < 4) {
        continue;
      }

      const gaps: number[] = [];
      for (let i = 0; i < columnItems.length - 1; i += 1) {
        gaps.push(columnItems[i + 1].top - columnItems[i].bottom);
      }

      if (gaps.length < 3) {
        continue;
      }

      const baselineGap = median(gaps);
      if (baselineGap <= 0) {
        continue;
      }

      for (const gap of gaps) {
        const tooLarge = gap - baselineGap > 24 && gap > baselineGap * 2.2;
        const tooSmall = baselineGap - gap > 24 && gap < baselineGap * 0.3;
        if (tooLarge || tooSmall) {
          findings.push({
            kind: "spacing-outlier",
            severity: "info",
            selector,
            message: `Spacing outlier in ${selector}: gap=${Math.round(gap)} baseline=${Math.round(baselineGap)}`,
          });
          break;
        }
      }
    }

    return findings;
  }, options);
}
