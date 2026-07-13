# Motion Scaffold

Default motion should be purposeful, not noisy.

## Page Load Stagger (CSS)

```css
@keyframes rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.reveal {
  opacity: 0;
  animation: rise 700ms cubic-bezier(.2,.8,.2,1) forwards;
}

.reveal[data-delay="1"] { animation-delay: 80ms; }
.reveal[data-delay="2"] { animation-delay: 160ms; }
.reveal[data-delay="3"] { animation-delay: 240ms; }
.reveal[data-delay="4"] { animation-delay: 320ms; }
```

Usage:

```html
<h1 class="reveal" data-delay="1">Headline</h1>
<p class="reveal" data-delay="2">Subhead</p>
<div class="reveal" data-delay="3">Cards</div>
```

## Hover Motion (Subtle)

- One pattern per surface: small lift + shadow change.
- Avoid stacking multiple transforms.

## Reduced Motion

Always support `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```
