import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/live_verification_screen.dart';
import 'screens/scan_evaluation_screen.dart';
import 'screens/report_screen.dart';
import 'screens/inspection_log_screen.dart';
import 'screens/profile_screen.dart';
import 'features/reports/reports_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    ChangeNotifierProvider(
      create: (_) => AppState(),
      child: const LMSSentinelApp(),
    ),
  );
}

class AppState extends ChangeNotifier {
  int currentIndex = 0;
  String selectedInspectionStatus = 'All';
  String? selectedImagePath;
  dynamic lastScanResult;

  void setCurrentIndex(int index) {
    currentIndex = index;
    notifyListeners();
  }

  void setInspectionStatus(String status) {
    selectedInspectionStatus = status;
    notifyListeners();
  }

  void setSelectedImagePath(String? path) {
    selectedImagePath = path;
    notifyListeners();
  }

  void setLastScanResult(dynamic result) {
    lastScanResult = result;
    notifyListeners();
  }
}

class LMSSentinelApp extends StatelessWidget {
  const LMSSentinelApp({super.key});

  @override
  Widget build(BuildContext context) {
    final brandPrimary = const Color(0xFF005F52);
    final brandAccent = const Color(0xFFE8F5E9);
    final titleText = const Color(0xFF1B2533);
    final subtitleText = const Color(0xFF6B7280);
    final fieldText = const Color(0xFF374151);

    final theme = ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: const Color(0xFFF8FAF9),
      colorScheme: ColorScheme.fromSeed(
        seedColor: brandPrimary,
        primary: brandPrimary,
        secondary: brandAccent,
        surface: Colors.white,
      ),
      textTheme: GoogleFonts.interTextTheme().copyWith(
        headlineLarge: GoogleFonts.inter(
          fontWeight: FontWeight.w800,
          color: titleText,
        ),
        titleLarge: GoogleFonts.inter(
          fontWeight: FontWeight.w700,
          color: titleText,
        ),
        bodyLarge: GoogleFonts.inter(color: fieldText),
        bodyMedium: GoogleFonts.inter(color: subtitleText),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: const Color(0xFFF8FAF9),
        foregroundColor: titleText,
        elevation: 0,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0xFFE5E7EB)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0xFF005F52), width: 1.5),
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: Colors.white,
        indicatorColor: const Color(0xFFE8F5E9),
        labelTextStyle: WidgetStateProperty.all(
          GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.w600),
        ),
      ),
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'LMS-Sentinel',
      theme: theme,
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/dashboard': (context) => const DashboardScreen(),
        '/live-verification': (context) => const LiveVerificationScreen(),
        '/scan-evaluation': (context) => const ScanEvaluationScreen(),
        '/report': (context) => const VerificationReportScreen(),
        '/inspection-log': (context) => const InspectionLogScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/reports': (context) => const StatutoryReportsScreen(),
      },
    );
  }
}
