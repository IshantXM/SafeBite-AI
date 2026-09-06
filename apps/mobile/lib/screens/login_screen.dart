import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../services/api_service.dart';
import '../widgets/app_logo.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController(text: 'inspector@safebite-ai.local');
  final _password = TextEditingController();
  final _otp = TextEditingController();
  final _accessKey = TextEditingController();
  String _role = 'Inspector';
  bool _loading = false;
  bool _otpRequested = false;
  bool _showKey = false;
  String? _devOtp;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _otp.dispose();
    _accessKey.dispose();
    super.dispose();
  }

  Future<void> _requestOtp() async {
    if (_email.text.trim().isEmpty) {
      _message('Enter your email address');
      return;
    }
    setState(() => _loading = true);
    final devOtp = await ApiService.requestOtp(_email.text.trim());
    if (!mounted) return;
    setState(() {
      _loading = false;
      _otpRequested = true;
      _devOtp = devOtp;
      if (devOtp != null) _otp.text = devOtp;
    });
    _message(devOtp == null ? 'OTP sent by SafetyBite-AI. Check your email.' : 'Development OTP generated. Enter it to continue.');
  }

  Future<void> _verifyOtp() async {
    setState(() => _loading = true);
    final success = await ApiService.verifyOtp(email: _email.text.trim(), code: _otp.text.trim(), role: _role);
    if (!mounted) return;
    setState(() => _loading = false);
    if (success) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      _message('Invalid or expired OTP');
    }
  }

  Future<void> _passwordLogin() async {
    setState(() => _loading = true);
    final success = await ApiService.login(username: _email.text.trim(), password: _password.text);
    if (!mounted) return;
    setState(() => _loading = false);
    if (success) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      _message('Sign in failed. Check the API or use email OTP.');
    }
  }

  Future<void> _keyLogin() async {
    setState(() => _loading = true);
    final success = await ApiService.loginWithInspectorKey(_accessKey.text.trim());
    if (!mounted) return;
    setState(() => _loading = false);
    if (success) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      _message('Invalid inspector access key');
    }
  }

  void _message(String text) => ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(text)));

  InputDecoration _decoration(String hint, IconData icon) => InputDecoration(
        hintText: hint,
        prefixIcon: Icon(icon, color: const Color(0xFF005F52)),
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF9),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 28),
          child: Column(
            children: [
              const AppLogo(size: 78),
              const SizedBox(height: 12),
              Text('SafetyBite-AI', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w800, color: const Color(0xFF1B2533))),
              const SizedBox(height: 4),
              Text('SECURE FOOD COMPLIANCE', style: GoogleFonts.inter(fontSize: 11, letterSpacing: 1.1, fontWeight: FontWeight.w700, color: const Color(0xFF005F52))),
              const SizedBox(height: 16),
              Card(
                margin: EdgeInsets.zero,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      DropdownButtonFormField<String>(
                        value: _role,
                        decoration: _decoration('Account role', Icons.badge_outlined),
                        items: const [
                          DropdownMenuItem(value: 'Admin', child: Text('Admin')),
                          DropdownMenuItem(value: 'Inspector', child: Text('Inspector')),
                          DropdownMenuItem(value: 'Consumer', child: Text('Consumer')),
                        ],
                        onChanged: (value) => setState(() => _role = value ?? 'Inspector'),
                      ),
                      const SizedBox(height: 12),
                      TextField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: _decoration('Email address', Icons.email_outlined)),
                      const SizedBox(height: 12),
                      if (!_otpRequested) ...[
                        TextField(controller: _password, obscureText: true, decoration: _decoration('Password', Icons.lock_outline)),
                        const SizedBox(height: 12),
                        ElevatedButton.icon(onPressed: _loading ? null : _passwordLogin, icon: const Icon(Icons.login), label: const Text('Sign in with password')),
                        const SizedBox(height: 8),
                        OutlinedButton.icon(onPressed: _loading ? null : _requestOtp, icon: const Icon(Icons.mark_email_read_outlined), label: const Text('Email me a SafetyBite-AI OTP')),
                      ] else ...[
                        TextField(controller: _otp, keyboardType: TextInputType.number, maxLength: 6, decoration: _decoration('6-digit email OTP', Icons.verified_user_outlined)),
                        if (_devOtp != null) Text('Local development OTP filled automatically', style: GoogleFonts.inter(fontSize: 11, color: Colors.orange.shade800)),
                        const SizedBox(height: 8),
                        ElevatedButton.icon(onPressed: _loading ? null : _verifyOtp, icon: const Icon(Icons.verified_outlined), label: Text(_loading ? 'Verifying...' : 'Verify and sign in')),
                        TextButton(onPressed: _loading ? null : _requestOtp, child: const Text('Send another OTP')),
                      ],
                      const Divider(height: 24),
                      TextButton.icon(onPressed: () => setState(() => _showKey = !_showKey), icon: const Icon(Icons.key_outlined), label: const Text('Admin inspector access key')),
                      if (_showKey) ...[
                        TextField(controller: _accessKey, obscureText: true, decoration: _decoration('Inspector access key', Icons.vpn_key_outlined)),
                        const SizedBox(height: 8),
                        OutlinedButton(onPressed: _loading ? null : _keyLogin, child: const Text('Use access key')),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text('SafetyBite-AI sends OTPs only when SMTP is configured on the backend.', textAlign: TextAlign.center, style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFF6B7280))),
            ],
          ),
        ),
      ),
    );
  }
}
