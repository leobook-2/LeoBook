// stairway_table.dart: Mirrors Core/System/guardrails.py STAIRWAY_TABLE for UI.

const List<Map<String, dynamic>> kStairwayTable = [
  {'step': 1, 'stake': 1000, 'odds_target': 4.0, 'payout': 4000},
  {'step': 2, 'stake': 4000, 'odds_target': 4.0, 'payout': 16000},
  {'step': 3, 'stake': 16000, 'odds_target': 4.0, 'payout': 64000},
  {'step': 4, 'stake': 64000, 'odds_target': 4.0, 'payout': 256000},
  {'step': 5, 'stake': 256000, 'odds_target': 4.0, 'payout': 1024000},
  {'step': 6, 'stake': 1024000, 'odds_target': 4.0, 'payout': 4096000},
  {'step': 7, 'stake': 2048000, 'odds_target': 4.0, 'payout': 2187000},
];

Map<String, dynamic> stairwayStepInfo(int step) {
  final idx = (step.clamp(1, 7)) - 1;
  return kStairwayTable[idx];
}
