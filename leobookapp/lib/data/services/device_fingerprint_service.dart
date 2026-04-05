// device_fingerprint_service.dart: Supabase CRUD for user_device_fingerprint.
// Part of LeoBook App — Data Services
//
// Stores per-user Football.com session fingerprint overrides:
//   proxy_server, user_agent, viewport_w, viewport_h
// The Python backend reads these at browser-launch time to mirror the user's
// device/IP, making Chapter 2 sessions appear tied to the user's fingerprint.

import 'package:flutter/foundation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class UserDeviceFingerprint {
  final String userId;
  final String? proxyServer;   // e.g. 'http://user:pass@1.2.3.4:8080'
  final String? userAgent;     // full UA string
  final int? viewportW;
  final int? viewportH;
  final String? updatedAt;

  const UserDeviceFingerprint({
    required this.userId,
    this.proxyServer,
    this.userAgent,
    this.viewportW,
    this.viewportH,
    this.updatedAt,
  });

  factory UserDeviceFingerprint.empty(String userId) =>
      UserDeviceFingerprint(userId: userId);

  factory UserDeviceFingerprint.fromRow(Map<String, dynamic> row) {
    return UserDeviceFingerprint(
      userId: row['user_id'] as String? ?? '',
      proxyServer: row['proxy_server'] as String?,
      userAgent: row['user_agent'] as String?,
      viewportW: (row['viewport_w'] as num?)?.toInt(),
      viewportH: (row['viewport_h'] as num?)?.toInt(),
      updatedAt: row['updated_at']?.toString(),
    );
  }

  Map<String, dynamic> toRow() => {
        'user_id': userId,
        'proxy_server': proxyServer?.trim().isEmpty == true ? null : proxyServer?.trim(),
        'user_agent': userAgent?.trim().isEmpty == true ? null : userAgent?.trim(),
        'viewport_w': viewportW,
        'viewport_h': viewportH,
        'updated_at': DateTime.now().toUtc().toIso8601String(),
      };

  UserDeviceFingerprint copyWith({
    String? proxyServer,
    String? userAgent,
    int? viewportW,
    int? viewportH,
  }) =>
      UserDeviceFingerprint(
        userId: userId,
        proxyServer: proxyServer ?? this.proxyServer,
        userAgent: userAgent ?? this.userAgent,
        viewportW: viewportW ?? this.viewportW,
        viewportH: viewportH ?? this.viewportH,
      );

  bool get isEmpty =>
      (proxyServer == null || proxyServer!.isEmpty) &&
      (userAgent == null || userAgent!.isEmpty) &&
      viewportW == null &&
      viewportH == null;
}

class DeviceFingerprintService {
  DeviceFingerprintService({SupabaseClient? client})
      : _sb = client ?? Supabase.instance.client;

  final SupabaseClient _sb;
  static const _table = 'user_device_fingerprint';

  String? get _uid => _sb.auth.currentUser?.id;

  /// Load the current user's fingerprint. Returns empty if not set.
  Future<UserDeviceFingerprint> load() async {
    final uid = _uid;
    if (uid == null) return UserDeviceFingerprint.empty('');
    try {
      final row = await _sb.from(_table).select().eq('user_id', uid).maybeSingle();
      if (row == null) return UserDeviceFingerprint.empty(uid);
      return UserDeviceFingerprint.fromRow(Map<String, dynamic>.from(row));
    } catch (e) {
      debugPrint('DeviceFingerprintService.load: $e');
      return UserDeviceFingerprint.empty(uid);
    }
  }

  /// Upsert the fingerprint row for the current user.
  Future<bool> save(UserDeviceFingerprint fp) async {
    final uid = _uid;
    if (uid == null) return false;
    try {
      await _sb.from(_table).upsert(fp.toRow(), onConflict: 'user_id');
      return true;
    } catch (e) {
      debugPrint('DeviceFingerprintService.save: $e');
      return false;
    }
  }

  /// Clear all fingerprint overrides (row stays, all fields nulled).
  Future<bool> clear() async {
    final uid = _uid;
    if (uid == null) return false;
    return save(UserDeviceFingerprint.empty(uid));
  }
}
