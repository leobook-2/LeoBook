// leo_typography.dart — LeoBook Design System v3.0 (DM Sans)
// Part of LeoBook App — Theme
//
// Full Material 3 type scale using DM Sans (Google Fonts).
// Mapped from UI Inspiration typography spec.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../constants/app_colors.dart';

final class LeoTypography {
  LeoTypography._();

  // ─── Display (Title XL: bold 40) ──────────────────────────
  static TextStyle get displayLarge => GoogleFonts.dmSans(
        fontSize: 40,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      );

  static TextStyle get displayMedium => GoogleFonts.dmSans(
        fontSize: 36,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.25,
      );

  static TextStyle get displaySmall => GoogleFonts.dmSans(
        fontSize: 32,
        fontWeight: FontWeight.w700,
      );

  // ─── Headline (Title L: bold 24, Title M: bold 20) ────────
  static TextStyle get headlineLarge => GoogleFonts.dmSans(
        fontSize: 28,
        fontWeight: FontWeight.w700,
      );

  static TextStyle get headlineMedium => GoogleFonts.dmSans(
        fontSize: 24,
        fontWeight: FontWeight.w700,
      );

  static TextStyle get headlineSmall => GoogleFonts.dmSans(
        fontSize: 20,
        fontWeight: FontWeight.w700,
      );

  // ─── Title (Title S: bold 18) ─────────────────────────────
  static TextStyle get titleLarge => GoogleFonts.dmSans(
        fontSize: 18,
        fontWeight: FontWeight.w700,
      );

  static TextStyle get titleMedium => GoogleFonts.dmSans(
        fontSize: 17,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.15,
      );

  static TextStyle get titleSmall => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
      );

  // ─── Body (Body: regular/medium 17, Subhead: 14) ──────────
  static TextStyle get bodyLarge => GoogleFonts.dmSans(
        fontSize: 17,
        fontWeight: FontWeight.w400,
      );

  static TextStyle get bodyMedium => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.25,
      );

  static TextStyle get bodySmall => GoogleFonts.dmSans(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        letterSpacing: 0.4,
      );

  // ─── Label ────────────────────────────────────────────────
  static TextStyle get labelLarge => GoogleFonts.dmSans(
        fontSize: 14,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.1,
      );

  static TextStyle get labelMedium => GoogleFonts.dmSans(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.5,
      );

  static TextStyle get labelSmall => GoogleFonts.dmSans(
        fontSize: 11,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.5,
      );

  // ─── TextTheme Factory ────────────────────────────────────
  static TextTheme toTextTheme(ColorScheme colorScheme) {
    final onSurface = colorScheme.onSurface;
    final onSurfaceVariant = colorScheme.onSurfaceVariant;
    final disabled = colorScheme.brightness == Brightness.dark
        ? AppColors.textDisabled
        : AppColors.textDisabledLight;

    return TextTheme(
      displayLarge: displayLarge.copyWith(color: onSurface),
      displayMedium: displayMedium.copyWith(color: onSurface),
      displaySmall: displaySmall.copyWith(color: onSurface),
      headlineLarge: headlineLarge.copyWith(color: onSurface),
      headlineMedium: headlineMedium.copyWith(color: onSurface),
      headlineSmall: headlineSmall.copyWith(color: onSurface),
      titleLarge: titleLarge.copyWith(color: onSurface),
      titleMedium: titleMedium.copyWith(color: onSurface),
      titleSmall: titleSmall.copyWith(color: onSurfaceVariant),
      bodyLarge: bodyLarge.copyWith(color: onSurface),
      bodyMedium: bodyMedium.copyWith(color: onSurfaceVariant),
      bodySmall: bodySmall.copyWith(color: disabled),
      labelLarge: labelLarge.copyWith(color: onSurface),
      labelMedium: labelMedium.copyWith(color: onSurfaceVariant),
      labelSmall: labelSmall.copyWith(color: disabled),
    );
  }
}
