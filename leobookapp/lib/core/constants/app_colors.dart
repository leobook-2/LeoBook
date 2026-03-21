// app_colors.dart — LeoBook Design System v3.0 (UI Inspiration Palette)
// Part of LeoBook App — Constants
//
// Color tokens derived from UI Inspiration color spec.
// Font: DM Sans. Primary accent: #775CDF (coloured).

import 'package:flutter/material.dart';

abstract final class AppColors {
  // ─── Primary (coloured) ─────────────────────────────────
  static const Color primary = Color(0xFF775CDF);
  static const Color primaryLight = Color(0xFF8B6FE8);
  static const Color primaryDark = Color(0xFF6247C5);
  // Button states from inspiration
  static const Color primaryOnTap = Color(0xFF6247C5);

  // ─── Secondary ───────────────────────────────────────────
  static const Color secondary = Color(0xFF8B5B8C);
  static const Color secondaryLight = Color(0xFFA878A9);
  static const Color secondaryDark = Color(0xFF6E4570);
  static const Color secondaryOnTap = Color(0xFF7E9EC0);

  // ─── Accent ──────────────────────────────────────────────
  static const Color accentPrimary = Color(0xFFB9C0FF);
  static const Color accentSecondary = Color(0xFFB5C89C);

  // ─── Semantic States ──────────────────────────────────────
  static const Color success = Color(0xFF1CDB2F);
  static const Color successLight = Color(0xFF6FE87A);
  static const Color warning = Color(0xFFF5CB3E);
  static const Color warningLight = Color(0xFFFADE78);
  static const Color error = Color(0xFFEB3333);
  static const Color errorLight = Color(0xFFF27A7A);

  // ─── Background Scale (Dark Theme) ───────────────────────
  // globe — general background
  static const Color neutral900 = Color(0xFF1C1B20);
  // island — cards, modals, windows
  static const Color neutral800 = Color(0xFF24232A);
  // on_island — nav bars, floating elements, borders
  static const Color neutral700 = Color(0xFF313038);
  // on_island_hover
  static const Color neutral600 = Color(0xFF3B3A42);
  static const Color neutral500 = Color(0xFF4A4952);
  static const Color neutral400 = Color(0xFF6B6B7A);
  static const Color neutral300 = Color(0xFF9F9F9F);
  static const Color neutral200 = Color(0xFFD0D0D6);
  static const Color neutral100 = Color(0xFFE8E8F0);
  static const Color neutral50 = Color(0xFFF5F5FA);

  // ─── Glass / Overlay ──────────────────────────────────────
  static const Color glass = Color(0x1AFFFFFF);
  static const Color glassBorder = Color(0x33FFFFFF);
  static const Color glassDark = Color(0x1A000000);

  // ─── Overlay (from inspiration) ───────────────────────────
  static const Color overlayLight = Color(0x66000000); // 40% black
  static const Color overlayDark = Color(0x99000000);  // 60% black

  // ─── Divider ──────────────────────────────────────────────
  static const Color dividerLight = Color(0xFF303030);
  static const Color divider = Color(0xFF24232A);

  // ─── Text on Dark ─────────────────────────────────────────
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFE2E2E2);
  static const Color textTertiary = Color(0xFF9F9F9F);
  static const Color textDisabled = Color(0xFF6B6B7A);
  static const Color textInverse = Color(0xFF1C1B20);

  // ─── Text on Coloured Background ─────────────────────────
  static const Color textOnPrimaryLight = Color(0xFFFFFFFF);
  static const Color textOnPrimaryDark = Color(0xFF1C1B20);

  // ─── Text on Light ────────────────────────────────────────
  static const Color textPrimaryLight = Color(0xFF1C1B20);
  static const Color textSecondaryLight = Color(0xFF4A4952);
  static const Color textDisabledLight = Color(0xFF9F9F9F);

  // ─── Button Text ──────────────────────────────────────────
  static const Color textButtonDark = Color(0xFF1C1B20);
  static const Color textButtonLight = Color(0xFFFFFFFF);

  // ─── Surface ──────────────────────────────────────────────
  static const Color surfaceDark = Color(0xFF24232A);
  static const Color surfaceCard = Color(0xFF24232A);
  static const Color surfaceElevated = Color(0xFF313038);

  // ─── Live ─────────────────────────────────────────────────
  static const Color liveRed = Color(0xFFEB3333);

  // ─── Liquid Glass aliases (backward compat) ───────────────
  static const Color liquidGlassBorderDark = Color(0x1AFFFFFF);
  static const Color liquidGlassBorderLight = Color(0x1A000000);

  // ─── Legacy aliases (kept for existing widget compat) ─────
  static const Color textGrey = textTertiary;
  static const Color textDark = textPrimaryLight;
}
