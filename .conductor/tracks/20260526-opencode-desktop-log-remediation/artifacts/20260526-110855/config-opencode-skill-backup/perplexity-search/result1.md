
================================================================================
ANSWER
================================================================================
To reset page numbering to 1 on a specific section or element in Vivliostyle (so `@bottom-center { content: counter(page); }` displays 1, ignoring a cover page), apply `counter-reset: page 0` to the element where the reset should occur, such as via a class selector or `:first` pseudo-class on a page break.[1]

This works because Vivliostyle automatically increments the `page` counter at the start of each page; resetting to 0 ensures the next page shows 1.[1] For example, with a cover page followed by content:

```css
/* Cover page (unnumbered) */
@page :first {
  @bottom-center { content: none; } /* Or empty */
}

/* Reset on the first content page/section */
.content-start {
  break-before: page; /* Force new page if needed */
  counter-reset: page 0;
}

@page {
  @bottom-center {
    content: counter(page);
  }
}
```

Apply the `.content-start` class to your HTML element (e.g., `<div class="content-start">Chapter 1...</div>`), which starts after the cover.[1] Note that `counter-reset: page;` (without `0`) may yield 2 due to auto-increment—always specify `0` for a true 1-start.[1]

For multi-document books (web publications), use `@page :nth(1) { counter-reset: page; }` on the target document's first page instead.[1][6] API options like `startPage: 1` in `SingleDocumentOptions` can also set the first page number directly (equivalent to `counter-reset: page 0`).[2]

Limitations: Resets on elements may not work perfectly in web publications due to known issues; test with `renderAllPages=true` for accurate pagination.[1][4][6]
================================================================================
