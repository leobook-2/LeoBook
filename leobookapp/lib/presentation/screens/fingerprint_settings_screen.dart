// fingerprint_settings_screen.dart: Per-user Football.com session fingerprint editor.
// Part of LeoBook App — Screens
//
// Allows users to set proxy_server, user_agent, viewport_w/h so the Python
// backend mirrors their device when opening Football.com for Chapter 2 automation.

import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:leobookapp/core/constants/app_colors.dart';
import 'package:leobookapp/data/services/device_fingerprint_service.dart';

class FingerprintSettingsScreen extends StatefulWidget {
  const FingerprintSettingsScreen({super.key});

  @override
  State<FingerprintSettingsScreen> createState() =>
      _FingerprintSettingsScreenState();
}

class _FingerprintSettingsScreenState
    extends State<FingerprintSettingsScreen> {
  final _service = DeviceFingerprintService();
  final _proxyCtrl = TextEditingController();
  final _uaCtrl = TextEditingController();
  final _vpwCtrl = TextEditingController();
  final _vphCtrl = TextEditingController();

  String _userId = '';
  bool _loading = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    _userId =
        Supabase.instance.client.auth.currentUser?.id ?? '';
    final fp = await _service.load();
    _proxyCtrl.text = fp.proxyServer ?? '';
    _uaCtrl.text = fp.userAgent ?? '';
    _vpwCtrl.text = fp.viewportW?.toString() ?? '';
    _vphCtrl.text = fp.viewportH?.toString() ?? '';
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    final fp = UserDeviceFingerprint(
      userId: _userId,
      proxyServer:
          _proxyCtrl.text.trim().isEmpty ? null : _proxyCtrl.text.trim(),
      userAgent: _uaCtrl.text.trim().isEmpty ? null : _uaCtrl.text.trim(),
      viewportW: int.tryParse(_vpwCtrl.text.trim()),
      viewportH: int.tryParse(_vphCtrl.text.trim()),
    );
    final ok = await _service.save(fp);
    if (mounted) {
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(ok ? 'Fingerprint saved.' : 'Save failed — check your connection.'),
        backgroundColor: ok ? AppColors.success : AppColors.liveRed,
      ));
    }
  }

  Future<void> _clear() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppColors.neutral800,
        title: const Text('Clear fingerprint?',
            style: TextStyle(color: Colors.white)),
        content: const Text(
          'Leo will use the default device settings for your Football.com sessions.',
          style: TextStyle(color: AppColors.textGrey, fontSize: 13),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel',
                style: TextStyle(color: AppColors.textGrey)),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Clear',
                style: TextStyle(color: AppColors.liveRed)),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    setState(() => _saving = true);
    final ok = await _service.clear();
    if (ok) {
      _proxyCtrl.clear();
      _uaCtrl.clear();
      _vpwCtrl.clear();
      _vphCtrl.clear();
    }
    if (mounted) {
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(ok ? 'Fingerprint cleared.' : 'Clear failed.'),
      ));
    }
  }

  @override
  void dispose() {
    _proxyCtrl.dispose();
    _uaCtrl.dispose();
    _vpwCtrl.dispose();
    _vphCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.neutral900,
      appBar: AppBar(
        backgroundColor: AppColors.neutral900,
        surfaceTintColor: Colors.transparent,
        title: const Text('Session Fingerprint'),
        actions: [
          if (!_saving && !_loading)
            TextButton(
              onPressed: _clear,
              child: const Text('Clear',
                  style: TextStyle(color: AppColors.liveRed)),
            ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              children: [
                // ── Info banner ─────────────────────────────────────────
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceDark,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white10),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.info_outline,
                          size: 18,
                          color: AppColors.primary.withValues(alpha: 0.8)),
                      const SizedBox(width: 10),
                      const Expanded(
                        child: Text(
                          'These overrides are used when Leo opens Football.com '
                          'on your behalf (Chapter 2). Leave blank to use defaults.',
                          style: TextStyle(
                              fontSize: 12,
                              color: AppColors.textGrey,
                              height: 1.5),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 28),

                // ── Proxy server ───────────────────────────────────────
                _sectionLabel('Proxy server'),
                const SizedBox(height: 8),
                _field(
                  controller: _proxyCtrl,
                  hint: 'http://user:pass@1.2.3.4:8080',
                  keyboardType: TextInputType.url,
                ),
                const SizedBox(height: 4),
                const Text(
                  'Route Football.com traffic through your device\'s IP.',
                  style: TextStyle(fontSize: 11, color: AppColors.textDisabled),
                ),
                const SizedBox(height: 20),

                // ── User agent ─────────────────────────────────────────
                _sectionLabel('User agent'),
                const SizedBox(height: 8),
                _field(
                  controller: _uaCtrl,
                  hint: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)…',
                  maxLines: 3,
                ),
                const SizedBox(height: 4),
                const Text(
                  'Match the browser UA your device uses when you visit Football.com manually.',
                  style: TextStyle(fontSize: 11, color: AppColors.textDisabled),
                ),
                const SizedBox(height: 20),

                // ── Viewport ───────────────────────────────────────────
                _sectionLabel('Viewport (pixels)'),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _field(
                        controller: _vpwCtrl,
                        hint: '390',
                        keyboardType: TextInputType.number,
                        label: 'Width',
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _field(
                        controller: _vphCtrl,
                        hint: '844',
                        keyboardType: TextInputType.number,
                        label: 'Height',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                const Text(
                  'Default: 390 × 844 (iPhone 14 portrait).',
                  style: TextStyle(fontSize: 11, color: AppColors.textDisabled),
                ),
                const SizedBox(height: 36),

                // ── Save button ────────────────────────────────────────
                FilledButton(
                  onPressed: _saving ? null : _save,
                  style: FilledButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _saving
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2),
                        )
                      : const Text(
                          'Save fingerprint',
                          style: TextStyle(
                              fontWeight: FontWeight.w700, fontSize: 15),
                        ),
                ),
                const SizedBox(height: 32),
              ],
            ),
    );
  }

  Widget _sectionLabel(String label) => Text(
        label,
        style: const TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: AppColors.textGrey,
          letterSpacing: 0.5,
        ),
      );

  Widget _field({
    required TextEditingController controller,
    String? hint,
    String? label,
    TextInputType? keyboardType,
    int maxLines = 1,
  }) {
    return TextField(
      controller: controller,
      keyboardType: keyboardType,
      maxLines: maxLines,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: AppColors.textGrey, fontSize: 13),
        hintText: hint,
        hintStyle:
            const TextStyle(color: AppColors.textDisabled, fontSize: 12),
        filled: true,
        fillColor: AppColors.surfaceDark,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary),
        ),
      ),
    );
  }
}
