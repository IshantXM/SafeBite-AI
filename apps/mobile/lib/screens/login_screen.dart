import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:google_fonts/google_fonts.dart';

import '../widgets/app_logo.dart';
import '../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _obscurePassword = true;
  bool _isSigningIn = false;
  final _usernameController = TextEditingController(text: 'inspector_sharma');
  final _passwordController = TextEditingController(text: 'inspector');

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    if (_usernameController.text.trim().isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter username and password')));
      return;
    }
    setState(() => _isSigningIn = true);
    final success = await ApiService.login(
      username: _usernameController.text.trim(),
      password: _passwordController.text,
    );
    if (!mounted) return;
    setState(() => _isSigningIn = false);
    if (success) {
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Sign in failed. Check that the backend is running.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF9),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: ConstrainedBox(
                constraints: BoxConstraints(minHeight: constraints.maxHeight),
                child: IntrinsicHeight(
                  child: Column(
                    children: [
                      const SizedBox(height: 30),
                      const AppLogo(size: 104),
                      const SizedBox(height: 22),
                      Text(
                        'SafetyBite-AI',
                        style: GoogleFonts.inter(
                          fontSize: 32,
                          fontWeight: FontWeight.w800,
                          color: const Color(0xFF1B2533),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'AI COMPLIANCE PLATFORM',
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.3,
                          color: const Color(0xFF005F52),
                        ),
                      ),
                      const SizedBox(height: 14),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        child: Text(
                          'AI-Powered Legal Metrology Compliance verification for field inspectors',
                          textAlign: TextAlign.center,
                          style: GoogleFonts.inter(
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            color: const Color(0xFF6B7280),
                            height: 1.5,
                          ),
                        ),
                      ),
                      const SizedBox(height: 28),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(18),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 16,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            TextField(
                              controller: _usernameController,
                              decoration: InputDecoration(
                                hintText: 'Inspector ID / Email',
                                prefixIcon: const Icon(Icons.person_outline_rounded, color: Color(0xFF005F52)),
                              ),
                            ),
                            const SizedBox(height: 18),
                            TextField(
                              obscureText: _obscurePassword,
                              controller: _passwordController,
                              decoration: InputDecoration(
                                hintText: 'Password',
                                prefixIcon: const Icon(Icons.lock_outline_rounded, color: Color(0xFF005F52)),
                                suffixIcon: IconButton(
                                  onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                  icon: Icon(
                                    _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                    color: const Color(0xFF6B7280),
                                  ),
                                ),
                              ),
                            ),
                            Align(
                              alignment: Alignment.centerRight,
                              child: TextButton(
                                onPressed: () {},
                                style: TextButton.styleFrom(
                                  foregroundColor: const Color(0xFF005F52),
                                ),
                                child: const Text('Forgot Password?'),
                              ),
                            ),
                            const SizedBox(height: 8),
                            SizedBox(
                              width: double.infinity,
                              child: ElevatedButton(
                                onPressed: _isSigningIn ? null : _signIn,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF005F52),
                                  foregroundColor: Colors.white,
                                  minimumSize: const Size.fromHeight(56),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(18),
                                  ),
                                  elevation: 0,
                                ),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    if (_isSigningIn)
                                      const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                    else
                                      Text(
                                      'Sign in',
                                      style: GoogleFonts.inter(
                                        fontSize: 16,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                    if (!_isSigningIn) ...[
                                      const SizedBox(width: 8),
                                      const Icon(Icons.arrow_forward_rounded),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 26),
                        child: Column(
                          children: [
                            Container(
                              width: 56,
                              height: 56,
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFFE8F5E9),
                                borderRadius: BorderRadius.circular(18),
                                border: Border.all(color: const Color(0xFFB2DFDB)),
                              ),
                              child: SvgPicture.string(
                                '''
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
                                  <path d="M32 8c6 0 11 5 11 11v4h-3v-4a8 8 0 1 0-16 0v4h-3v-4c0-6 5-11 11-11Zm-16 18h32a4 4 0 0 1 4 4v18a4 4 0 0 1-4 4H16a4 4 0 0 1-4-4V30a4 4 0 0 1 4-4Zm6 8h20v8H22zm0 12h14v4H22z" fill="#005F52"/>
                                </svg>
                                ''',
                                width: 32,
                                height: 32,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              'MINISTRY OF CONSUMER AFFAIRS',
                              textAlign: TextAlign.center,
                              style: GoogleFonts.inter(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.8,
                                color: const Color(0xFF005F52),
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Department of Consumer Affairs, Government of India',
                              textAlign: TextAlign.center,
                              style: GoogleFonts.inter(
                                fontSize: 11,
                                fontWeight: FontWeight.w500,
                                color: const Color(0xFF6B7280),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
