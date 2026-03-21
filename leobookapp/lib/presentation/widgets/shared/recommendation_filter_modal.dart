// recommendation_filter_modal.dart: Filter bottom sheet for Top Predictions.
// Part of LeoBook App — Widgets
//
// Classes: RecommendationFilterModal

import 'package:flutter/material.dart';
import 'package:leobookapp/core/constants/app_colors.dart';
import 'package:leobookapp/core/constants/spacing_constants.dart';
import 'package:leobookapp/core/theme/leo_typography.dart';
import 'package:leobookapp/presentation/widgets/shared/chips/leo_chip.dart';
import 'package:leobookapp/presentation/widgets/shared/buttons/leo_button.dart';
import 'package:leobookapp/presentation/widgets/shared/toggles/leo_switch.dart';

class RecommendationFilterModal extends StatefulWidget {
  final List<String> initialLeagues;
  final List<String> initialPredictionTypes;
  final double initialMinOdds;
  final double initialMaxOdds;
  final double initialMinReliability;
  final List<String> initialConfidenceLevels;
  final bool initialOnlyAvailable;
  final List<String> availableLeagues;
  final List<String> availablePredictionTypes;
  final void Function({
    required List<String> leagues,
    required List<String> types,
    required double minOdds,
    required double maxOdds,
    required double minReliability,
    required List<String> confidenceLevels,
    required bool onlyAvailable,
  }) onApply;

  const RecommendationFilterModal({
    super.key,
    this.initialLeagues = const [],
    this.initialPredictionTypes = const [],
    this.initialMinOdds = 1.0,
    this.initialMaxOdds = 10.0,
    this.initialMinReliability = 0.0,
    this.initialConfidenceLevels = const [],
    this.initialOnlyAvailable = false,
    this.availableLeagues = const [],
    this.availablePredictionTypes = const [],
    required this.onApply,
  });

  @override
  State<RecommendationFilterModal> createState() =>
      _RecommendationFilterModalState();
}

class _RecommendationFilterModalState extends State<RecommendationFilterModal> {
  late List<String> _selectedLeagues;
  late List<String> _selectedTypes;
  late double _minOdds;
  late double _maxOdds;
  late double _minReliability;
  late List<String> _selectedConfidence;
  late bool _onlyAvailable;

  static const _confidenceOptions = ['High', 'Medium', 'Low'];

  @override
  void initState() {
    super.initState();
    _selectedLeagues = List.from(widget.initialLeagues);
    _selectedTypes = List.from(widget.initialPredictionTypes);
    _minOdds = widget.initialMinOdds;
    _maxOdds = widget.initialMaxOdds;
    _minReliability = widget.initialMinReliability;
    _selectedConfidence = List.from(widget.initialConfidenceLevels);
    _onlyAvailable = widget.initialOnlyAvailable;
  }

  void _reset() {
    setState(() {
      _selectedLeagues = [];
      _selectedTypes = [];
      _minOdds = 1.0;
      _maxOdds = 10.0;
      _minReliability = 0.0;
      _selectedConfidence = [];
      _onlyAvailable = false;
    });
  }

  void _apply() {
    widget.onApply(
      leagues: _selectedLeagues,
      types: _selectedTypes,
      minOdds: _minOdds,
      maxOdds: _maxOdds,
      minReliability: _minReliability,
      confidenceLevels: _selectedConfidence,
      onlyAvailable: _onlyAvailable,
    );
    Navigator.pop(context);
  }

  void _toggleLeague(String league) {
    setState(() {
      if (_selectedLeagues.contains(league)) {
        _selectedLeagues.remove(league);
      } else {
        _selectedLeagues.add(league);
      }
    });
  }

  void _toggleType(String type) {
    setState(() {
      if (_selectedTypes.contains(type)) {
        _selectedTypes.remove(type);
      } else {
        _selectedTypes.add(type);
      }
    });
  }

