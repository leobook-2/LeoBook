// rl_training_jobs_service.dart: Queue RL training jobs in Supabase.
// Part of LeoBook App — Data Services

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class RlTrainingJobsService {
  RlTrainingJobsService({SupabaseClient? client}) : _sb = client ?? Supabase.instance.client;

  final SupabaseClient _sb;
  static const _table = 'rl_training_jobs';

  String? get _uid => _sb.auth.currentUser?.id;

  Future<void> enqueue({
    required String ruleEngineId,
    String trainSeason = 'current',
    int phase = 1,
  }) async {
    final uid = _uid;
    if (uid == null) return;
    await _sb.from(_table).insert({
      'user_id': uid,
      'rule_engine_id': ruleEngineId,
      'status': 'queued',
      'train_season': trainSeason,
      'phase': phase,
    });
  }

  Future<List<Map<String, dynamic>>> recentJobs({int limit = 20}) async {
    final uid = _uid;
    if (uid == null) return [];
    try {
      final rows = await _sb
          .from(_table)
          .select()
          .eq('user_id', uid)
          .order('requested_at', ascending: false)
          .limit(limit) as List;
      return rows.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } catch (e) {
      debugPrint('recentJobs: $e');
      return [];
    }
  }
}
