// email_otp_signup_screen.dart: Email OTP sign-up (no SMS/WhatsApp phone OTP).
// Part of LeoBook App — Screens

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:leobookapp/core/constants/app_colors.dart';
import 'package:leobookapp/logic/cubit/user_cubit.dart';
import 'package:leobookapp/presentation/screens/main_screen.dart';
import 'package:leobookapp/presentation/screens/profile_setup_screen.dart';

/// Sign-up with email verification code (Supabase email OTP).
class EmailOtpSignUpScreen extends StatefulWidget {
  const EmailOtpSignUpScreen({
    super.key,
    this.initialEmail = '',
    this.title = 'Create your account',
  });

  final String initialEmail;
  final String title;

  @override
  State<EmailOtpSignUpScreen> createState() => _EmailOtpSignUpScreenState();
}

class _EmailOtpSignUpScreenState extends State<EmailOtpSignUpScreen> {
  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  bool _codeSent = false;

  @override
  void initState() {
    super.initState();
    _emailController.text = widget.initialEmail;
  }

  @override
  void dispose() {
    _emailController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendCode() async {
    final email = _emailController.text.trim();
    if (!_looksLikeEmail(email)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Enter a valid email address.'),
          backgroundColor: AppColors.liveRed,
        ),
      );
      return;
    }
    await context.read<UserCubit>().sendSignUpEmailOtp(email);
    if (!mounted || context.read<UserCubit>().state is UserError) {
      return;
    }
    setState(() => _codeSent = true);
  }

  void _verify() {
    final email = _emailController.text.trim();
    final token = _otpController.text.trim();
    if (token.length < 6) return;
    context.read<UserCubit>().verifyEmailOtp(email, token);
  }

  bool _looksLikeEmail(String s) {
    return s.contains('@') && s.contains('.') && s.length > 5;
  }

  void _goMain() {
    Navigator.of(context).pushAndRemoveUntil(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => const MainScreen(),
        transitionsBuilder: (_, anim, __, child) =>
            FadeTransition(opacity: anim, child: child),
        transitionDuration: const Duration(milliseconds: 400),
      ),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<UserCubit, UserState>(
      listener: (context, state) {
        if (state is UserAuthenticated) {
          _goMain();
        } else if (state is UserProfileIncomplete) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const ProfileSetupScreen()),
          );
        } else if (state is UserError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.message),
              backgroundColor: AppColors.liveRed,
            ),
          );
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.neutral900,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: () {
              if (_codeSent) {
                setState(() => _codeSent = false);
              } else {
                Navigator.of(context).pop();
              }
            },
          ),
        ),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: BlocBuilder<UserCubit, UserState>(
              builder: (context, state) {
                final loading = state is UserLoading;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      widget.title,
                      style: GoogleFonts.dmSans(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _codeSent
                          ? 'Enter the code we sent to your email.'
                          : 'New accounts use email verification (no SMS).',
                      style: GoogleFonts.dmSans(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 28),
                    if (!_codeSent) ...[
                      TextField(
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        style: const TextStyle(color: Colors.white),
                        decoration:
                            _fieldDecoration('Email', Icons.email_outlined),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: loading ? null : _sendCode,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: Text(
                          'Send verification code',
                          style:
                              GoogleFonts.dmSans(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ] else ...[
                      TextField(
                        controller: _otpController,
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly,
                          LengthLimitingTextInputFormatter(8),
                        ],
                        style: const TextStyle(
                            color: Colors.white, letterSpacing: 4),
                        decoration:
                            _fieldDecoration('6-digit code', Icons.pin_outlined),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton(
                        onPressed: loading ? null : _verify,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: Text(
                          'Verify and continue',
                          style:
                              GoogleFonts.dmSans(fontWeight: FontWeight.bold),
                        ),
                      ),
                      TextButton(
                        onPressed: loading ? null : _sendCode,
                        child: Text(
                          'Resend code',
                          style:
                              GoogleFonts.dmSans(color: AppColors.textTertiary),
                        ),
                      ),
                    ],
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _fieldDecoration(String hint, IconData icon) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(color: AppColors.textDisabled, fontSize: 14),
      prefixIcon: Icon(icon, color: AppColors.textTertiary, size: 20),
      filled: true,
      fillColor: AppColors.neutral700.withValues(alpha: 0.5),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.08)),
      ),
    );
  }
}
