// stairway_model.dart: Project Stairway data model with geometric progression.
// Part of LeoBook App — Data Models
//
// Classes: StairwayStep, StairwayProject

import 'dart:math' as math;

/// One step in a Stairway project.
class StairwayStep {
  final int stepNumber;     // 1-based
  final double seedAmount;  // starting balance for this step
  final double targetAmount;// balance needed to complete this step
  final String status;      // 'pending' | 'active' | 'completed' | 'failed'

  const StairwayStep({
    required this.stepNumber,
    required this.seedAmount,
    required this.targetAmount,
    this.status = 'pending',
  });

  bool get isPending   => status == 'pending';
  bool get isActive    => status == 'active';
  bool get isCompleted => status == 'completed';
  bool get isFailed    => status == 'failed';

  /// Profit needed to complete this step.
  double get profitNeeded => targetAmount - seedAmount;

  /// Multiplier from seed to target for this single step.
  double get stepMultiplier => targetAmount / seedAmount;
}

/// A complete Project Stairway with N steps and geometric progression.
///
/// Example: seed=1000, target=2x over 7 steps:
///   stepMultiplier = 2.0^(1/7) ≈ 1.1041
///   Step 1: 1000.00 → 1104.09
///   Step 2: 1104.09 → 1219.02
///   ...
///   Step 7: 1901.53 → 2100.00  (≈ 2000 due to rounding)
class StairwayProject {
  final double seedAmount;
  final double targetMultiplier; // e.g. 2.0 for doubling
  final int stepCount;           // e.g. 7
  final int currentStep;         // 1-based, from user_stairway_state
  final int cycleCount;
  final String? lastResult;

  const StairwayProject({
    this.seedAmount = 1000.0,
    this.targetMultiplier = 2.0,
    this.stepCount = 7,
    this.currentStep = 1,
    this.cycleCount = 0,
    this.lastResult,
  });

  /// Per-step geometric multiplier: targetMultiplier^(1/stepCount).
  double get perStepMultiplier =>
      math.pow(targetMultiplier, 1.0 / stepCount).toDouble();

  /// Final target balance after all steps.
  double get totalTarget => seedAmount * targetMultiplier;

  /// Generate all steps with precise seed/target amounts.
  List<StairwayStep> get steps {
    final m = perStepMultiplier;
    final list = <StairwayStep>[];
    double stepSeed = seedAmount;
    for (int i = 1; i <= stepCount; i++) {
      final stepTarget = stepSeed * m;
      final String status;
      if (i < currentStep) {
        status = 'completed';
      } else if (i == currentStep) {
        status = 'active';
      } else {
        status = 'pending';
      }
      list.add(StairwayStep(
        stepNumber: i,
        seedAmount: stepSeed,
        targetAmount: stepTarget,
        status: status,
      ));
      stepSeed = stepTarget;
    }
    return list;
  }

  /// The currently active step (or last step if finished).
  StairwayStep get activeStep {
    final idx = (currentStep - 1).clamp(0, stepCount - 1);
    return steps[idx];
  }

  /// Overall progress 0.0–1.0 (completed steps / total steps).
  double get progressPct =>
      ((currentStep - 1).clamp(0, stepCount)) / stepCount;

  String get progressLabel => 'Step $currentStep / $stepCount';
}
