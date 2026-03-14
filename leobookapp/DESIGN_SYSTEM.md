# LeoBook Design System v2.0

> **Dart SDK**: 3.8.1 · **Flutter**: ≥3.22 · **Font**: Inter (GoogleFonts) · Updated: 2026-03-14

---

## 1. Color Palette

All tokens live in `lib/core/constants/app_colors.dart`.

| Token | Hex | Role | WCAG note |
|---|---|---|---|
| `primary` | `#6C63FF` | Electric violet — CTAs, focus rings | 7.1:1 on `neutral900` (AAA) |
| `primaryLight` | `#9D97FF` | Hover / tint states | |
| `primaryDark` | `#4B44CC` | Pressed / deep accent | |
| `secondary` | `#00D4AA` | Emerald teal — success indicators | 6.8:1 on `neutral900` |
| `secondaryLight` | `#4DFFDB` | Secondary tint | |
| `secondaryDark` | `#009E7E` | Secondary deep | |
| `success` | `#22C55E` | Correct predictions | 4.9:1 on `neutral900` |
| `warning` | `#F59E0B` | Caution states | 3.1:1 on `neutral900` (large text) |
| `error` / `liveRed` | `#EF4444` | Error / live match | 4.6:1 on `neutral900` |
| `errorLight` | `#FEE2E2` | Error container | |
| `neutral50–900` | scale | Background / surface / text greys | |
| `glass` | `#1A2332` (60%) | Frosted card fill | |
| `glassBorder` | `#FFFFFF` (8%) | Card border | |
| `textPrimary` | `#F1F5F9` | Body text on dark | 15:1 on `neutral900` (AAA) |
| `textSecondary` | `#94A3B8` | Secondary / hint | 5.9:1 on `neutral900` (AA) |
| `textDisabled` | `#475569` | Disabled | |
| `textInverse` | `#0F172A` | Text on light surfaces | |
| `divider` | `#1E293B` | Dividers | |
| `surfaceCard` | `#111827` | Card background | |
| `surfaceElevated` | `#1E293B` | Modal / elevated surface | |

---

## 2. Typography Scale

All tokens in `lib/core/theme/leo_typography.dart`. Font: **Inter** via `GoogleFonts.inter()`.

| Style | Size (sp) | Weight | Line Height | Use case |
|---|---|---|---|---|
| `displayLarge` | 57 | 400 | 1.12 | Hero numbers |
| `displayMedium` | 45 | 400 | 1.16 | Section hero |
| `displaySmall` | 36 | 400 | 1.22 | Feature headings |
| `headlineLarge` | 32 | 700 | 1.25 | Page titles |
| `headlineMedium` | 28 | 700 | 1.29 | Section titles |
| `headlineSmall` | 24 | 700 | 1.33 | Card headlines |
| `titleLarge` | 22 | 700 | 1.27 | AppBar title, dialog title |
| `titleMedium` | 16 | 600 | 1.50 | List tile title |
| `titleSmall` | 14 | 600 | 1.43 | Subtitle |
| `bodyLarge` | 16 | 400 | 1.50 | Primary body text |
| `bodyMedium` | 14 | 400 | 1.43 | Standard body |
| `bodySmall` | 12 | 400 | 1.33 | Caption, helper text |
| `labelLarge` | 14 | 600 | 1.43 | Button labels |
| `labelMedium` | 12 | 600 | 1.33 | Tags, field labels |
| `labelSmall` | 11 | 600 | 1.45 | Micro labels, badges |

---

## 3. Spacing Grid

Base unit: **4dp**. All tokens in `lib/core/constants/spacing_constants.dart`.

| Token | Value (dp) | Semantic use |
|---|---|---|
| `xs` | 4 | Icon gaps, micro spacing |
| `sm` | 8 | Tight padding, row gaps |
| `md` | 12 | Input content padding |
| `lg` | 16 | Standard padding |
| `xl` | 20 | Section gaps |
| `xl2` | 24 | Button horizontal padding |
| `xl3` | 32 | Card vertical spacing |
| `xl4` | 48 | Touch targets, section breaks |
| `xl5` | 64 | Page-level spacing |
| `xl6` | 80 | Hero spacing |
| `xl7` | 96 | Large layout gaps |
| `xl8` | 128 | Full-bleed spacing |
| `cardPadding` | 16 | `GlassCard` default padding |
| `cardRadius` | 16 | Card border radius |
| `borderRadius` | 12 | Input, button radius |
| `chipRadius` | 100 | Pill / stadium shape |
| `componentGap` | 16 | Gap between components in column |
| `screenPadding` | 20 | Horizontal screen margins |
| `sectionGap` | 32 | Between page sections |
| `touchTarget` | 48 | Minimum tap area (WCAG 2.5.5) |
| `iconSize` | 24 | Standard icon size |

---

## 4. Responsive Breakpoints

Defined in `lib/core/constants/responsive_constants.dart`.

