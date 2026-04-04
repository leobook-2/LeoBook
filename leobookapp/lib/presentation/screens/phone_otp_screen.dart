// phone_otp_screen.dart: SMS/WhatsApp OTP entrypoint removed (policy).
// Part of LeoBook App — Screens
//
// Use email OTP sign-up or phone + password sign-in instead.

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:leobookapp/core/constants/app_colors.dart';
import 'package:leobookapp/data/repositories/auth_repository.dart';
import 'package:leobookapp/presentation/screens/login_screen.dart';

class PhoneOtpScreen extends StatelessWidget {
  const PhoneOtpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.neutral900,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Phone SMS sign-in',
                style: GoogleFonts.dmSans(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                AuthRepository.kSmsOtpDisabledMessage,
                style: GoogleFonts.dmSans(
                  fontSize: 14,
                  color: AppColors.textTertiary,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: () {
                  Navigator.of(context).pushAndRemoveUntil(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                    (_) => false,
                  );
                },
                child: const Text('Back to sign in'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