  void _toggleConfidence(String level) {
    setState(() {
      if (_selectedConfidence.contains(level)) {
        _selectedConfidence.remove(level);
      } else {
        _selectedConfidence.add(level);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final bottomPad = MediaQuery.of(context).viewPadding.bottom;

    return Container(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.of(context).size.height * 0.92,
      ),
      decoration: const BoxDecoration(
        color: AppColors.neutral900,
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        border: Border(
          top: BorderSide(color: AppColors.neutral700, width: 0.5),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // ── Handle Bar ──
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Container(
              width: 48,
              height: 5,
              decoration: BoxDecoration(
                color: AppColors.neutral600,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),

          // ── Header ──
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: SpacingScale.screenPadding,
              vertical: SpacingScale.sm,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Filters',
                  style: LeoTypography.headlineMedium.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppColors.neutral700,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(
                      Icons.close,
                      size: 18,
                      color: AppColors.textTertiary,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // ── Scrollable Content ──
          Flexible(
            child: SingleChildScrollView(
              padding: EdgeInsets.fromLTRB(
                SpacingScale.screenPadding,
                SpacingScale.lg,
                SpacingScale.screenPadding,
                100 + bottomPad,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ─── Availability Toggle ──────────
                  _buildSectionHeader('Bookie Availability'),
                  const SizedBox(height: SpacingScale.sm),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: SpacingScale.lg,
                      vertical: SpacingScale.md,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.neutral800,
                      borderRadius: BorderRadius.circular(SpacingScale.cardRadius),
                      border: Border.all(
                        color: AppColors.neutral700,
                        width: 0.5,
                      ),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: Text(
                            'Available on Football.com',
                            style: LeoTypography.bodyMedium.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ),
                        LeoSwitch(
                          value: _onlyAvailable,
                          onChanged: (v) => setState(() => _onlyAvailable = v),
                          semanticLabel: 'Filter by bookie availability',
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: SpacingScale.sectionGap),

                  // ─── Leagues ───────────────────────
                  _buildSectionHeader('Leagues'),
                  const SizedBox(height: SpacingScale.md),
                  if (widget.availableLeagues.isEmpty)
                    Text(
                      'No leagues available',
                      style: LeoTypography.bodySmall.copyWith(
                        color: AppColors.textTertiary,
                      ),
                    )
                  else
                    ...widget.availableLeagues.map((league) {
                      final isSelected = _selectedLeagues.contains(league);
                      // Strip region prefix for display
                      String displayName = league;
                      if (league.contains(':')) {
                        displayName = league.split(':').last.trim();
                      }
                      return Padding(
                        padding: const EdgeInsets.only(bottom: SpacingScale.sm),
                        child: GestureDetector(
                          onTap: () => _toggleLeague(league),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: SpacingScale.lg,
                              vertical: SpacingScale.md,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.neutral800,
                              borderRadius: BorderRadius.circular(
                                SpacingScale.borderRadius,
                              ),
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.primary
                                    : AppColors.neutral700,
                                width: isSelected ? 1.0 : 0.5,
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Flexible(
                                  child: Text(
                                    displayName,
                                    style: LeoTypography.bodyMedium.copyWith(
                                      color: isSelected
                                          ? AppColors.textPrimary
                                          : AppColors.textSecondary,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                Container(
                                  width: 22,
                                  height: 22,
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? AppColors.primary
                                        : Colors.transparent,
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(
                                      color: isSelected
                                          ? AppColors.primary
                                          : AppColors.neutral600,
                                      width: 2,
                                    ),
                                  ),
                                  child: isSelected
                                      ? const Icon(
                                          Icons.check,
                                          size: 14,
                                          color: Colors.white,
                                        )
                                      : null,
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    }),

                  const SizedBox(height: SpacingScale.sectionGap),

                  // ─── Prediction Type ──────────────
                  _buildSectionHeader('Prediction Type'),
                  const SizedBox(height: SpacingScale.md),
                  Wrap(
                    spacing: SpacingScale.sm,
                    runSpacing: SpacingScale.sm,
                    children: widget.availablePredictionTypes.map((type) {
                      final isSelected = _selectedTypes.contains(type);
                      return LeoChip(
                        label: type,
                        selected: isSelected,
                        onTap: () => _toggleType(type),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: SpacingScale.sectionGap),

                  // ─── Confidence Level ─────────────
                  _buildSectionHeader('Confidence'),
                  const SizedBox(height: SpacingScale.md),
                  Wrap(
                    spacing: SpacingScale.sm,
                    runSpacing: SpacingScale.sm,
                    children: _confidenceOptions.map((level) {
                      final isSelected = _selectedConfidence.contains(level);
                      return LeoChip(
                        label: level,
                        selected: isSelected,
                        onTap: () => _toggleConfidence(level),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: SpacingScale.sectionGap),

                  // ─── Odds Range ────────────────────
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildSectionHeader('Odds Range'),
                      Text(
                        '${_minOdds.toStringAsFixed(1)} — ${_maxOdds.toStringAsFixed(1)}',
                        style: LeoTypography.labelLarge.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: SpacingScale.lg),
                  SliderTheme(
                    data: SliderThemeData(
                      activeTrackColor: AppColors.primary,
                      inactiveTrackColor: AppColors.neutral700,
                      thumbColor: AppColors.primary,
                      overlayColor: AppColors.primary.withValues(alpha: 0.15),
                      trackHeight: 4,
                      rangeThumbShape: const RoundRangeSliderThumbShape(
                        enabledThumbRadius: 10,
                      ),
                    ),
                    child: RangeSlider(
                      values: RangeValues(_minOdds, _maxOdds),
                      min: 1.0,
                      max: 10.0,
                      divisions: 90,
                      onChanged: (v) {
                        setState(() {
                          _minOdds = v.start;
                          _maxOdds = v.end;
                        });
                      },
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: ['1.0', '3.0', '5.0', '7.0', '10.0']
                          .map((l) => Text(
                                l,
                                style: LeoTypography.labelSmall.copyWith(
                                  color: AppColors.textTertiary,
                                ),
                              ))
                          .toList(),
                    ),
                  ),

                  const SizedBox(height: SpacingScale.sectionGap),

                  // ─── Reliability ───────────────────
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      _buildSectionHeader('Min Reliability'),
                      Text(
                        '${_minReliability.toStringAsFixed(0)}%',
                        style: LeoTypography.labelLarge.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: SpacingScale.lg),
                  SliderTheme(
                    data: SliderThemeData(
                      activeTrackColor: AppColors.primary,
                      inactiveTrackColor: AppColors.neutral700,
                      thumbColor: AppColors.primary,
                      overlayColor: AppColors.primary.withValues(alpha: 0.15),
                      trackHeight: 4,
                    ),
                    child: Slider(
                      value: _minReliability,
                      min: 0,
                      max: 100,
                      divisions: 20,
                      onChanged: (v) =>
                          setState(() => _minReliability = v),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Sticky Footer ──
          Container(
            padding: EdgeInsets.fromLTRB(
              SpacingScale.screenPadding,
              SpacingScale.lg,
              SpacingScale.screenPadding,
              SpacingScale.lg + bottomPad,
            ),
            decoration: const BoxDecoration(
              color: AppColors.neutral900,
              border: Border(
                top: BorderSide(color: AppColors.neutral700, width: 0.5),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: LeoButton(
                    label: 'Reset',
                    variant: LeoButtonVariant.tertiary,
                    onPressed: _reset,
                  ),
                ),
                const SizedBox(width: SpacingScale.lg),
                Expanded(
                  flex: 2,
                  child: LeoButton(
                    label: 'Apply Filters',
                    variant: LeoButtonVariant.primary,
                    fullWidth: true,
                    onPressed: _apply,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String text) {
    return Text(
      text.toUpperCase(),
      style: LeoTypography.labelSmall.copyWith(
        color: AppColors.textTertiary,
        fontWeight: FontWeight.w900,
        letterSpacing: 1.5,
      ),
    );
  }
}