| DeviceType | Width Threshold | Behaviour |
|---|---|---|
| `mobile` | < 480dp | Single-column, compact layout |
| `tablet` | 480–767dp | Two-column grid, larger typography |
| `desktop` | ≥ 1024dp | Sidebar navigation, multi-column |

Use `Responsive.of(context)` → `DeviceType` enum.  
Use `Responsive.sp(context, base)` for fluid font/icon sizing (clamped 0.65×–1.6×).

---

## 5. Component Gallery

### LeoButton
`lib/presentation/widgets/shared/buttons/leo_button.dart`

**Purpose**: Primary interaction element with 3 variants, press-scale animation, loading state.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `label` | `String` | required | Button text |
| `onPressed` | `VoidCallback?` | required | null = disabled |
| `variant` | `LeoButtonVariant` | `primary` | primary / secondary / tertiary |
| `size` | `LeoButtonSize` | `medium` | small / medium / large |
| `leadingIcon` | `Widget?` | null | Optional prefix icon |
| `isLoading` | `bool` | false | Shows spinner, disables tap |
| `fullWidth` | `bool` | false | Expand to available width |

```dart
// Primary CTA
LeoButton(label: 'View Prediction', onPressed: () => nav.push(...));

// Outlined secondary
LeoButton(
  label: 'Filter',
  variant: LeoButtonVariant.secondary,
  leadingIcon: const Icon(Icons.tune, size: 16),
  onPressed: showFilter,
);

// Loading state
LeoButton(label: 'Saving...', isLoading: true, onPressed: null);
```

---

### GlassCard
`lib/presentation/widgets/shared/cards/glass_card.dart`

**Purpose**: Frosted-glass surface card. Primary container widget throughout the app.

| Parameter | Type | Default |
|---|---|---|
| `child` | `Widget` | required |
| `padding` | `EdgeInsetsGeometry?` | `SpacingScale.cardPadding` all |
| `borderRadius` | `double` | `SpacingScale.cardRadius` (16) |
| `blurRadius` | `double` | 12.0 |
| `backgroundColor` | `Color?` | `AppColors.glass` |
| `borderColor` | `Color?` | `AppColors.glassBorder` |
| `onTap` | `VoidCallback?` | null |

```dart
GlassCard(
  onTap: () => openDetail(match),
  child: Column(children: [
    Text(match.homeTeam, style: LeoTypography.titleMedium),
    SizedBox(height: SpacingScale.sm),
    LeoBadge(label: 'LIVE', variant: LeoBadgeVariant.live),
  ]),
);
```

---

### LeoBadge
`lib/presentation/widgets/shared/badges/leo_badge.dart`

**Purpose**: Semantic status pill for matches, predictions, bets.

| Variant | Colours | Use |
|---|---|---|
| `live` | Red tint + icon dot | Ongoing match |
| `finished` | Neutral | FT result |
| `scheduled` | Primary tint | Upcoming |
| `prediction` | Secondary tint | Leo prediction displayed |
| `betPlaced` | Success tint | Placed bet |
| `custom` | Caller-provided | Freeform |

```dart
LeoBadge(label: 'LIVE 34\'', variant: LeoBadgeVariant.live);
LeoBadge(label: 'FT', variant: LeoBadgeVariant.finished, size: LeoBadgeSize.small);
```

---

### LeoChip
`lib/presentation/widgets/shared/chips/leo_chip.dart`

**Purpose**: Filter/tag chip with selection state and optional delete affordance.

```dart
LeoChip(
  label: 'Premier League',
  selected: _activeLeague == 'PL',
  icon: Icons.sports_soccer,
  onTap: () => setState(() => _activeLeague = 'PL'),
  onDelete: () => clearFilter(),
);
```

---

### LeoTextField
`lib/presentation/widgets/shared/forms/leo_text_field.dart`

**Purpose**: Animated focus-ring input with inline validation.

```dart
LeoTextField(
  label: 'Email',
  hint: 'you@example.com',
  keyboardType: TextInputType.emailAddress,
  validator: (v) => v!.contains('@') ? null : 'Invalid email',
  onChanged: (v) => bloc.add(EmailChanged(v)),
);
```

---

### LeoSwitch / LeoCheckbox
`lib/presentation/widgets/shared/toggles/`

```dart
// Theme toggle
LeoSwitch(
  value: context.watch<ThemeCubit>().isDark,
  onChanged: (_) => context.read<ThemeCubit>().toggleTheme(),
  semanticLabel: 'Toggle dark mode',
);

// Terms checkbox
LeoCheckbox(
  value: _accepted,
  onChanged: (v) => setState(() => _accepted = v ?? false),
  semanticLabel: 'Accept terms and conditions',
);
```

---

## 6. Animation Guidelines

Tokens in `lib/core/animations/leo_animations.dart`.

