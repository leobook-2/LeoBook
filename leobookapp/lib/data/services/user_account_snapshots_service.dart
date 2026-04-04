// user_account_snapshots_service.dart: Stairway + Football.com balance from Supabase.
// Part of LeoBook App — Data Services

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class UserStairwaySnapshot {
  final int currentStep;
  final String? lastUpdated;
  final String? lastResult;
  final int cycleCount;
  final String? weekBucket;
  final int weekCyclesCompleted;

  const UserStairwaySnapshot({
    required this.currentStep,
    this.lastUpdated,
    this.lastResult,
    this.cycleCount = 0,
    this.weekBucket,
    this.weekCyclesCompleted = 0,
  });

  factory UserStairwaySnapshot.fromRow(Map<String, dynamic> m) {
    return UserStairwaySnapshot(
      currentStep: (m['current_step'] as num?)?.toInt() ?? 1,
      lastUpdated: m['last_updated']?.toString(),
      lastResult: m['last_result']?.toString(),
      cycleCount: (m['cycle_count'] as num?)?.toInt() ?? 0,
      weekBucket: m['week_bucket']?.toString(),
      weekCyclesCompleted: (m['week_cycles_completed'] as num?)?.toInt() ?? 0,
    );
  }
}

class UserFbBalanceSnapshot {
  final double balance;
  final String currency;
  final String? source;
  final String? capturedAt;

  const UserFbBalanceSnapshot({
    required this.balance,
    this.currency = 'NGN',
    this.source,
    this.capturedAt,
  });

  factory UserFbBalanceSnapshot.fromRow(Map<String, dynamic> m) {
    return UserFbBalanceSnapshot(
      balance: (m['balance'] as num?)?.toDouble() ?? 0,
      currency: m['currency']?.toString() ?? 'NGN',
      source: m['source']?.toString(),
      capturedAt: m['captured_at']?.toString(),
    );
  }
}

class UserAccountSnapshotsService {
  UserAccountSnapshotsService({SupabaseClient? client}) : _sb = client ?? Supabase.instance.client;

  final SupabaseClient _sb;

  String? get _uid => _sb.auth.currentUser?.id;

  Future<UserStairwaySnapshot?> fetchStairway() async {
    final uid = _uid;
    if (uid == null) return null;
    try {
      final row = await _sb.from('user_stairway_state').select().eq('user_id', uid).maybeSingle();
      if (row == null) return null;
      return UserStairwaySnapshot.fromRow(Map<String, dynamic>.from(row));
    } catch (e) {
      debugPrint('fetchStairway: $e');
      return null;
    }
  }

  Future<UserFbBalanceSnapshot?> fetchFbBalance() async {
    final uid = _uid;
    if (uid == null) return null;
    try {
      final row = await _sb.from('user_fb_balance').select().eq('user_id', uid).maybeSingle();
      if (row == null) return null;
      return UserFbBalanceSnapshot.fromRow(Map<String, dynamic>.from(row));
    } catch (e) {
      debugPrint('fetchFbBalance: $e');
      return null;
    }
  }
}
