
================================================================================
ANSWER
================================================================================
To create a cover page with a background color that bleeds fully to all page edges in Vivliostyle, use a **named page rule with `margin: 0` and `bleed` property**[4][6].

Here's the approach:

```css
@page cover {
  margin: 0;
  bleed: 6mm;
}

.cover {
  page: cover;
  background-color: your-color;
}
```

**Key steps:**

1. **Define a named page rule** (`@page cover`) that sets `margin: 0` to remove default page margins[4]
2. **Set the `bleed` property** within the `@page` rule to specify how far content extends beyond the page boundary[6]. The bleed value (e.g., `6mm`) determines the area that will be printed beyond the crop marks[2]
3. **Apply the named page** to your cover element using the `page: cover` property[4]
4. **Add your background color** to the cover element or the `@page` rule itself

The `bleed` property is supported in Vivliostyle and works within `@page` rules[6]. By combining `margin: 0` with the bleed setting, your background color will extend fully to the page edges without being constrained by default margins[4].

If you're using Vivliostyle CLI, you can also specify bleed via command line: `vivliostyle build example.html -m --bleed 6mm`[2]
================================================================================