| Name | Duration | Curve | Use case |
|---|---|---|---|
| `LeoDuration.micro` | 100ms | — | Immediate feedback (ripple) |
| `LeoDuration.short` | 200ms | `LeoCurve.smooth` | Press animations, border transitions |
| `LeoDuration.medium` | 300ms | `LeoCurve.gentle` | Fade-in, slide-in on mount |
| `LeoDuration.long` | 500ms | `LeoCurve.gentle` | Pulse, skeleton shimmer cycle |
| `LeoDuration.xlong` | 800ms | `LeoCurve.bouncy` | Page hero entrance |
| `LeoCurve.smooth` | — | `easeInOutCubic` | All general transitions |
| `LeoCurve.bouncy` | — | `easeOutBack` | Celebratory / confirmation |
| `LeoCurve.sharp` | — | `easeOutExpo` | Dismiss / collapse |
| `LeoCurve.gentle` | — | `easeInOut` | Subtle background animations |

**Stagger pattern** (list items):
```dart
ListView.builder(
  itemBuilder: (ctx, i) => LeoFadeIn(
    delay: Duration(milliseconds: i * 50),
    child: MatchCard(match: matches[i]),
  ),
);
```

**Loading skeleton** (replace CircularProgressIndicator):
```dart
_RepeatingShimmer(width: double.infinity, height: 80, borderRadius: SpacingScale.cardRadius)
```

---

## 7. Accessibility Checklist

- [x] **Contrast** — 7:1 `textPrimary` on `neutral900` (AAA body text)
- [x] **Contrast** — 4.5:1 minimum on all interactive elements  
- [x] **Touch targets** — 48×48dp enforced via `ConstrainedBox` in `LeoButton`, `LeoChip`
- [x] **Semantics** — `Semantics(button: true)` on all tappable widgets
- [x] **Semantics** — `Semantics(toggled:)` on `LeoSwitch`, `checked:` on `LeoCheckbox`
- [x] **Semantics** — `Semantics(label:)` on `MatchCard` (team names + status)
- [x] **Focus rings** — `LeoTextField` shows 2px primary border on focus
- [x] **Screen reader** — error messages exposed via `liveRegion: true`
- [ ] **Images** — add `Semantics(image: true, label:)` to team crest `CachedNetworkImage`
- [ ] **Decorative icons** — wrap with `ExcludeSemantics` where icon is decorative only

---

## 8. Migration Guide

### Colors
```dart
// Before
color: Color(0xFF1E88E5)
// After
color: AppColors.primary
```

### Spacing
```dart
// Before
EdgeInsets.all(16)
// After
EdgeInsets.all(SpacingScale.lg)
```

### Typography
```dart
// Before
TextStyle(fontSize: 14, fontWeight: FontWeight.w600)
// After
LeoTypography.labelLarge
```

### Card
```dart
// Before
Container(
  decoration: BoxDecoration(
    color: Color(0xFF1A2332),
    borderRadius: BorderRadius.circular(12),
    border: Border.all(color: Colors.white12),
  ),
  child: ...,
)
// After
GlassCard(child: ...)
```

### Button
```dart
// Before
ElevatedButton(
  style: ElevatedButton.styleFrom(backgroundColor: Color(0xFF6C63FF)),
  onPressed: onTap,
  child: Text('View'),
)
// After
LeoButton(label: 'View', onPressed: onTap)
```

### Theme Toggle
```dart
// Wire in main.dart (already done):
BlocProvider<ThemeCubit>(create: (_) => ThemeCubit()),

// In any widget:
LeoSwitch(
  value: context.watch<ThemeCubit>().isDark,
  onChanged: (_) => context.read<ThemeCubit>().toggleTheme(),
  semanticLabel: 'Toggle dark mode',
)
```

---

## File Map

| File | Purpose |
|---|---|
| `lib/core/constants/app_colors.dart` | All color tokens + legacy aliases |
| `lib/core/theme/leo_typography.dart` | Full M3 type scale (Inter) |
| `lib/core/constants/spacing_constants.dart` | 4dp grid + semantic aliases |
| `lib/core/constants/responsive_constants.dart` | Breakpoints + Responsive helpers |
| `lib/core/theme/app_theme_v2.dart` | Dark + Light ThemeData |
| `lib/core/theme/theme_cubit.dart` | ThemeMode state management |
| `lib/core/animations/leo_animations.dart` | Duration/Curve tokens + animated widgets |
| `lib/presentation/widgets/shared/buttons/leo_button.dart` | Primary button component |
| `lib/presentation/widgets/shared/cards/glass_card.dart` | Glass surface card |
| `lib/presentation/widgets/shared/badges/leo_badge.dart` | Status badge |
| `lib/presentation/widgets/shared/chips/leo_chip.dart` | Filter chip |
| `lib/presentation/widgets/shared/forms/leo_text_field.dart` | Animated input field |
| `lib/presentation/widgets/shared/toggles/leo_switch.dart` | Theme/feature toggle |
| `lib/presentation/widgets/shared/toggles/leo_checkbox.dart` | Selection checkbox |
