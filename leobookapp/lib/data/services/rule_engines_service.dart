// rule_engines_service.dart: Supabase CRUD for user_rule_engines.
// Part of LeoBook App — Data Services

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/rule_config_model.dart';

class RuleEnginesService {
  RuleEnginesService({SupabaseClient? client}) : _sb = client ?? Supabase.instance.client;

  final SupabaseClient _sb;
  static const _table = 'user_rule_engines';

  String _newId() => 'eng_${DateTime.now().millisecondsSinceEpoch}';

  String? get _uid => _sb.auth.currentUser?.id;

  /// Full JSON blob for worker/Python parity (includes weights, scope, etc.).
  Map<String, dynamic> _rowToModelMap(Map<String, dynamic> row) {
    final cfg = row['config_json'];
    final base = cfg is Map<String, dynamic>
        ? Map<String, dynamic>.from(cfg)
        : <String, dynamic>{};
    base['id'] = row['id']?.toString() ?? base['id'] ?? 'default';
    base['name'] = row['name'] ?? base['name'] ?? 'Engine';
    base['description'] = row['description'] ?? base['description'] ?? '';
    base['is_default'] = row['is_default'] == true;
    if (row['is_builtin_default'] == true) {
      base['is_builtin_default'] = true;
    }
    return base;
  }

  RuleConfigModel rowToEngine(Map<String, dynamic> row) {
    return RuleConfigModel.fromJson(_rowToModelMap(row));
  }

  Future<void> ensureBuiltinDefault() async {
    final uid = _uid;
    if (uid == null) return;
    try {
      final existing =
          await _sb.from(_table).select('id').eq('user_id', uid).limit(1) as List?;
      if (existing != null && existing.isNotEmpty) return;

      final def = RuleConfigModel(
        id: 'default',
        name: 'Default',
        description: 'Standard LeoBook prediction logic',
        isDefault: true,
      );
      await saveEngine(def, isBuiltinDefault: true);
    } catch (e) {
      debugPrint('ensureBuiltinDefault: $e');
    }
  }

  Future<List<RuleConfigModel>> loadAll() async {
    final uid = _uid;
    if (uid == null) return [];
    try {
      await ensureBuiltinDefault();
      final rows =
          await _sb.from(_table).select().eq('user_id', uid).order('created_at') as List;
      return rows
          .map((e) => rowToEngine(Map<String, dynamic>.from(e as Map)))
          .toList();
    } catch (e) {
      debugPrint('RuleEnginesService.loadAll: $e');
      return [];
    }
  }

  Future<int> countCustomEngines() async {
    final all = await loadAll();
    return all.where((e) => e.id != 'default' && !e.name.startsWith('Default')).length;
  }

  /// Custom engines = not the built-in default id.
  int countCustomEnginesSync(List<RuleConfigModel> engines) {
    return engines.where((e) => e.id != 'default').length;
  }

  Future<void> saveEngine(RuleConfigModel engine, {bool isBuiltinDefault = false}) async {
    final uid = _uid;
    if (uid == null) throw StateError('Not signed in');

    final id = engine.id.isEmpty ? _newId() : engine.id;
    final json = engine.toJson();
    json['id'] = id;

    final now = DateTime.now().toUtc().toIso8601String();
    final payload = <String, dynamic>{
      'id': id,
      'user_id': uid,
      'name': engine.name,
      'description': engine.description,
      'config_json': json,
      'is_default': engine.isDefault,
      'is_builtin_default': isBuiltinDefault || id == 'default',
      'updated_at': now,
    };

    await _sb.from(_table).upsert(payload, onConflict: 'id');
  }

  Future<void> setDefaultEngine(String engineId) async {
    final uid = _uid;
    if (uid == null) return;
    final rows = await _sb.from(_table).select('id').eq('user_id', uid) as List;
    final now = DateTime.now().toUtc().toIso8601String();
    for (final r in rows) {
      final id = (r as Map)['id']?.toString();
      if (id == null) continue;
      await _sb.from(_table).update({
        'is_default': id == engineId,
        'updated_at': now,
      }).eq('id', id);
    }
  }

  Future<bool> deleteEngine(String engineId) async {
    if (engineId == 'default') return false;
    final uid = _uid;
    if (uid == null) return false;
    try {
      final row = await _sb.from(_table).select('is_builtin_default').eq('id', engineId).maybeSingle();
      if (row != null && row['is_builtin_default'] == true) return false;
      await _sb.from(_table).delete().eq('id', engineId).eq('user_id', uid);
      return true;
    } catch (e) {
      debugPrint('deleteEngine: $e');
      return false;
    }
  }

  Future<RuleConfigModel?> getDefaultEngine() async {
    final list = await loadAll();
    try {
      return list.firstWhere((e) => e.isDefault);
    } catch (_) {
      return list.isNotEmpty ? list.first : null;
    }
  }
}
