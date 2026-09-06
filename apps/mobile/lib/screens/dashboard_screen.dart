import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../widgets/status_badge.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final items = [
      {
        'title': 'Sunrise Gold Refined Oil',
        'meta': 'Sunrise Oils • 10 mins ago',
        'status': 'Violation',
        'color': const Color(0xFFE53935),
        'bg': const Color(0xFFFFEBEE),
      },
      {
        'title': 'Fortified Wheat Flour 5kg',
        'meta': 'Bharat Atta • 1 hour ago',
        'status': 'Compliant',
        'color': const Color(0xFF2E7D32),
        'bg': const Color(0xFFE8F5E9),
      },
      {
        'title': 'Amul Butter 500g',
        'meta': 'GCMMF • Yesterday',
        'status': 'Pending',
        'color': const Color(0xFFFB8C00),
        'bg': const Color(0xFFFFF3E0),
      },
    ];

    final counters = [
      {'label': 'Today', 'value': '3', 'color': const Color(0xFF005F52), 'bg': const Color(0xFFE8F5E9)},
      {'label': 'Pending', 'value': '7', 'color': const Color(0xFFFB8C00), 'bg': const Color(0xFFFFF3E0)},
      {'label': 'Violations', 'value': '12', 'color': const Color(0xFFE53935), 'bg': const Color(0xFFFFEBEE)},
    ];

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF9),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 8),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Namaste, R. Sharma',
                          style: GoogleFonts.inter(
                            fontSize: 28,
                            fontWeight: FontWeight.w800,
                            color: const Color(0xFF1B2533),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Legal Metrology Inspector — Zone 2',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                            color: const Color(0xFF6B7280),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF005F52), Color(0xFF0A7D6B)],
                      ),
                      borderRadius: BorderRadius.circular(15),
                    ),
                    child: const Center(
                      child: Text(
                        'RS',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 12,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: Row(
                  children: List.generate(counters.length, (index) {
                    final item = counters[index];
                    return Expanded(
                      child: Padding(
                        padding: EdgeInsets.only(right: index < counters.length - 1 ? 10 : 0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 18),
                          decoration: BoxDecoration(
                            color: item['bg'] as Color,
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: Column(
                            children: [
                              Text(
                                item['label'] as String,
                                style: GoogleFonts.inter(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: const Color(0xFF374151),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                item['value'] as String,
                                style: GoogleFonts.inter(
                                  fontSize: 28,
                                  fontWeight: FontWeight.w800,
                                  color: item['color'] as Color,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.pushNamed(context, '/live-verification');
                  },
                  icon: const Icon(Icons.camera_alt_rounded),
                  label: const Text('Start New Scan / Inspection'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF005F52),
                    foregroundColor: Colors.white,
                    minimumSize: const Size.fromHeight(58),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 18),
            Expanded(
              child: Container(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Recent Inspections',
                      style: GoogleFonts.inter(
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        color: const Color(0xFF1B2533),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Expanded(
                      child: ListView.separated(
                        itemCount: items.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 12),
                        itemBuilder: (context, index) {
                          final item = items[index];
                          return Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(20),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.04),
                                  blurRadius: 10,
                                  offset: const Offset(0, 6),
                                ),
                              ],
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 52,
                                  height: 52,
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF3F4F6),
                                    borderRadius: BorderRadius.circular(14),
                                  ),
                                  child: const Icon(Icons.qr_code_2_rounded, color: Color(0xFF005F52)),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item['title'] as String,
                                        style: GoogleFonts.inter(
                                          fontSize: 16,
                                          fontWeight: FontWeight.w700,
                                          color: const Color(0xFF1B2533),
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        item['meta'] as String,
                                        style: GoogleFonts.inter(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w500,
                                          color: const Color(0xFF6B7280),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                StatusBadge(
                                  label: item['status'] as String,
                                  color: item['color'] as Color,
                                  background: item['bg'] as Color,
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
            NavigationBar(
              selectedIndex: 0,
              onDestinationSelected: (value) {
                switch (value) {
                  case 0:
                    Navigator.pushReplacementNamed(context, '/dashboard');
                    break;
                  case 1:
                    Navigator.pushReplacementNamed(context, '/inspection-log');
                    break;
                  case 2:
                    Navigator.pushReplacementNamed(context, '/reports');
                    break;
                  case 3:
                    Navigator.pushReplacementNamed(context, '/profile');
                    break;
                }
              },
              destinations: const [
                NavigationDestination(icon: Icon(Icons.home_rounded), label: 'Home'),
                NavigationDestination(icon: Icon(Icons.article_outlined), label: 'Inspections'),
                NavigationDestination(icon: Icon(Icons.bar_chart_rounded), label: 'Reports'),
                NavigationDestination(icon: Icon(Icons.person_rounded), label: 'Profile'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
